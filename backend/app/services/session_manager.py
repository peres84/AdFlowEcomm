import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.models.session import SessionData
import logging

logger = logging.getLogger(__name__)

# In-memory session store
sessions: Dict[str, SessionData] = {}

# Session TTL in minutes (default 30)
SESSION_TTL_MINUTES = 30


def create_session() -> str:
    """
    Create a new session with a unique ID.
    
    Returns:
        str: The generated session ID
    """
    session_id = str(uuid.uuid4())
    now = datetime.now()
    
    session_data = SessionData(
        session_id=session_id,
        created_at=now,
        expires_at=now + timedelta(minutes=SESSION_TTL_MINUTES)
    )
    
    sessions[session_id] = session_data
    logger.info(f"Created new session: {session_id}")
    
    return session_id


def get_session(session_id: str) -> Optional[SessionData]:
    """
    Retrieve a session by ID if it exists and hasn't expired.
    
    Args:
        session_id: The session ID to retrieve
        
    Returns:
        SessionData if found and valid, None otherwise
    """
    session = sessions.get(session_id)
    
    if session:
        # Check if session has expired
        if session.expires_at > datetime.now():
            return session
        else:
            # Session expired, remove it
            logger.info(f"Session expired: {session_id}")
            del sessions[session_id]
            return None
    
    return None


def update_session(session_id: str, session_data: SessionData) -> bool:
    """
    Update an existing session.
    
    Args:
        session_id: The session ID to update
        session_data: The updated session data
        
    Returns:
        bool: True if successful, False if session not found
    """
    if session_id in sessions:
        sessions[session_id] = session_data
        logger.info(f"Updated session: {session_id}")
        return True
    
    logger.warning(f"Attempted to update non-existent session: {session_id}")
    return False


def delete_session(session_id: str) -> bool:
    """
    Delete a session by ID.
    
    Args:
        session_id: The session ID to delete
        
    Returns:
        bool: True if deleted, False if not found
    """
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Deleted session: {session_id}")
        return True
    
    return False


def cleanup_expired_sessions() -> int:
    """
    Remove all expired sessions from the store.
    
    Returns:
        int: Number of sessions cleaned up
    """
    now = datetime.now()
    expired_sessions = [
        sid for sid, session in sessions.items()
        if session.expires_at <= now
    ]
    
    for session_id in expired_sessions:
        del sessions[session_id]
    
    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    return len(expired_sessions)


def get_session_count() -> int:
    """
    Get the current number of active sessions.
    
    Returns:
        int: Number of active sessions
    """
    return len(sessions)
