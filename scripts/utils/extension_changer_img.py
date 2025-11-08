"""
Image Format Converter Utility

This module provides professional image format conversion functionality for API requests
that have strict format requirements. Commonly used when API endpoints reject images
due to unsupported file extensions or formats.

Typical use case:
    1. Attempt API request with original image format
    2. If request fails due to format/extension errors, use convert_image_format()
    3. Retry API request with converted image

Example:
    from scripts.extension_changer_img import convert_image_format
    
    try:
        # Attempt API call with original image
        result = api_call("image.png")
    except UnsupportedFormatError:
        # Convert and retry
        converted_path = convert_image_format("image.png", "JPEG")
        result = api_call(converted_path)
"""

from PIL import Image
import os
from typing import Optional, Dict


# Supported format mappings
SUPPORTED_FORMATS = {
    "JPEG": [".jpg", ".jpeg"],
    "PNG": [".png"],
    "WEBP": [".webp"],
    "BMP": [".bmp"],
    "TIFF": [".tiff", ".tif"],
    "GIF": [".gif"]
}

# Common API format requirements
API_PREFERRED_FORMATS = {
    "runware": ["JPEG", "PNG", "WEBP"],
    "openai": ["PNG", "JPEG", "WEBP", "GIF"],
    "stability": ["PNG", "JPEG", "WEBP"],
    "midjourney": ["PNG", "JPEG", "WEBP", "GIF"]
}


def convert_image_format(
    image_path: str,
    target_format: str,
    output_path: Optional[str] = None,
    quality: int = 95,
    optimize: bool = True,
    preserve_transparency: bool = True
) -> str:
    """
    Convert an image to a different format with professional quality settings.
    
    This function handles API format requirements by converting images to
    supported formats. Useful when API requests fail due to unsupported
    file extensions (e.g., "unsupportedImageFormat" errors).
    
    Args:
        image_path: Path to the source image file
        target_format: Desired output format (JPEG, PNG, WEBP, BMP, TIFF, GIF)
        output_path: Optional custom output path. If None, saves as 
                    '<original_name>.<new_ext>' in the same directory
        quality: Compression quality for lossy formats (1-100). 
                Higher = better quality, larger file
        optimize: Enable optimization for smaller file sizes (JPEG, PNG, WEBP)
        preserve_transparency: If True and source has alpha channel, converts
                              to PNG if target format doesn't support transparency
    
    Returns:
        str: Path to the converted image file
    
    Raises:
        FileNotFoundError: If the source image doesn't exist
        ValueError: If target format is not supported
        IOError: If image cannot be opened or saved
    
    Example:
        >>> # Convert PNG to JPEG for API compatibility
        >>> converted = convert_image_format("photo.png", "JPEG")
        >>> print(f"Converted image: {converted}")
        
        >>> # Convert with custom output path
        >>> converted = convert_image_format(
        ...     "photo.bmp",
        ...     "WEBP",
        ...     output_path="output/photo.webp",
        ...     quality=90
        ... )
    """
    # Validation
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    target_format = target_format.upper()
    if target_format not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS.keys())
        raise ValueError(f"Unsupported format: {target_format}. Supported: {supported}")
    
    if not 1 <= quality <= 100:
        raise ValueError(f"Quality must be between 1-100, got: {quality}")
    
    try:
        # Open image
        img = Image.open(image_path)
        original_format = img.format
        has_transparency = img.mode in ("RGBA", "LA", "P") and "transparency" in img.info
        
        # Handle transparency preservation
        if has_transparency and preserve_transparency:
            if target_format not in ["PNG", "WEBP", "GIF"]:
                print(f"⚠️  Target format {target_format} doesn't support transparency. Converting to PNG instead.")
                target_format = "PNG"
        
        # Convert RGBA to RGB for formats that don't support alpha
        if target_format in ["JPEG", "BMP"] and img.mode in ("RGBA", "LA", "P"):
            # Create white background
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            rgb_img.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            img = rgb_img
        
        # Determine output path
        if output_path is None:
            directory = os.path.dirname(image_path)
            filename = os.path.basename(image_path)
            name, _ = os.path.splitext(filename)
            ext = SUPPORTED_FORMATS[target_format][0]
            output_path = os.path.join(directory, f"{name}{ext}")
        
        # Prepare save parameters
        save_kwargs = {"format": target_format}
        
        if target_format == "JPEG":
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = optimize
        elif target_format == "PNG":
            save_kwargs["optimize"] = optimize
        elif target_format == "WEBP":
            save_kwargs["quality"] = quality
            save_kwargs["method"] = 6 if optimize else 4
        elif target_format == "GIF":
            if img.mode != "P":
                img = img.convert("P", palette=Image.ADAPTIVE)
        
        # Save converted image
        img.save(output_path, **save_kwargs)
        
        print(f"✅ Converted {original_format} → {target_format}: {output_path}")
        return output_path
        
    except Exception as e:
        raise IOError(f"Failed to convert image: {str(e)}")


def get_image_format(image_path: str) -> str:
    """
    Get the format of an image file.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        str: Image format (e.g., "JPEG", "PNG", "WEBP")
    
    Raises:
        FileNotFoundError: If the image doesn't exist
        IOError: If the image cannot be opened
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            return img.format
    except Exception as e:
        raise IOError(f"Failed to read image format: {str(e)}")


def is_format_supported(image_path: str, supported_formats: list) -> bool:
    """
    Check if an image format is in the list of supported formats.
    
    Useful for pre-validating images before API calls to avoid
    format-related errors.
    
    Args:
        image_path: Path to the image file
        supported_formats: List of supported format names (e.g., ["JPEG", "PNG"])
    
    Returns:
        bool: True if format is supported, False otherwise
    
    Example:
        >>> if not is_format_supported("image.bmp", ["JPEG", "PNG"]):
        ...     image_path = convert_image_format("image.bmp", "JPEG")
    """
    try:
        current_format = get_image_format(image_path)
        return current_format in [fmt.upper() for fmt in supported_formats]
    except (FileNotFoundError, IOError):
        return False


def convert_for_api(
    image_path: str,
    api_name: str,
    output_path: Optional[str] = None,
    preferred_format: Optional[str] = None
) -> str:
    """
    Convert an image to a format compatible with a specific API.
    
    This is a convenience function that uses predefined format requirements
    for common APIs. If the image is already in a supported format, it returns
    the original path without conversion.
    
    Args:
        image_path: Path to the source image file
        api_name: Name of the API (runware, openai, stability, midjourney)
        output_path: Optional custom output path
        preferred_format: Override the default preferred format for the API
    
    Returns:
        str: Path to the converted image (or original if already compatible)
    
    Raises:
        ValueError: If API name is not recognized
        FileNotFoundError: If the source image doesn't exist
        IOError: If conversion fails
    
    Example:
        >>> # Auto-convert for Runware API
        >>> image_path = convert_for_api("photo.bmp", "runware")
        
        >>> # Convert with specific format preference
        >>> image_path = convert_for_api("photo.tiff", "openai", preferred_format="PNG")
    """
    api_name = api_name.lower()
    
    if api_name not in API_PREFERRED_FORMATS:
        available = ", ".join(API_PREFERRED_FORMATS.keys())
        raise ValueError(f"Unknown API: {api_name}. Available: {available}")
    
    supported_formats = API_PREFERRED_FORMATS[api_name]
    
    # Check if already in supported format
    if is_format_supported(image_path, supported_formats):
        print(f"✅ Image format already supported by {api_name} API")
        return image_path
    
    # Determine target format
    if preferred_format:
        target_format = preferred_format.upper()
        if target_format not in supported_formats:
            print(f"⚠️  {target_format} not in {api_name} supported formats. Using {supported_formats[0]} instead.")
            target_format = supported_formats[0]
    else:
        target_format = supported_formats[0]  # Use first as default
    
    print(f"🔄 Converting image for {api_name} API to {target_format}...")
    return convert_image_format(image_path, target_format, output_path)


def batch_convert(
    image_paths: list,
    target_format: str,
    output_dir: Optional[str] = None,
    quality: int = 95
) -> Dict[str, str]:
    """
    Convert multiple images to the same format.
    
    Args:
        image_paths: List of paths to source images
        target_format: Desired output format for all images
        output_dir: Optional directory for converted images. If None, saves
                   in same directory as source
        quality: Compression quality (1-100)
    
    Returns:
        Dict[str, str]: Mapping of original paths to converted paths
    
    Example:
        >>> images = ["photo1.png", "photo2.bmp", "photo3.tiff"]
        >>> converted = batch_convert(images, "JPEG", output_dir="converted/")
        >>> print(f"Converted {len(converted)} images")
    """
    results = {}
    
    for image_path in image_paths:
        try:
            if output_dir:
                filename = os.path.basename(image_path)
                name, _ = os.path.splitext(filename)
                ext = SUPPORTED_FORMATS[target_format.upper()][0]
                output_path = os.path.join(output_dir, f"{name}{ext}")
            else:
                output_path = None
            
            converted_path = convert_image_format(
                image_path,
                target_format,
                output_path=output_path,
                quality=quality
            )
            results[image_path] = converted_path
            
        except Exception as e:
            print(f"❌ Failed to convert {image_path}: {str(e)}")
            results[image_path] = None
    
    return results
