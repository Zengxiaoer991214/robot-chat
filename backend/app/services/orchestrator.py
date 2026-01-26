"""
Chat Orchestrator Engine - manages AI group conversations.
"""
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Room, Agent, Message
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
            
            # Check if room has agents
            if not room.agents:
                raise ValueError("Room has no agents")
            
            # Set room status to running
            room.status = "running"
            self.db.commit()
            logger.info(f"Starting conversation for room {self.room_id}")
            
            # Send system message announcing the topic
            await self._send_system_message(
                settings.conversation_start_template.format(topic=room.topic),
                websocket_broadcast_callback
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
                
                # Select next agent (round-robin)
                agent = self._select_next_agent(room.agents)
                if not agent:
                    logger.error(f"No agent selected for room {self.room_id}")
                    break
                
                try:
                    # Generate response
                    response = await self._generate_agent_response(agent, room)
                    
                    # Save message
                    message = await self._save_message(
                        room_id=room.id,
                        agent_id=agent.id,
                        content=response,
                        role="assistant"
                    )
                    
                    # Broadcast via WebSocket
                    if websocket_broadcast_callback:
                        await websocket_broadcast_callback(room.id, {
                            "type": "message",
                            "data": {
                                "id": message.id,
                                "agent_id": agent.id,
                                "agent_name": agent.name,
                                "content": response,
                                "created_at": message.created_at.isoformat()
                            }
                        })
                    
                    # Increment round count
                    room.current_rounds += 1
                    self.db.commit()
                    
                    logger.info(f"Room {self.room_id}: Agent {agent.name} spoke (round {room.current_rounds}/{room.max_rounds})")
                    
                    # Sleep to avoid rapid-fire messages
                    await asyncio.sleep(settings.default_sleep_between_messages)
                    
                except Exception as e:
                    logger.error(f"Error generating response for agent {agent.id}: {str(e)}")
                    # Continue to next agent instead of stopping the conversation
                    continue
            
            # Mark room as finished
            room.status = "finished"
            self.db.commit()
            logger.info(f"Conversation finished for room {self.room_id}")
            
            # Send completion message
            await self._send_system_message(
                settings.conversation_end_template,
                websocket_broadcast_callback
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
    
    def _select_next_agent(self, agents: List[Agent]) -> Optional[Agent]:
        """
        Select the next agent to speak using round-robin strategy.
        
        Args:
            agents: List of agents in the room
            
        Returns:
            Selected agent or None if no agents available
        """
        if not agents:
            return None
        
        agent = agents[self.current_agent_index % len(agents)]
        self.current_agent_index += 1
        return agent
    
    async def _generate_agent_response(self, agent: Agent, room: Room) -> str:
        """
        Generate a response from the given agent.
        
        Args:
            agent: Agent to generate response from
            room: Current room
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If generation fails
        """
        # Get recent messages for context
        messages = self._get_recent_messages(room.id)
        
        # Convert to format expected by LLM
        llm_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Get LLM adapter
        adapter = get_llm_adapter(
            provider=agent.provider,
            model_name=agent.model_name,
            temperature=agent.temperature,
            api_key=agent.api_key_config
        )
        
        # Generate response
        response = await adapter.generate(llm_messages, agent.system_prompt)
        
        return response
    
    def _get_recent_messages(self, room_id: int) -> List[Message]:
        """
        Get recent messages from the room for context.
        
        Args:
            room_id: Room ID
            
        Returns:
            List of recent messages (limited by max_context_messages)
        """
        messages = (
            self.db.query(Message)
            .filter(Message.room_id == room_id)
            .order_by(desc(Message.created_at))
            .limit(settings.max_context_messages)
            .all()
        )
        # Reverse to chronological order
        return list(reversed(messages))
    
    async def _save_message(self, room_id: int, agent_id: Optional[int], content: str, role: str) -> Message:
        """
        Save a message to the database.
        
        Args:
            room_id: Room ID
            agent_id: Agent ID (None for system messages)
            content: Message content
            role: Message role (user, assistant, system)
            
        Returns:
            Created message object
        """
        message = Message(
            room_id=room_id,
            agent_id=agent_id,
            content=content,
            role=role,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    async def _send_system_message(self, content: str, websocket_broadcast_callback=None):
        """
        Send a system message.
        
        Args:
            content: Message content
            websocket_broadcast_callback: Optional callback for WebSocket broadcast
        """
        message = await self._save_message(
            room_id=self.room_id,
            agent_id=None,
            content=content,
            role="system"
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
