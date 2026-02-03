from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db, SessionLocal
from app.models import Agent, Role, ChatSession, ChatSessionMessage, User
from app.schemas import (
    ChatRequest, ChatCompletionResponse, 
    ChatSessionResponse, ChatSessionCreate, 
    ChatSessionMessageResponse
)
from app.services.llm_adapter import get_llm_adapter
from app.api.deps import get_current_user
import logging
from typing import List

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# ===== Session Management Endpoints =====

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all chat sessions ordered by updated_at desc for current user."""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()
    return sessions

@router.post("/sessions", response_model=ChatSessionResponse)
def create_session(session_in: ChatSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new chat session."""
    # Validate agent ownership
    agent = db.query(Agent).filter(Agent.id == session_in.agent_id, Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or access denied")
        
    if session_in.role_id:
        role = db.query(Role).filter(Role.id == session_in.role_id, Role.user_id == current_user.id).first()
        if not role:
             raise HTTPException(status_code=404, detail="Role not found or access denied")

    session = ChatSession(
        user_id=current_user.id,
        agent_id=session_in.agent_id,
        role_id=session_in.role_id,
        title=session_in.title or "New Chat"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()

@router.get("/sessions/{session_id}/messages", response_model=List[ChatSessionMessageResponse])
def get_session_messages(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get messages for a specific session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = db.query(ChatSessionMessage).filter(ChatSessionMessage.session_id == session_id).order_by(ChatSessionMessage.created_at).all()
    return messages


# ===== Completion Endpoint =====

async def stream_and_save(generator, session_id: int):
    """Wrapper to save streamed content to DB."""
    full_content = ""
    try:
        async for chunk in generator:
            full_content += chunk
            yield chunk
    finally:
        # Save complete message to DB using a new session
        # This runs after the response is fully sent (or if client disconnects?)
        # Ideally, we save what we have.
        if full_content:
            try:
                db = SessionLocal()
                msg = ChatSessionMessage(
                    session_id=session_id,
                    role="assistant",
                    content=full_content
                )
                db.add(msg)
                # Update session timestamp
                session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
                if session:
                    session.updated_at = session.updated_at # force update? No, assigning new value.
                    # SQLA automatically updates onupdate=... but we need to trigger it.
                    # Just committing might work if we touch it.
                    from datetime import datetime
                    session.updated_at = datetime.utcnow()
                db.commit()
                db.close()
            except Exception as e:
                logger.error(f"Failed to save assistant message: {e}")

@router.post("/completion", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a chat completion from a specific agent and optional role.
    """
    try:
        # 3. Handle Session Persistence & Validation
        session_id = request.session_id
        if session_id:
             # Verify session ownership
             session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
             if not session:
                 raise HTTPException(status_code=404, detail="Session not found or access denied")
             
             # Use agent/role from session? Or request? 
             # Request might be standalone. If session_id is passed, we should respect session config or request overrides?
             # For now, let's use request params but validate they match user ownership if provided.
             
        # 1. Get Agent
        agent = db.query(Agent).filter(Agent.id == request.agent_id, Agent.user_id == current_user.id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found or access denied")

        # 2. Get Role (if provided) and construct system prompt
        base_prompt = agent.system_prompt or ""  # Use empty string if None
        
        system_prompt = base_prompt
        
        if request.role_id:
            role = db.query(Role).filter(Role.id == request.role_id, Role.user_id == current_user.id).first()
            if role:
                # Construct persona prompt
                persona_parts = [f"Name: {role.name}"]
                if role.gender: persona_parts.append(f"Gender: {role.gender}")
                if role.age: persona_parts.append(f"Age: {role.age}")
                if role.profession: persona_parts.append(f"Profession: {role.profession}")
                if role.personality: persona_parts.append(f"Personality: {role.personality}")
                
                persona_text = "\n".join(persona_parts)
                
                # Combine agent prompt (base instruction) with role prompt (persona)
                if base_prompt:
                    system_prompt = f"{base_prompt}\n\nRole Persona:\n{persona_text}"
                else:
                    system_prompt = f"Role Persona:\n{persona_text}"
            else:
                 # Role requested but not found/owned
                 raise HTTPException(status_code=404, detail="Role not found or access denied")

        if not session_id:
            # Create new session if not provided
            new_session = ChatSession(
                user_id=current_user.id,
                agent_id=request.agent_id,
                role_id=request.role_id,
                title=request.message[:30] + "..." if len(request.message) > 30 else request.message
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id
        
        # Save User Message
        user_msg = ChatSessionMessage(
            session_id=session_id,
            role="user",
            content=request.message,
            image_url=request.image
        )
        db.add(user_msg)
        
        # Update session timestamp
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            # Re-touch to update timestamp
            from datetime import datetime
            session.updated_at = datetime.utcnow()
            
        db.commit()

        # 4. Prepare Messages (Load from DB + Current)
        # Strategy: We trust the DB state.
        # But we also need to respect the 'history' passed if we want to support non-persistent context?
        # Actually, if we use session_id, we should load from DB.
        # Let's load last 20 messages from this session.
        
        db_messages = db.query(ChatSessionMessage).filter(ChatSessionMessage.session_id == session_id).order_by(ChatSessionMessage.created_at).all()
        
        valid_messages = []
        for msg in db_messages:
            # Exclude the current one we just added? No, we need it.
            # But we haven't generated response yet.
            # Convert DB message to LLM format
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.image_url:
                 msg_dict["image"] = msg.image_url # Pass image to adapter
            valid_messages.append(msg_dict)
            
        # 5. Call LLM
        adapter = get_llm_adapter(
            provider=agent.provider,
            model_name=agent.model_name,
            temperature=agent.temperature,
            api_key=agent.api_key_config,
            use_proxy=agent.use_proxy
        )
        
        if request.stream:
            return StreamingResponse(
                stream_and_save(adapter.generate_stream(valid_messages, system_prompt), session_id),
                media_type="text/plain"
            )
        
        # Non-streaming
        response_content = await adapter.generate(valid_messages, system_prompt)
        
        # Save Assistant Message
        asst_msg = ChatSessionMessage(
            session_id=session_id,
            role="assistant",
            content=response_content
        )
        db.add(asst_msg)
        db.commit()
        
        return ChatCompletionResponse(content=response_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")
