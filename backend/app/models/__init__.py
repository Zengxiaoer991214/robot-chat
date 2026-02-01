"""
SQLAlchemy database models for the AI Group Chat system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Table, DateTime
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    rooms = relationship("Room", back_populates="creator")


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
    
    # Relationships
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
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="roles")
    rooms = relationship("Room", secondary=room_roles, back_populates="roles")
    messages = relationship("Message", back_populates="sender_role")
