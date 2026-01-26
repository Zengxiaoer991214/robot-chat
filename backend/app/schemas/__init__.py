"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ===== User Schemas =====
class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=1, max_length=50)


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== Agent Schemas =====
class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    provider: str = Field(..., min_length=1, max_length=50)
    model_name: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = Field(..., min_length=1)
    api_key_config: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class AgentCreate(AgentBase):
    """Schema for creating an agent."""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an agent."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=50)
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    system_prompt: Optional[str] = Field(None, min_length=1)
    api_key_config: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)


class AgentResponse(AgentBase):
    """Schema for agent response."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# ===== Room Schemas =====
class RoomBase(BaseModel):
    """Base room schema."""
    name: str = Field(..., min_length=1, max_length=100)
    topic: str = Field(..., min_length=1)
    max_rounds: int = Field(default=20, ge=1, le=1000)


class RoomCreate(RoomBase):
    """Schema for creating a room."""
    creator_id: Optional[int] = None
    agent_ids: List[int] = Field(default_factory=list, min_length=0)


class RoomResponse(RoomBase):
    """Schema for room response."""
    id: int
    current_rounds: int
    status: str
    creator_id: Optional[int]
    created_at: datetime
    agents: List[AgentResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class RoomJoin(BaseModel):
    """Schema for joining agents to a room."""
    agent_id: int


# ===== Message Schemas =====
class MessageBase(BaseModel):
    """Base message schema."""
    content: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(user|assistant|system)$")


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    room_id: int
    agent_id: Optional[int] = None


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: int
    room_id: int
    agent_id: Optional[int]
    created_at: datetime
    agent: Optional[AgentResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== WebSocket Schemas =====
class WSMessage(BaseModel):
    """WebSocket message schema."""
    type: str  # message, status, error
    data: dict
