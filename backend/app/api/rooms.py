"""
API endpoints for room management.
"""
import logging
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Room, Agent, Role, User
from app.schemas import RoomCreate, RoomResponse, RoomJoin, MessageResponse, UserMessageRequest
from app.services.orchestrator import ChatOrchestrator
from app.api.websocket import manager
from app.api.deps import get_current_user
from app.models import Room, Agent, Role, User, Message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rooms", tags=["rooms"])

# Store active orchestrators
active_orchestrators = {}


@router.post("/{room_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    room_id: int, 
    message_data: UserMessageRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Send a user message to the room.
    """
    try:
        # Validate room
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
            
        # Create message
        message = Message(
            room_id=room_id,
            content=message_data.content,
            role="user",
            session_id=room.session_id,
            sender_name=current_user.username
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Broadcast to WebSocket
        # Construct message dict for broadcast
        msg_dict = {
            "type": "message",
            "data": {
                "id": message.id,
                "room_id": message.room_id,
                "content": message.content,
                "role": "user",
                "sender_name": message.sender_name,
                "created_at": message.created_at.isoformat()
            }
        }
        
        await manager.broadcast(room_id, msg_dict)
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message to room {room_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(room_data: RoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new chat room.
    
    Args:
        room_data: Room creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created room
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate role IDs if provided
        roles = []
        if room_data.role_ids:
            # Check roles exist and belong to user
            roles = db.query(Role).filter(Role.id.in_(room_data.role_ids), Role.user_id == current_user.id).all()
            if len(roles) != len(room_data.role_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more role IDs are invalid or access denied"
                )

        # Create room
        room_dict = room_data.model_dump(exclude={"role_ids"})
        room = Room(**room_dict, creator_id=current_user.id)
        room.roles = roles
        
        db.add(room)
        db.commit()
        db.refresh(room)
        
        logger.info(f"Created room: {room.name} (ID: {room.id}) for user {current_user.username}")
        return room
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create room: {str(e)}"
        )


@router.get("", response_model=List[RoomResponse])
async def get_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all rooms for current user.
    """
    try:
        rooms = db.query(Room).filter(Room.creator_id == current_user.id).order_by(Room.created_at.desc()).offset(skip).limit(limit).all()
        return rooms
    except Exception as e:
        logger.error(f"Error fetching rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch rooms: {str(e)}"
        )


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a specific room by ID.
    """
    try:
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch room: {str(e)}"
        )


@router.post("/{room_id}/join", response_model=RoomResponse)
async def join_room(room_id: int, join_data: RoomJoin, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Add a role to a room.
    """
    try:
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        role = db.query(Role).filter(Role.id == join_data.role_id, Role.user_id == current_user.id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {join_data.role_id} not found or access denied"
            )
        
        # Check if role already in room
        if role in room.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {join_data.role_id} already in room"
            )
        
        # Add role to room
        room.roles.append(role)
        db.commit()
        db.refresh(room)
        
        logger.info(f"Role {role.name} joined room {room.name}")
        return room
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining room {room_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join room: {str(e)}"
        )


@router.post("/{room_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_room(room_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Start the autonomous conversation in a room.
    """
    try:
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        if room.status == "running":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room conversation already running"
            )
        
        if not room.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room has no roles"
            )
        
        # Create orchestrator
        orchestrator = ChatOrchestrator(room_id)
        active_orchestrators[room_id] = orchestrator
        
        # Start conversation in background
        background_tasks.add_task(orchestrator.start_conversation, manager.broadcast)
        
        logger.info(f"Started conversation for room {room_id}")
        return {"message": "Conversation started", "room_id": room_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start room: {str(e)}"
        )


@router.post("/{room_id}/stop", status_code=status.HTTP_200_OK)
async def stop_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Stop the conversation in a room.
    """
    try:
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        # Stop orchestrator if running
        if room_id in active_orchestrators:
            active_orchestrators[room_id].stop()
            del active_orchestrators[room_id]
        
        # Update room status
        room.status = "idle"
        db.commit()
        
        logger.info(f"Stopped conversation for room {room_id}")
        return {"message": "Conversation stopped", "room_id": room_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping room {room_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop room: {str(e)}"
        )


@router.post("/{room_id}/finish", status_code=status.HTTP_200_OK)
async def finish_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Terminate the conversation in a room (mark as finished).
    """
    try:
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        # Stop orchestrator if running
        if room_id in active_orchestrators:
            active_orchestrators[room_id].stop()
            del active_orchestrators[room_id]
        
        # Update room status
        room.status = "finished"
        db.commit()
        
        logger.info(f"Terminated conversation for room {room_id}")
        return {"message": "Conversation terminated", "room_id": room_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminating room {room_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate room: {str(e)}"
        )


@router.post("/{room_id}/restart", status_code=status.HTTP_200_OK)
async def restart_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Restart the conversation in a room (new session).
    """
    try:
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
            
        # Stop orchestrator if running
        if room_id in active_orchestrators:
            active_orchestrators[room_id].stop()
            del active_orchestrators[room_id]
            
        # Update room state for new session
        room.status = "idle"
        room.current_rounds = 0
        room.session_id += 1
        db.commit()
        
        logger.info(f"Restarted room {room_id} (New Session ID: {room.session_id})")
        return {"message": "Conversation restarted", "room_id": room_id, "session_id": room.session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting room {room_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart room: {str(e)}"
        )


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a chat room.
    """
    try:
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
            
        # Stop orchestrator if running
        if room_id in active_orchestrators:
            active_orchestrators[room_id].stop()
            del active_orchestrators[room_id]
            
        db.delete(room)
        db.commit()
        
        logger.info(f"Deleted room {room_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting room {room_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete room: {str(e)}"
        )


@router.get("/{room_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    room_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    session_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get messages from a room.
    """
    try:
        from app.models import Message
        
        room = db.query(Room).filter(Room.id == room_id, Room.creator_id == current_user.id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        query = db.query(Message).filter(Message.room_id == room_id)
        
        if session_id is not None:
            query = query.filter(Message.session_id == session_id)
            
        messages = (
            query
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching messages for room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch messages: {str(e)}"
        )
