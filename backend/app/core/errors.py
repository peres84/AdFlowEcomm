"""
Centralized error handling module for ProductFlow API.

This module provides:
- Custom exception classes for different error types
- Structured error response models
- Error logging utilities
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProductFlowError(Exception):
    """Base exception class for ProductFlow errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        retry_allowed: bool = True
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.retry_allowed = retry_allowed
        super().__init__(self.message)


class SessionNotFoundError(ProductFlowError):
    """Raised when a session is not found or has expired"""
    
    def __init__(self, session_id: str):
        super().__init__(
            message="Session not found or expired. Please start a new session.",
            status_code=404,
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id},
            retry_allowed=False
        )


class ValidationError(ProductFlowError):
    """Raised when request validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
            retry_allowed=False
        )


class FileUploadError(ProductFlowError):
    """Raised when file upload fails"""
    
    def __init__(self, message: str, filename: Optional[str] = None):
        details = {"filename": filename} if filename else {}
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            details=details,
            retry_allowed=True
        )


class ExternalAPIError(ProductFlowError):
    """Raised when external API calls fail (OpenAI, Runware)"""
    
    def __init__(
        self,
        service: str,
        message: str,
        original_error: Optional[str] = None
    ):
        details = {
            "service": service,
            "original_error": original_error
        }
        super().__init__(
            message=f"Failed to communicate with {service}: {message}",
            status_code=500,
            error_code="EXTERNAL_API_ERROR",
            details=details,
            retry_allowed=True
        )


class ImageGenerationError(ProductFlowError):
    """Raised when image generation fails"""
    
    def __init__(self, message: str, scenario: Optional[str] = None):
        details = {"scenario": scenario} if scenario else {}
        super().__init__(
            message=f"Image generation failed: {message}",
            status_code=500,
            error_code="IMAGE_GENERATION_ERROR",
            details=details,
            retry_allowed=True
        )


class VideoGenerationError(ProductFlowError):
    """Raised when video generation fails"""
    
    def __init__(self, message: str, scenario: Optional[str] = None):
        details = {"scenario": scenario} if scenario else {}
        super().__init__(
            message=f"Video generation failed: {message}",
            status_code=500,
            error_code="VIDEO_GENERATION_ERROR",
            details=details,
            retry_allowed=True
        )


class FFmpegError(ProductFlowError):
    """Raised when FFmpeg operations fail"""
    
    def __init__(self, message: str, command: Optional[str] = None):
        details = {"command": command} if command else {}
        super().__init__(
            message=f"Video processing failed: {message}",
            status_code=500,
            error_code="FFMPEG_ERROR",
            details=details,
            retry_allowed=True
        )


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
):
    """
    Log error with timestamp and context information.
    
    Args:
        error: The exception that occurred
        context: Additional context information
        session_id: Session ID if available
    """
    timestamp = datetime.now().isoformat()
    error_type = type(error).__name__
    error_message = str(error)
    
    log_data = {
        "timestamp": timestamp,
        "error_type": error_type,
        "error_message": error_message,
        "session_id": session_id,
        "context": context or {}
    }
    
    # Log with appropriate level
    if isinstance(error, ProductFlowError):
        if error.status_code >= 500:
            logger.error(f"Error occurred: {log_data}", exc_info=True)
        else:
            logger.warning(f"Client error: {log_data}")
    else:
        logger.error(f"Unexpected error: {log_data}", exc_info=True)


def create_error_response(
    error: Exception,
    include_details: bool = True
) -> Dict[str, Any]:
    """
    Create a structured error response.
    
    Args:
        error: The exception that occurred
        include_details: Whether to include detailed error information
        
    Returns:
        Dictionary with error response data
    """
    if isinstance(error, ProductFlowError):
        response = {
            "error": True,
            "error_code": error.error_code,
            "message": error.message,
            "retry_allowed": error.retry_allowed,
            "timestamp": datetime.now().isoformat()
        }
        
        if include_details and error.details:
            response["details"] = error.details
            
        return response
    else:
        # Generic error response for unexpected errors
        return {
            "error": True,
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again.",
            "retry_allowed": True,
            "timestamp": datetime.now().isoformat()
        }
