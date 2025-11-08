from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio
from app.api import session, form
from app.services import session_manager

# Load environment variables
load_dotenv()


async def cleanup_task():
    """Background task to cleanup expired sessions every 5 minutes"""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        session_manager.cleanup_expired_sessions()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Start the cleanup task
    cleanup_task_handle = asyncio.create_task(cleanup_task())
    yield
    # Shutdown: Cancel the cleanup task
    cleanup_task_handle.cancel()
    try:
        await cleanup_task_handle
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="ProductFlow API",
    description="AI-powered product video generator API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories for serving uploaded files and outputs
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Include routers
app.include_router(session.router)
app.include_router(form.router)

@app.get("/")
async def root():
    return {
        "message": "ProductFlow API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/stats")
async def get_stats():
    """Get API statistics including active session count"""
    return {
        "active_sessions": session_manager.get_session_count()
    }
