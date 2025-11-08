from fastapi import APIRouter
from pydantic import BaseModel
from app.services import session_manager
from app.models.session import SessionData
from app.core import SessionNotFoundError, log_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/session", tags=["session"])


class SessionCreateResponse(BaseModel):
    """Response model for session creation"""
    session_id: str


class SessionResponse(BaseModel):
    """Response model for session retrieval"""
    session_data: SessionData


@router.post("/create", response_model=SessionCreateResponse)
async def create_session():
    """
    Create a new session.
    
    Returns:
        SessionCreateResponse with the new session ID
    """
    try:
        session_id = session_manager.create_session()
        logger.info(f"New session created: {session_id}")
        return SessionCreateResponse(session_id=session_id)
    except Exception as e:
        log_error(e, context={"endpoint": "/api/session/create"})
        raise


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Retrieve a session by ID.
    
    Args:
        session_id: The session ID to retrieve
        
    Returns:
        SessionResponse with the session data
        
    Raises:
        SessionNotFoundError: If session not found or expired
    """
    try:
        session_data = session_manager.get_session(session_id)
        
        if session_data is None:
            raise SessionNotFoundError(session_id)
        
        logger.info(f"Session retrieved: {session_id}")
        return SessionResponse(session_data=session_data)
    except SessionNotFoundError:
        raise
    except Exception as e:
        log_error(e, context={"endpoint": "/api/session/{session_id}", "session_id": session_id})
        raise


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session by ID.
    
    Args:
        session_id: The session ID to delete
        
    Returns:
        Success message
        
    Raises:
        SessionNotFoundError: If session not found
    """
    try:
        success = session_manager.delete_session(session_id)
        
        if not success:
            raise SessionNotFoundError(session_id)
        
        logger.info(f"Session deleted: {session_id}")
        return {"message": "Session deleted successfully"}
    except SessionNotFoundError:
        raise
    except Exception as e:
        log_error(e, context={"endpoint": "/api/session/delete", "session_id": session_id})
        raise


@router.post("/cleanup")
async def cleanup_sessions():
    """
    Manually trigger cleanup of expired sessions.
    
    Returns:
        Number of sessions cleaned up
    """
    try:
        count = session_manager.cleanup_expired_sessions()
        logger.info(f"Manual cleanup completed: {count} sessions removed")
        return {"cleaned_up": count}
    except Exception as e:
        log_error(e, context={"endpoint": "/api/session/cleanup"})
        raise
