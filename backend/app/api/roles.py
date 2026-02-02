"""
API endpoints for role management.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Role, Agent, User
from app.schemas import RoleCreate, RoleUpdate, RoleResponse
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role_data: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new Role (Persona).
    """
    try:
        # Check if agent exists and belongs to user
        agent = db.query(Agent).filter(Agent.id == role_data.agent_id, Agent.user_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {role_data.agent_id} not found or access denied"
            )
        
        role = Role(**role_data.model_dump(), user_id=current_user.id)
        db.add(role)
        db.commit()
        db.refresh(role)
        
        logger.info(f"Created role: {role.name} (ID: {role.id}) for user {current_user.username}")
        return role
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.get("", response_model=List[RoleResponse])
async def get_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all available roles for current user.
    """
    try:
        roles = db.query(Role).filter(Role.user_id == current_user.id).order_by(Role.created_at.desc()).offset(skip).limit(limit).all()
        return roles
    except Exception as e:
        logger.error(f"Error fetching roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch roles: {str(e)}"
        )


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a specific role by ID.
    """
    try:
        role = db.query(Role).filter(Role.id == role_id, Role.user_id == current_user.id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found"
            )
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch role: {str(e)}"
        )


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role_data: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a role.
    """
    try:
        role = db.query(Role).filter(Role.id == role_id, Role.user_id == current_user.id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found"
            )
            
        update_data = role_data.model_dump(exclude_unset=True)
        
        if 'agent_id' in update_data:
             # Verify new agent ownership
             agent = db.query(Agent).filter(Agent.id == update_data['agent_id'], Agent.user_id == current_user.id).first()
             if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {update_data['agent_id']} not found or access denied"
                )
        
        for key, value in update_data.items():
            setattr(role, key, value)
            
        db.commit()
        db.refresh(role)
        return role
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a role.
    """
    try:
        role = db.query(Role).filter(Role.id == role_id, Role.user_id == current_user.id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found"
            )
            
        db.delete(role)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}"
        )
