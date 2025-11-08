"""
Scene Description Models
Models for video scene descriptions
"""

from pydantic import BaseModel
from typing import Optional


class SceneDescription(BaseModel):
    """Model for a video scene description"""
    scenario: str  # hook, problem, solution, cta
    duration: int  # seconds
    visual_description: str
    camera_work: str
    lighting: str
    audio_design: str
    background_music: str
    sound_effects: str
    dialog_narration: str
    selected_image_id: str


class SceneDescriptionRequest(BaseModel):
    """Request model for generating scene descriptions"""
    session_id: str
    selected_images: dict  # {scenario: image_id}


class SceneRegenerateRequest(BaseModel):
    """Request model for regenerating a scene description"""
    session_id: str
    scenario: str
    feedback: str


class SceneDescriptionResponse(BaseModel):
    """Response model for a single scene description"""
    scenario: str
    duration: int
    visual_description: str
    camera_work: str
    lighting: str
    audio_design: str
    background_music: str
    sound_effects: str
    dialog_narration: str
    selected_image_id: str


class SceneDescriptionsResponse(BaseModel):
    """Response model for scene descriptions generation"""
    success: bool
    message: str
    scenes: list[SceneDescriptionResponse]
