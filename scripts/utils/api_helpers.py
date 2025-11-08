"""
API Helper Utilities

Common API operations used across testing scripts:
- Request building
- Response parsing
- Error handling
- UUID generation
"""

import uuid
import base64
import os
from typing import Dict, Any, Optional


def generate_task_uuid() -> str:
    """
    Generate a unique UUID v4 for API tasks.
    
    Returns:
        str: UUID v4 string
        
    Example:
        >>> task_id = generate_task_uuid()
        >>> print(task_id)
        '550e8400-e29b-41d4-a716-446655440000'
    """
    return str(uuid.uuid4())


def encode_image_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path: Path to image file
        
    Returns:
        str: Base64 encoded image
        
    Raises:
        FileNotFoundError: If image doesn't exist
        
    Example:
        >>> b64_image = encode_image_base64("product.jpg")
        >>> print(len(b64_image))
        123456
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_runware_headers(api_key: str) -> Dict[str, str]:
    """
    Build standard headers for Runware API requests.
    
    Args:
        api_key: Runware API key
        
    Returns:
        Dict with required headers
        
    Example:
        >>> headers = build_runware_headers("your_api_key")
        >>> print(headers)
        {'Content-Type': 'application/json', 'Authorization': 'Bearer your_api_key'}
    """
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }


def build_mirelo_headers(api_key: str) -> Dict[str, str]:
    """
    Build standard headers for Mirelo API requests.
    
    Args:
        api_key: Mirelo API key
        
    Returns:
        Dict with required headers
        
    Example:
        >>> headers = build_mirelo_headers("your_api_key")
        >>> print(headers)
        {'Content-Type': 'application/json', 'x-api-key': 'your_api_key'}
    """
    return {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }


def extract_response_data(
    response_json: Dict[str, Any],
    data_key: str = "data",
    fallback_keys: Optional[list] = None
) -> list:
    """
    Extract data array from API response with fallback keys.
    
    Args:
        response_json: JSON response from API
        data_key: Primary key to look for (default: "data")
        fallback_keys: Alternative keys to try (e.g., ["results"])
        
    Returns:
        List of data items, or empty list if not found
        
    Example:
        >>> response = {"data": [{"id": 1}, {"id": 2}]}
        >>> items = extract_response_data(response)
        >>> print(len(items))
        2
    """
    if fallback_keys is None:
        fallback_keys = ["results"]
    
    # Try primary key
    if data_key in response_json:
        return response_json[data_key]
    
    # Try fallback keys
    for key in fallback_keys:
        if key in response_json:
            return response_json[key]
    
    return []


def find_task_in_response(
    response_json: Dict[str, Any],
    task_uuid: str,
    data_key: str = "data"
) -> Optional[Dict[str, Any]]:
    """
    Find a specific task in API response by UUID.
    
    Args:
        response_json: JSON response from API
        task_uuid: UUID to search for
        data_key: Key containing data array
        
    Returns:
        Task data dict, or None if not found
        
    Example:
        >>> response = {"data": [{"taskUUID": "abc-123", "status": "success"}]}
        >>> task = find_task_in_response(response, "abc-123")
        >>> print(task["status"])
        'success'
    """
    data = extract_response_data(response_json, data_key)
    
    for item in data:
        if item.get("taskUUID") == task_uuid:
            return item
    
    return None


def check_api_error(
    response_json: Dict[str, Any],
    task_uuid: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Check if API response contains errors.
    
    Args:
        response_json: JSON response from API
        task_uuid: Optional UUID to match specific error
        
    Returns:
        Error dict if found, None otherwise
        
    Example:
        >>> response = {"errors": [{"code": "invalid", "message": "Bad request"}]}
        >>> error = check_api_error(response)
        >>> print(error["code"])
        'invalid'
    """
    if "errors" not in response_json:
        return None
    
    errors = response_json["errors"]
    if not errors:
        return None
    
    # If task_uuid provided, find matching error
    if task_uuid:
        for error in errors:
            if error.get("taskUUID") == task_uuid:
                return error
        return None
    
    # Return first error
    return errors[0]


def format_api_error(error: Dict[str, Any]) -> str:
    """
    Format API error for display.
    
    Args:
        error: Error dict from API
        
    Returns:
        Formatted error string
        
    Example:
        >>> error = {"code": "invalid", "message": "Bad request"}
        >>> print(format_api_error(error))
        'Error [invalid]: Bad request'
    """
    code = error.get("code", "unknown")
    message = error.get("message", "No message provided")
    
    error_str = f"Error [{code}]: {message}"
    
    if "documentation" in error:
        error_str += f"\nDocs: {error['documentation']}"
    
    return error_str


def validate_api_key(api_key: Optional[str], service_name: str = "API") -> bool:
    """
    Validate that API key is present.
    
    Args:
        api_key: API key to validate
        service_name: Name of service for error message
        
    Returns:
        bool: True if valid, False otherwise (prints error)
        
    Example:
        >>> if not validate_api_key(api_key, "Runware"):
        ...     return
        ❌ Missing Runware API key
    """
    if not api_key:
        print(f"❌ Missing {service_name} API key")
        return False
    return True


def build_image_upload_payload(
    image_path: str,
    task_uuid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build payload for image upload to Runware.
    
    Args:
        image_path: Path to image file
        task_uuid: Optional task UUID (generates if not provided)
        
    Returns:
        Dict with upload payload
        
    Example:
        >>> payload = build_image_upload_payload("product.jpg")
        >>> print(payload["taskType"])
        'imageUpload'
    """
    if task_uuid is None:
        task_uuid = generate_task_uuid()
    
    image_b64 = encode_image_base64(image_path)
    
    return {
        "taskType": "imageUpload",
        "taskUUID": task_uuid,
        "image": image_b64
    }
