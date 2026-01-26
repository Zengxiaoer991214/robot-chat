"""
WebSocket endpoint for real-time messaging.
"""
import logging
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Room

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for rooms."""
    
    def __init__(self):
        # room_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: int):
        """Connect a client to a room."""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        logger.info(f"Client connected to room {room_id}")
    
    def disconnect(self, websocket: WebSocket, room_id: int):
        """Disconnect a client from a room."""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        logger.info(f"Client disconnected from room {room_id}")
    
    async def broadcast(self, room_id: int, message: dict):
        """Broadcast a message to all clients in a room."""
        if room_id not in self.active_connections:
            return
        
        # Convert message to JSON
        message_json = json.dumps(message)
        
        # Send to all connected clients
        disconnected = []
        for websocket in self.active_connections[room_id]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket, room_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    """
    WebSocket endpoint for real-time room updates.
    
    Args:
        websocket: WebSocket connection
        room_id: Room ID to connect to
    """
    # Note: Can't use Depends(get_db) directly in WebSocket endpoints
    # We'll validate the room exists before accepting the connection
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Validate room exists
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            await websocket.close(code=4004, reason="Room not found")
            return
        
        # Accept connection
        await manager.connect(websocket, room_id)
        
        try:
            # Keep connection alive and listen for client messages
            while True:
                data = await websocket.receive_text()
                # Echo back for now (can add client message handling later)
                logger.info(f"Received from client in room {room_id}: {data}")
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, room_id)
            logger.info(f"WebSocket disconnected from room {room_id}")
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket, room_id)
    finally:
        db.close()


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager
