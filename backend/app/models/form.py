from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class FormSubmission(BaseModel):
    """Model for form submission data"""
    session_id: str = Field(..., description="Session ID for the user")
    product_name: str = Field(..., min_length=1, max_length=200, description="Name of the product")
    category: str = Field(..., min_length=1, description="Product category")
    target_audience: str = Field(..., min_length=1, description="Target audience for the product")
    main_benefit: str = Field(..., min_length=1, max_length=1000, description="Main benefit of the product")
    brand_colors: List[str] = Field(..., min_items=1, description="Brand color palette (hex codes or color names)")
    brand_tone: str = Field(..., min_length=1, description="Brand tone (e.g., professional, casual, playful)")
    target_platform: str = Field(..., min_length=1, description="Target platform (e.g., Instagram, TikTok, YouTube)")
    website_url: Optional[str] = Field(None, description="Website URL (optional)")
    scene_description: str = Field(..., min_length=1, max_length=2000, description="Scene description for visual style")


class FormSubmissionResponse(BaseModel):
    """Response model for form submission"""
    success: bool
    message: str
    session_id: str
