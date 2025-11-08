"""
Video Generation Models
Models for video generation requests and responses
"""

from pydantic import BaseModel
from typing import List, Dict, Optional


class VideoGenerationRequest(BaseModel):
    """Request model for generating video scenes"""
    session_id: str


class VideoRegenerateRequest(BaseModel):
    """Request model for regenerating a single video scene"""
    session_id: str
    scenario: str


class VideoSceneStatus(BaseModel):
    """Status model for a single video scene"""
    scenario: str
    status: str  # generating, completed, failed
    progress: int  # 0-100
    video_url: Optional[str] = None
    error: Optional[str] = None


class VideoGenerationResponse(BaseModel):
    """Response model for video generation initiation"""
    success: bool
    message: str
    job_id: str


class VideoStatusResponse(BaseModel):
    """Response model for video generation status"""
    job_id: str
    overall_status: str  # generating, completed, failed, partial
    scenes: List[VideoSceneStatus]


class VideoMergeRequest(BaseModel):
    """Request model for merging video scenes"""
    session_id: str
    scene_videos: Dict[str, str]  # scenario -> video_url mapping


class VideoMergeResponse(BaseModel):
    """Response model for video merge operation"""
    success: bool
    message: str
    final_video_url: Optional[str] = None
    duration: Optional[int] = None  # Total duration in seconds
