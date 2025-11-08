from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    message: str
    image_url: str = Field(..., description="URL to access the uploaded image")
    image_path: str = Field(..., description="Server path to the uploaded image")
    original_filename: str
    compressed: bool = Field(..., description="Whether the image was compressed")
    dimensions: dict = Field(..., description="Image dimensions (width, height)")


class UploadError(BaseModel):
    """Error response model for file upload"""
    error: bool = True
    message: str
    details: str
