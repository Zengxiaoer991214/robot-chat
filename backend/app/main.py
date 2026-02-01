"""
Main FastAPI application.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.api import agents, roles, rooms, websocket, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting application...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Reset any "running" rooms to "idle" on startup (since orchestrators are in-memory)
    from app.core.database import SessionLocal
    from app.models import Room
    
    db = SessionLocal()
    try:
        running_rooms = db.query(Room).filter(Room.status == "running").all()
        for room in running_rooms:
            room.status = "idle"
            logger.info(f"Reset room {room.id} status to idle on startup")
        db.commit()
    except Exception as e:
        logger.error(f"Error resetting room statuses: {str(e)}")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="AI Group Chat API",
    description="API for AI-powered group chat system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(agents.router)
app.include_router(roles.router)
app.include_router(rooms.router)
app.include_router(websocket.router)


# Serve SPA if dist directory exists (Production)
dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")

if os.path.exists(dist_dir):
    # Mount static files
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")

    # SPA Fallback for 404
    @app.exception_handler(StarletteHTTPException)
    async def spa_fallback(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            # Check if it's an API call
            if request.url.path.startswith("/api") or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
                return JSONResponse(status_code=404, content={"detail": "Not Found"})
            # Fallback to index.html
            return FileResponse(os.path.join(dist_dir, "index.html"))
        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail)})

else:
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "AI Group Chat API",
            "version": "1.0.0",
            "docs": "/docs"
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
