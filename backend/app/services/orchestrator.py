"""
Chat Orchestrator Engine - manages AI group conversations.
"""
import asyncio
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Room, Agent, Message, Role
from app.services.llm_adapter import get_llm_adapter
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """
    Orchestrates multi-agent conversations in a chat room.
    Manages turn-taking, message generation, and conversation flow.
    """
    
    def __init__(self, room_id: int, db: Session):
        """
        Initialize the orchestrator.
        
        Args:
            room_id: ID of the room to orchestrate
            db: Database session
        """
        self.room_id = room_id
        self.db = db
        self.current_agent_index = 0
        self._stop_requested = False
    
    def stop(self):
        """Request the orchestrator to stop."""
        logger.info(f"Stop requested for room {self.room_id}")
        self._stop_requested = True
    
    async def start_conversation(self, websocket_broadcast_callback=None):
        """
        Start the autonomous conversation loop.
        
        Args:
            websocket_broadcast_callback: Optional callback function to broadcast messages
                                         Should accept (room_id, message_dict) as parameters
        
        Raises:
            ValueError: If room not found or invalid state
            Exception: If conversation fails
        """
        try:
            # Load room and validate
            room = self.db.query(Room).filter(Room.id == self.room_id).first()
            if not room:
                raise ValueError(f"Room {self.room_id} not found")
            
            if room.status == "finished":
                raise ValueError("Room conversation already finished")
            
            # Check if room has roles
            if not room.roles:
                raise ValueError("Room has no roles")
            participants = room.roles
            
            # Set room status to running
            room.status = "running"
            self.db.commit()
            logger.info(f"Starting conversation for room {self.room_id} (Mode: {room.mode})")
            
            # Send system message announcing the topic
            if room.mode == 'group_chat':
                start_msg = f"Welcome to the group chat! Topic: {room.topic}. Everyone, please introduce yourselves briefly."
            else:
                start_msg = settings.conversation_start_template.format(topic=room.topic)
                
            await self._send_system_message(
                start_msg,
                websocket_broadcast_callback,
                session_id=room.session_id
            )
            
            # Main conversation loop
            while not self._stop_requested:
                # Refresh room state
                self.db.refresh(room)
                
                # Check if max rounds reached
                if room.current_rounds >= room.max_rounds:
                    logger.info(f"Room {self.room_id} reached max rounds ({room.max_rounds})")
                    break
                
                # Check if status changed
                if room.status != "running":
                    logger.info(f"Room {self.room_id} status changed to {room.status}")
                    break
                
                # Select next participant (round-robin)
                participant = self._select_next_participant(participants)
                if not participant:
                    logger.error(f"No participant selected for room {self.room_id}")
                    break
                
                try:
                    # Generate response
                    response = await self._generate_response(participant, room)
                    
                    # Determine agent_id, role_id and sender_name
                    agent_id = None
                    role_id = None
                    sender_name = "Unknown"
                    
                    if isinstance(participant, Agent):
                        agent_id = participant.id
                        sender_name = participant.name
                    elif isinstance(participant, Role):
                        agent_id = participant.agent_id
                        role_id = participant.id
                        sender_name = participant.name
                    
                    # Save message
                    message = await self._save_message(
                        room_id=room.id,
                        agent_id=agent_id,
                        role_id=role_id,
                        content=response,
                        role="assistant",
                        session_id=room.session_id,
                        sender_name=sender_name
                    )
                    
                    # Broadcast via WebSocket
                    if websocket_broadcast_callback:
                        await websocket_broadcast_callback(room.id, {
                            "type": "message",
                            "data": {
                                "id": message.id,
                                "agent_id": agent_id,
                                "role_id": role_id,
                                "agent_name": sender_name,
                                "content": response,
                                "created_at": message.created_at.isoformat()
                            }
                        })
                    
                    # Increment round count
                    room.current_rounds += 1
                    self.db.commit()
                    
                    logger.info(f"Room {self.room_id}: {sender_name} spoke (round {room.current_rounds}/{room.max_rounds})")
                    
                    # Sleep to avoid rapid-fire messages
                    await asyncio.sleep(settings.default_sleep_between_messages)
                    
                except Exception as e:
                    logger.error(f"Error generating response for participant: {str(e)}")
                    # Continue to next participant instead of stopping the conversation
                    continue
            
            # Mark room as finished
            room.status = "finished"
            self.db.commit()
            logger.info(f"Conversation finished for room {self.room_id}")
            
            # Send completion message
            await self._send_system_message(
                settings.conversation_end_template,
                websocket_broadcast_callback,
                session_id=room.session_id
            )
            
        except Exception as e:
            logger.error(f"Error in conversation orchestration: {str(e)}")
            # Update room status to idle on error
            try:
                room = self.db.query(Room).filter(Room.id == self.room_id).first()
                if room:
                    room.status = "idle"
                    self.db.commit()
            except Exception:
                pass
            raise
    
    def _select_next_participant(self, participants: List[Union[Agent, Role]]) -> Optional[Union[Agent, Role]]:
        """
        Select the next participant to speak using round-robin strategy.
        
        Args:
            participants: List of agents or roles in the room
            
        Returns:
            Selected participant or None if no participants available
        """
        if not participants:
            return None
        
        participant = participants[self.current_agent_index % len(participants)]
        self.current_agent_index += 1
        return participant
    
    async def _generate_response(self, participant: Union[Agent, Role], room: Room) -> str:
        """
        Generate a response from the given participant.
        
        Args:
            participant: Agent or Role to generate response from
            room: Current room
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If generation fails
        """
        # Get recent messages for context
        messages = self._get_recent_messages(room)
        
        # Convert to format expected by LLM
        llm_messages = []
        for msg in messages:
            content = msg.content
            if msg.sender_name:
                content = f"{msg.sender_name}: {msg.content}"
            llm_messages.append({"role": msg.role, "content": content})
        
        # Determine configuration
        if isinstance(participant, Role):
            agent = participant.agent
            # Construct role-based system prompt
            system_prompt = (
                f"You are playing the role of {participant.name}. "
                f"Gender: {participant.gender or 'Not specified'}. "
                f"Age: {participant.age or 'Not specified'}. "
                f"Profession: {participant.profession or 'Not specified'}. "
                f"Personality: {participant.personality or 'Not specified'}. "
                f"Aggressiveness Level (1-10): {participant.aggressiveness}. "
                f"You are in a group chat. The topic is: {room.topic}. "
                "Your responses must be SHORT, CONCISE, and mimic casual human group chat behavior. "
                "Do not write long paragraphs. Do not use formal language unless your character fits it. "
                "Maximum 30 words per message. "
                "React to other people's messages based on your personality."
            )
        else:
            # Fallback for unexpected types, though we expect only Roles
            raise ValueError(f"Invalid participant type: {type(participant)}")

        # Get LLM adapter
        adapter = get_llm_adapter(
            provider=agent.provider,
            model_name=agent.model_name,
            temperature=agent.temperature,
            api_key=agent.api_key_config
        )
        
        # Generate response
        response = await adapter.generate(llm_messages, system_prompt)
        
        return response
    
    def _get_recent_messages(self, room: Room) -> List[Message]:
        """
        Get recent messages from the room for context.
        
        Args:
            room: Room object
            
        Returns:
            List of recent messages (limited by max_context_messages)
        """
        messages = (
            self.db.query(Message)
            .filter(Message.room_id == room.id)
            .filter(Message.session_id == room.session_id)
            .order_by(desc(Message.created_at))
            .limit(settings.max_context_messages)
            .all()
        )
        # Reverse to chronological order
        return list(reversed(messages))
    
    async def _save_message(self, room_id: int, agent_id: Optional[int], role_id: Optional[int], content: str, role: str, session_id: int = 0, sender_name: Optional[str] = None) -> Message:
        """
        Save a message to the database.
        
        Args:
            room_id: Room ID
            agent_id: Agent ID (None for system messages)
            role_id: Role ID (None for system messages)
            content: Message content
            role: Message role (user, assistant, system)
            session_id: Session ID for conversation restarts
            sender_name: Name of the sender
            
        Returns:
            Created message object
        """
        message = Message(
            room_id=room_id,
            agent_id=agent_id,
            role_id=role_id,
            content=content,
            role=role,
            session_id=session_id,
            sender_name=sender_name,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    async def _send_system_message(self, content: str, websocket_broadcast_callback=None, session_id: int = 0):
        """
        Send a system message.
        
        Args:
            content: Message content
            websocket_broadcast_callback: Optional callback for WebSocket broadcast
            session_id: Session ID
        """
        message = await self._save_message(
            room_id=self.room_id,
            agent_id=None,
            content=content,
            role="system",
            session_id=session_id
        )
        
        if websocket_broadcast_callback:
            await websocket_broadcast_callback(self.room_id, {
                "type": "message",
                "data": {
                    "id": message.id,
                    "agent_id": None,
                    "agent_name": "System",
                    "content": content,
                    "created_at": message.created_at.isoformat()
                }
            })
