"""
API endpoints for agent management.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from sqlalchemy import or_
from app.core.database import get_db
from app.models import Agent, User
from app.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new AI agent.
    
    Args:
        agent_data: Agent creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created agent
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate provider
        valid_providers = ["openai", "deepseek", "ollama", "google", "chatanywhere", "dashscope"]
        if agent_data.provider.lower() not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )
        
        # Create agent
        agent = Agent(**agent_data.model_dump(), user_id=current_user.id)
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Created agent: {agent.name} (ID: {agent.id}) for user {current_user.username}")
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
async def get_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all available AI agents for the current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of agents
    """
    try:
        # Return agents created by current user OR global agents
        agents = db.query(Agent).filter(
            or_(
                Agent.user_id == current_user.id,
                Agent.is_global == True
            )
        ).order_by(Agent.id.desc()).offset(skip).limit(limit).all()
        return agents
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a specific agent by ID.
    
    Args:
        agent_id: Agent ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Agent details
        
    Raises:
        HTTPException: If agent not found or access denied
    """
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == current_user.id).first()
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
async def update_agent(agent_id: int, agent_data: AgentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update an agent.
    
    Args:
        agent_id: Agent ID
        agent_data: Update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated agent
        
    Raises:
        HTTPException: If agent not found or access denied
    """
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )

        if agent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this agent"
            )
        
        # Update fields
        update_data = agent_data.model_dump(exclude_unset=True)
        
        # If api_key_config is provided but empty, do not update it (keep existing)
        if "api_key_config" in update_data and update_data["api_key_config"] == "":
            del update_data["api_key_config"]
            
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
async def delete_agent(agent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete an agent.
    
    Args:
        agent_id: Agent ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If agent not found or access denied
    """
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == current_user.id).first()
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
