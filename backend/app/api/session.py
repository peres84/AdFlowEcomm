from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import session_manager
from app.models.session import SessionData

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
    session_id = session_manager.create_session()
    return SessionCreateResponse(session_id=session_id)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Retrieve a session by ID.
    
    Args:
        session_id: The session ID to retrieve
        
    Returns:
        SessionResponse with the session data
        
    Raises:
        HTTPException: 404 if session not found or expired
    """
    session_data = session_manager.get_session(session_id)
    
    if session_data is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired"
        )
    
    return SessionResponse(session_data=session_data)


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session by ID.
    
    Args:
        session_id: The session ID to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if session not found
    """
    success = session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    return {"message": "Session deleted successfully"}


@router.post("/cleanup")
async def cleanup_sessions():
    """
    Manually trigger cleanup of expired sessions.
    
    Returns:
        Number of sessions cleaned up
    """
    count = session_manager.cleanup_expired_sessions()
    return {"cleaned_up": count}
