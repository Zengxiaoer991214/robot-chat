"""
SQLAlchemy database models for the AI Group Chat system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


# Association table for many-to-many relationship between rooms and roles
room_roles = Table(
    'room_roles',
    Base.metadata,
    Column('room_id', Integer, ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """User model representing system users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    rooms = relationship("Room", back_populates="creator")
    agents = relationship("Agent", back_populates="creator")
    roles = relationship("Role", back_populates="creator")


class Agent(Base):
    """AI Agent configuration model."""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    provider = Column(String(50), nullable=False)  # openai, deepseek, ollama, etc.
    model_name = Column(String(100), nullable=False)  # gpt-4, llama3, etc.
    system_prompt = Column(Text, nullable=False)
    api_key_config = Column(Text, nullable=True)  # Encrypted or specific key
    temperature = Column(Float, default=0.7, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="agents")
    messages = relationship("Message", back_populates="agent")
    roles = relationship("Role", back_populates="agent", cascade="all, delete-orphan")


class Room(Base):
    """Chat room model."""
    
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    topic = Column(Text, nullable=False)
    max_rounds = Column(Integer, default=20, nullable=False)
    current_rounds = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default='idle', nullable=False)  # idle, running, finished
    mode = Column(String(20), default='debate', nullable=False)  # debate, group_chat
    session_id = Column(Integer, default=0, nullable=False)  # For managing conversation restarts
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="rooms")
    roles = relationship("Role", secondary=room_roles, back_populates="rooms")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class Message(Base):
    """Message model for chat records."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True)  # NULL for system messages
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    session_id = Column(Integer, default=0, nullable=False)  # Linked to room session
    sender_name = Column(String(100), nullable=True)  # Name of the sender (Agent or Role name)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    room = relationship("Room", back_populates="messages")
    agent = relationship("Agent", back_populates="messages")
    sender_role = relationship("Role", back_populates="messages")


class Role(Base):
    """Role model for agent personas."""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=True)
    age = Column(String(20), nullable=True)
    profession = Column(String(100), nullable=True)
    personality = Column(Text, nullable=True)
    aggressiveness = Column(Integer, default=5, nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="roles")
    agent = relationship("Agent", back_populates="roles")
    rooms = relationship("Room", secondary=room_roles, back_populates="roles")
    messages = relationship("Message", back_populates="sender_role")


class ChatSession(Base):
    """Chat session model for direct playground chats."""
    
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = relationship("ChatSessionMessage", back_populates="session", cascade="all, delete-orphan")
    agent = relationship("Agent")
    role = relationship("Role")


class ChatSessionMessage(Base):
    """Message model for chat sessions."""
    
    __tablename__ = "chat_session_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)  # Base64 data or URL
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
