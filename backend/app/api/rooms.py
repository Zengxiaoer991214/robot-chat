"""
API endpoints for room management.
"""
import logging
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Room, Agent
from app.schemas import RoomCreate, RoomResponse, RoomJoin, MessageResponse
from app.services.orchestrator import ChatOrchestrator
from app.api.websocket import manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rooms", tags=["rooms"])

# Store active orchestrators
active_orchestrators = {}


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(room_data: RoomCreate, db: Session = Depends(get_db)):
    """
    Create a new chat room.
    
    Args:
        room_data: Room creation data
        db: Database session
        
    Returns:
        Created room
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate role IDs if provided
        roles = []
        if room_data.role_ids:
            roles = db.query(Role).filter(Role.id.in_(room_data.role_ids)).all()
            if len(roles) != len(room_data.role_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more role IDs are invalid"
                )

        # Create room
        room_dict = room_data.model_dump(exclude={"role_ids"})
        room = Room(**room_dict)
        room.roles = roles
        
        db.add(room)
        db.commit()
        db.refresh(room)
        
        logger.info(f"Created room: {room.name} (ID: {room.id})")
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
async def get_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all rooms.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of rooms
    """
    try:
        rooms = db.query(Room).offset(skip).limit(limit).all()
        return rooms
    except Exception as e:
        logger.error(f"Error fetching rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch rooms: {str(e)}"
        )


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    Get a specific room by ID.
    
    Args:
        room_id: Room ID
        db: Database session
        
    Returns:
        Room details
        
    Raises:
        HTTPException: If room not found
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
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
async def join_room(room_id: int, join_data: RoomJoin, db: Session = Depends(get_db)):
    """
    Add a role to a room.
    
    Args:
        room_id: Room ID
        join_data: Role join data
        db: Database session
        
    Returns:
        Updated room
        
    Raises:
        HTTPException: If room or role not found
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        role = db.query(Role).filter(Role.id == join_data.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {join_data.role_id} not found"
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
async def start_room(room_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Start the autonomous conversation in a room.
    
    Args:
        room_id: Room ID
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If room not found or already running
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
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
        orchestrator = ChatOrchestrator(room_id, db)
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
async def stop_room(room_id: int, db: Session = Depends(get_db)):
    """
    Stop the conversation in a room.
    
    Args:
        room_id: Room ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If room not found
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
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


@router.post("/{room_id}/restart", status_code=status.HTTP_200_OK)
async def restart_room(room_id: int, db: Session = Depends(get_db)):
    """
    Restart the conversation in a room (new session).
    
    Args:
        room_id: Room ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
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
async def delete_room(room_id: int, db: Session = Depends(get_db)):
    """
    Delete a chat room.
    
    Args:
        room_id: Room ID
        db: Database session
    """
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
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
    db: Session = Depends(get_db)
):
    """
    Get messages from a room.
    
    Args:
        room_id: Room ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        session_id: Optional session ID filter
        db: Database session
        
    Returns:
        List of messages
        
    Raises:
        HTTPException: If room not found
    """
    try:
        from app.models import Message
        
        room = db.query(Room).filter(Room.id == room_id).first()
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
