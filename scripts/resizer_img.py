"""
Image Resizer Utility

This module provides professional image resizing functionality for API requests
that have strict dimension requirements. Commonly used when API endpoints reject
images due to invalid width/height constraints.

Typical use case:
    1. Attempt API request with original image
    2. If request fails due to dimension errors, use resize_image()
    3. Retry API request with resized image

Example:
    from scripts.resizer_img import resize_image
    
    try:
        # Attempt API call with original image
        result = api_call(image_path)
    except DimensionError:
        # Resize and retry
        resized_path = resize_image(image_path, 1366, 768)
        result = api_call(resized_path)
"""

from PIL import Image
import os
from typing import Optional, Tuple


def resize_image(
    image_path: str,
    target_width: int,
    target_height: int,
    output_path: Optional[str] = None,
    output_format: str = "JPEG",
    quality: int = 95,
    maintain_aspect_ratio: bool = False
) -> str:
    """
    Resize an image to specified dimensions with professional quality settings.
    
    This function is designed to handle API dimension requirements by resizing
    images to exact specifications. Useful when API requests fail due to
    invalid image dimensions (e.g., "invalidFrameImageWidth" errors).
    
    Args:
        image_path: Path to the source image file
        target_width: Desired width in pixels
        target_height: Desired height in pixels
        output_path: Optional custom output path. If None, saves as 
                    'resized_<original_name>' in the same directory
        output_format: Image format for output (JPEG, PNG, WEBP, etc.)
        quality: Compression quality (1-100). Higher = better quality, larger file
        maintain_aspect_ratio: If True, resizes to fit within target dimensions
                              while maintaining aspect ratio. If False, stretches
                              to exact dimensions (default behavior for API compliance)
    
    Returns:
        str: Path to the resized image file
    
    Raises:
        FileNotFoundError: If the source image doesn't exist
        ValueError: If dimensions are invalid (<=0)
        IOError: If image cannot be opened or saved
    
    Example:
        >>> # Resize for API that requires 1366x768
        >>> resized = resize_image("photo.jpg", 1366, 768)
        >>> print(f"Resized image saved at: {resized}")
        
        >>> # Resize with custom output path and maintain aspect ratio
        >>> resized = resize_image(
        ...     "photo.jpg", 
        ...     1920, 
        ...     1080,
        ...     output_path="output/resized.jpg",
        ...     maintain_aspect_ratio=True
        ... )
    """
    # Validation
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    if target_width <= 0 or target_height <= 0:
        raise ValueError(f"Invalid dimensions: {target_width}x{target_height}")
    
    if not 1 <= quality <= 100:
        raise ValueError(f"Quality must be between 1-100, got: {quality}")
    
    # Open and process image
    try:
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if saving as JPEG
        if output_format.upper() == "JPEG" and img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
            img = rgb_img
        
        # Resize logic
        if maintain_aspect_ratio:
            img.thumbnail((target_width, target_height), Image.LANCZOS)
        else:
            img = img.resize((target_width, target_height), Image.LANCZOS)
        
        # Determine output path
        if output_path is None:
            directory = os.path.dirname(image_path)
            filename = os.path.basename(image_path)
            name, _ = os.path.splitext(filename)
            ext = output_format.lower() if output_format.lower() != "jpeg" else "jpg"
            output_path = os.path.join(directory, f"resized_{name}.{ext}")
        
        # Save with appropriate settings
        save_kwargs = {"format": output_format}
        if output_format.upper() in ["JPEG", "WEBP"]:
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        
        img.save(output_path, **save_kwargs)
        
        return output_path
        
    except Exception as e:
        raise IOError(f"Failed to process image: {str(e)}")


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Get the dimensions of an image without loading it fully into memory.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Tuple[int, int]: (width, height) in pixels
    
    Raises:
        FileNotFoundError: If the image doesn't exist
        IOError: If the image cannot be opened
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        raise IOError(f"Failed to read image dimensions: {str(e)}")


def validate_dimensions(
    image_path: str,
    required_width: int,
    required_height: int,
    tolerance: int = 0
) -> bool:
    """
    Check if an image meets dimension requirements.
    
    Useful for pre-validating images before API calls to avoid
    dimension-related errors.
    
    Args:
        image_path: Path to the image file
        required_width: Required width in pixels
        required_height: Required height in pixels
        tolerance: Acceptable deviation in pixels (default: 0 for exact match)
    
    Returns:
        bool: True if dimensions are within tolerance, False otherwise
    
    Example:
        >>> if not validate_dimensions("image.jpg", 1366, 768):
        ...     image_path = resize_image("image.jpg", 1366, 768)
    """
    try:
        width, height = get_image_dimensions(image_path)
        width_ok = abs(width - required_width) <= tolerance
        height_ok = abs(height - required_height) <= tolerance
        return width_ok and height_ok
    except (FileNotFoundError, IOError):
        return False
