# Error Handling and Logging

This document describes the centralized error handling and logging system implemented for the ProductFlow API.

## Overview

The error handling system provides:
- **Custom exception classes** for different error types
- **Structured error responses** with consistent format
- **Comprehensive logging** with timestamps and context
- **Retry functionality** indication for recoverable errors
- **Global exception handlers** in FastAPI

## Custom Exception Classes

All custom exceptions inherit from `ProductFlowError` base class:

### ProductFlowError (Base Class)
```python
ProductFlowError(
    message: str,
    status_code: int = 500,
    error_code: str = "INTERNAL_ERROR",
    details: Optional[Dict[str, Any]] = None,
    retry_allowed: bool = True
)
```

### Specific Exception Types

1. **SessionNotFoundError** (404)
   - Raised when a session is not found or has expired
   - `retry_allowed = False`

2. **ValidationError** (400)
   - Raised when request validation fails
   - `retry_allowed = False`

3. **FileUploadError** (400)
   - Raised when file upload fails
   - `retry_allowed = True`

4. **ExternalAPIError** (500)
   - Raised when external API calls fail (OpenAI, Runware)
   - `retry_allowed = True`

5. **ImageGenerationError** (500)
   - Raised when image generation fails
   - `retry_allowed = True`

6. **VideoGenerationError** (500)
   - Raised when video generation fails
   - `retry_allowed = True`

7. **FFmpegError** (500)
   - Raised when FFmpeg operations fail
   - `retry_allowed = True`

## Error Response Format

All errors return a consistent JSON structure:

```json
{
  "error": true,
  "error_code": "SESSION_NOT_FOUND",
  "message": "Session not found or expired. Please start a new session.",
  "retry_allowed": false,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "details": {
    "session_id": "abc123"
  }
}
```

## Logging

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

### Log Format
```
2024-01-15 10:30:00 - app.api.session - INFO - New session created: abc123
```

### Colored Console Output
- DEBUG: Cyan
- INFO: Green
- WARNING: Yellow
- ERROR: Red
- CRITICAL: Magenta

### Configuration
Set log level via environment variable:
```bash
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Usage Examples

### In API Endpoints

```python
from app.core import (
    SessionNotFoundError,
    ValidationError,
    log_error
)
import logging

logger = logging.getLogger(__name__)

@router.post("/example")
async def example_endpoint(request: ExampleRequest):
    try:
        # Validate session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise SessionNotFoundError(request.session_id)
        
        # Validate input
        if not request.required_field:
            raise ValidationError(
                message="Required field is missing",
                field="required_field"
            )
        
        # Business logic
        logger.info(f"Processing request for session: {request.session_id}")
        result = do_something()
        
        return {"success": True, "result": result}
        
    except (SessionNotFoundError, ValidationError):
        # Let global handler catch these
        raise
    except Exception as e:
        # Log unexpected errors
        log_error(
            e,
            context={"endpoint": "/example"},
            session_id=request.session_id
        )
        raise
```

### External API Calls

```python
from app.core import ExternalAPIError

try:
    response = await openai_client.chat.completions.create(...)
except Exception as e:
    raise ExternalAPIError(
        service="OpenAI",
        message="Failed to generate response",
        original_error=str(e)
    )
```

### File Operations

```python
from app.core import FileUploadError

try:
    # File processing
    process_file(file_path)
except Exception as e:
    raise FileUploadError(
        message=f"Failed to process file: {str(e)}",
        filename=file.filename
    )
```

## Global Exception Handlers

The FastAPI app includes global exception handlers in `main.py`:

1. **ProductFlowError Handler**: Catches all custom exceptions
2. **HTTPException Handler**: Catches FastAPI HTTP exceptions
3. **RequestValidationError Handler**: Catches Pydantic validation errors
4. **General Exception Handler**: Catches all other unexpected exceptions

## Best Practices

1. **Always use specific exception types** when possible
2. **Include context information** in log_error calls
3. **Log at appropriate levels**:
   - INFO for successful operations
   - WARNING for client errors (4xx)
   - ERROR for server errors (5xx)
4. **Don't log sensitive information** (API keys, passwords, etc.)
5. **Provide user-friendly error messages** in exceptions
6. **Set retry_allowed appropriately**:
   - False for validation errors, session not found
   - True for external API failures, temporary issues

## Testing Error Handling

Test that errors are properly caught and formatted:

```python
def test_session_not_found():
    response = client.get("/api/session/invalid-id")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == True
    assert data["error_code"] == "SESSION_NOT_FOUND"
    assert data["retry_allowed"] == False
```

## Monitoring and Debugging

1. **Check logs** for error patterns
2. **Monitor error rates** by error_code
3. **Track retry_allowed errors** separately
4. **Set up alerts** for critical errors
5. **Use context information** to trace issues

## Environment Variables

```bash
# Logging configuration
LOG_LEVEL=INFO  # Default: INFO

# Other relevant settings
DEBUG=false
```

## Future Enhancements

- Add structured logging (JSON format) for production
- Implement error tracking service integration (Sentry, etc.)
- Add request ID tracking across services
- Implement rate limiting for retry attempts
- Add metrics collection for error rates
