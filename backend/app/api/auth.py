from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    password: str

@router.get("/status")
async def get_auth_status():
    """Check if authentication is required."""
    return {
        "required": settings.app_password is not None and len(settings.app_password) > 0
    }

@router.post("/verify")
async def verify_password(data: LoginRequest = Body(...)):
    """Verify the application password."""
    if not settings.app_password:
        return {"success": True, "message": "No password configured"}
        
    if data.password == settings.app_password:
        return {"success": True, "token": "authenticated"} # In a real app, return a JWT
    else:
        raise HTTPException(status_code=401, detail="Incorrect password")
