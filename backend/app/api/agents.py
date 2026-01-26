"""
API endpoints for agent management.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Agent
from app.schemas import AgentCreate, AgentUpdate, AgentResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """
    Create a new AI agent.
    
    Args:
        agent_data: Agent creation data
        db: Database session
        
    Returns:
        Created agent
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate provider
        valid_providers = ["openai", "deepseek", "ollama"]
        if agent_data.provider.lower() not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )
        
        # Create agent
        agent = Agent(**agent_data.model_dump())
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Created agent: {agent.name} (ID: {agent.id})")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("", response_model=List[AgentResponse])
async def get_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all available AI agents.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of agents
    """
    try:
        agents = db.query(Agent).offset(skip).limit(limit).all()
        return agents
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Get a specific agent by ID.
    
    Args:
        agent_id: Agent ID
        db: Database session
        
    Returns:
        Agent details
        
    Raises:
        HTTPException: If agent not found
    """
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch agent: {str(e)}"
        )


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent_data: AgentUpdate, db: Session = Depends(get_db)):
    """
    Update an agent.
    
    Args:
        agent_id: Agent ID
        agent_data: Update data
        db: Database session
        
    Returns:
        Updated agent
        
    Raises:
        HTTPException: If agent not found or update fails
    """
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        # Update fields
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Updated agent {agent_id}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Delete an agent.
    
    Args:
        agent_id: Agent ID
        db: Database session
        
    Raises:
        HTTPException: If agent not found or deletion fails
    """
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        db.delete(agent)
        db.commit()
        
        logger.info(f"Deleted agent {agent_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )
