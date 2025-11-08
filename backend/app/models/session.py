from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class GeneratedImage(BaseModel):
    """Model for a generated image"""
    id: str
    scenario: str  # hook, problem, solution, cta
    use_case: str
    prompt: str
    image_url: str
    has_logo: bool
    created_at: datetime


class SceneDescription(BaseModel):
    """Model for a video scene description"""
    scenario: str
    duration: int  # seconds
    visual_description: str
    camera_work: str
    lighting: str
    audio_design: str
    background_music: str
    sound_effects: str
    dialog_narration: str
    selected_image_id: str


class SceneVideo(BaseModel):
    """Model for a generated video scene"""
    scenario: str
    video_url: str
    duration: int
    status: str  # generating, completed, failed
    created_at: datetime


class SessionData(BaseModel):
    """Model for user session data"""
    session_id: str
    created_at: datetime
    expires_at: datetime
    
    # Form data
    product_name: Optional[str] = None
    category: Optional[str] = None
    target_audience: Optional[str] = None
    main_benefit: Optional[str] = None
    brand_colors: Optional[List[str]] = None
    brand_tone: Optional[str] = None
    target_platform: Optional[str] = None
    website_url: Optional[str] = None
    scene_description: Optional[str] = None
    
    # Uploaded files
    product_image_path: Optional[str] = None
    product_image_url: Optional[str] = None
    logo_image_path: Optional[str] = None
    logo_image_url: Optional[str] = None
    
    # Product analysis
    product_analysis: Optional[Dict] = None
    
    # Generated images
    generated_images: List[GeneratedImage] = []
    selected_images: Optional[Dict[str, str]] = None
    
    # Scene descriptions
    scene_descriptions: List[SceneDescription] = []
    
    # Generated videos
    scene_videos: List[SceneVideo] = []
    final_video_url: Optional[str] = None
