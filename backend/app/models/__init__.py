"""
SQLAlchemy database models for the AI Group Chat system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


# Association table for many-to-many relationship between rooms and agents
room_agents = Table(
    'room_agents',
    Base.metadata,
    Column('room_id', Integer, ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id', ondelete='CASCADE'), primary_key=True)
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
    rooms = relationship("Room", secondary=room_agents, back_populates="agents")
    messages = relationship("Message", back_populates="agent")


class Room(Base):
    """Chat room model."""
    
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    topic = Column(Text, nullable=False)
    max_rounds = Column(Integer, default=20, nullable=False)
    current_rounds = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default='idle', nullable=False)  # idle, running, finished
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="rooms")
    agents = relationship("Agent", secondary=room_agents, back_populates="rooms")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class Message(Base):
    """Message model for chat records."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True)  # NULL for system messages
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    room = relationship("Room", back_populates="messages")
    agent = relationship("Agent", back_populates="messages")
