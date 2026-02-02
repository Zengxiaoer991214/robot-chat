"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ===== User Schemas =====
class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== Token Schemas =====
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None



# ===== Agent Schemas =====
class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    provider: str = Field(..., min_length=1, max_length=50)
    model_name: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = Field(default="", description="System prompt for the agent")
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
    system_prompt: Optional[str] = Field(None)
    api_key_config: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)


class AgentResponse(AgentBase):
    """Schema for agent response."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# ===== Role Schemas =====
class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., min_length=1, max_length=100)
    gender: Optional[str] = None
    age: Optional[str] = None
    profession: Optional[str] = None
    personality: Optional[str] = None
    aggressiveness: int = Field(default=5, ge=1, le=10)
    agent_id: int


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[str] = None
    age: Optional[str] = None
    profession: Optional[str] = None
    personality: Optional[str] = None
    aggressiveness: Optional[int] = Field(None, ge=1, le=10)
    agent_id: Optional[int] = None



class RoleResponse(RoleBase):
    """Schema for role response."""
    id: int
    created_at: datetime
    agent: Optional[AgentResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== Room Schemas =====
class RoomBase(BaseModel):
    """Base room schema."""
    name: str = Field(..., min_length=1, max_length=100)
    topic: str = Field(..., min_length=1)
    max_rounds: int = Field(default=20, ge=1, le=100)
    mode: str = Field(default='debate')  # debate, group_chat


class RoomCreate(RoomBase):
    """Schema for creating a room."""
    role_ids: List[int] = Field(..., min_items=2)


class RoomResponse(RoomBase):
    """Schema for room response."""
    id: int
    status: str
    current_rounds: int
    created_at: datetime
    roles: List[RoleResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class RoomJoin(BaseModel):
    """Schema for joining a room."""
    role_id: Optional[int] = None  # If joining as a specific role (human takeover)


# ===== Message Schemas =====
class MessageBase(BaseModel):
    """Base message schema."""
    content: str
    role: str  # user, assistant, system


class UserMessageRequest(BaseModel):
    """Schema for user sending a message."""
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    room_id: int
    agent_id: Optional[int] = None
    role_id: Optional[int] = None


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: int
    room_id: int
    agent_id: Optional[int] = None
    sender_name: Optional[str] = None
    role_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== Chat Session Schemas =====
class ChatSessionMessageBase(BaseModel):
    role: str
    content: str
    image_url: Optional[str] = None


class ChatSessionMessageCreate(ChatSessionMessageBase):
    pass


class ChatSessionMessageResponse(ChatSessionMessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChatSessionBase(BaseModel):
    agent_id: int
    role_id: Optional[int] = None
    title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # messages: List[ChatSessionMessageResponse] = []  # Typically loaded separately
    
    model_config = ConfigDict(from_attributes=True)


# ===== Chat Schemas =====
class ChatRequest(BaseModel):
    """Schema for direct chat request."""
    agent_id: int
    role_id: Optional[int] = None
    session_id: Optional[int] = None
    message: str
    image: Optional[str] = None  # Base64 string
    history: List[Dict[str, str]] = []  # [{"role": "user", "content": "hi"}, ...]
    stream: bool = False


class ChatCompletionResponse(BaseModel):
    """Schema for direct chat response."""
    content: str
