from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from app.models.upload import FileUploadResponse, UploadError
from app.services import session_manager
import os
import logging
from PIL import Image
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
COMPRESSION_MAX_SIZE = 1024  # Max dimension for compression


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file.
    
    Args:
        file: The uploaded file
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )


def compress_image(
    image_path: str,
    max_size: int = COMPRESSION_MAX_SIZE,
    quality: int = 85
) -> tuple[str, bool, tuple[int, int]]:
    """
    Compress image using PIL if it exceeds max dimensions.
    
    Args:
        image_path: Path to the image file
        max_size: Maximum dimension (width or height)
        quality: JPEG quality (1-100)
        
    Returns:
        Tuple of (output_path, was_compressed, (width, height))
    """
    try:
        img = Image.open(image_path)
        original_size = img.size
        was_compressed = False
        
        # Check if compression is needed
        if img.width > max_size or img.height > max_size:
            # Calculate new dimensions maintaining aspect ratio
            if img.width > img.height:
                new_width = max_size
                new_height = int(img.height * (max_size / img.width))
            else:
                new_height = max_size
                new_width = int(img.width * (max_size / img.height))
            
            # Convert RGBA to RGB if saving as JPEG
            if img.mode == "RGBA":
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                img = rgb_img
            
            # Resize with high-quality LANCZOS algorithm
            img = img.resize((new_width, new_height), Image.LANCZOS)
            was_compressed = True
        
        # Save the image (compressed or original)
        save_kwargs = {"optimize": True}
        if img.format in ["JPEG", "JPG"] or image_path.lower().endswith(('.jpg', '.jpeg')):
            save_kwargs["quality"] = quality
            save_kwargs["format"] = "JPEG"
        
        img.save(image_path, **save_kwargs)
        final_size = img.size
        img.close()
        
        return image_path, was_compressed, final_size
        
    except Exception as e:
        logger.error(f"Failed to compress image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {str(e)}"
        )


async def save_uploaded_file(
    file: UploadFile,
    session_id: str,
    file_prefix: str
) -> tuple[str, str]:
    """
    Save uploaded file to disk.
    
    Args:
        file: The uploaded file
        session_id: Session ID for organizing files
        file_prefix: Prefix for the filename (e.g., 'product', 'logo')
        
    Returns:
        Tuple of (file_path, file_url)
    """
    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{session_id}_{file_prefix}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Generate URL for accessing the file
        file_url = f"/uploads/{unique_filename}"
        
        return file_path, file_url
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


@router.post("/product", response_model=FileUploadResponse)
async def upload_product_image(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and compress product image.
    
    This endpoint accepts a product image, validates it, compresses it if needed,
    and stores it in the session. The image is compressed to a maximum of 1024x1024
    while maintaining aspect ratio.
    
    Args:
        session_id: Session ID from form
        file: The product image file
        
    Returns:
        FileUploadResponse with image URL and metadata
        
    Raises:
        HTTPException: 404 if session not found, 400 for invalid file, 500 for processing errors
    """
    try:
        # Validate session
        session = session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Product upload failed: Session not found - {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired"
            )
        
        # Validate file
        validate_image_file(file)
        
        # Save file
        file_path, file_url = await save_uploaded_file(file, session_id, "product")
        
        # Compress image
        compressed_path, was_compressed, dimensions = compress_image(file_path)
        
        # Update session
        session.product_image_path = compressed_path
        session.product_image_url = file_url
        
        success = session_manager.update_session(session_id, session)
        if not success:
            logger.error(f"Failed to update session with product image: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save image to session"
            )
        
        logger.info(f"Product image uploaded successfully for session: {session_id}")
        
        return FileUploadResponse(
            success=True,
            message="Product image uploaded successfully",
            image_url=file_url,
            image_path=compressed_path,
            original_filename=file.filename,
            compressed=was_compressed,
            dimensions={"width": dimensions[0], "height": dimensions[1]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in product image upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during upload"
        )


@router.post("/logo", response_model=FileUploadResponse)
async def upload_logo_image(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and compress logo image (optional).
    
    This endpoint accepts a logo image, validates it, compresses it if needed,
    and stores it in the session. The logo is compressed to a maximum of 1024x1024
    while maintaining aspect ratio. PNG with transparent background is recommended.
    
    Args:
        session_id: Session ID from form
        file: The logo image file
        
    Returns:
        FileUploadResponse with image URL and metadata
        
    Raises:
        HTTPException: 404 if session not found, 400 for invalid file, 500 for processing errors
    """
    try:
        # Validate session
        session = session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Logo upload failed: Session not found - {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired"
            )
        
        # Validate file
        validate_image_file(file)
        
        # Save file
        file_path, file_url = await save_uploaded_file(file, session_id, "logo")
        
        # Compress image
        compressed_path, was_compressed, dimensions = compress_image(file_path)
        
        # Update session
        session.logo_image_path = compressed_path
        session.logo_image_url = file_url
        
        success = session_manager.update_session(session_id, session)
        if not success:
            logger.error(f"Failed to update session with logo image: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save logo to session"
            )
        
        logger.info(f"Logo image uploaded successfully for session: {session_id}")
        
        return FileUploadResponse(
            success=True,
            message="Logo image uploaded successfully",
            image_url=file_url,
            image_path=compressed_path,
            original_filename=file.filename,
            compressed=was_compressed,
            dimensions={"width": dimensions[0], "height": dimensions[1]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in logo image upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during upload"
        )
