"""
Videos API Router
Handles video generation and status tracking endpoints
"""

from fastapi import APIRouter, status
from app.models.video import (
    VideoGenerationRequest,
    VideoRegenerateRequest,
    VideoGenerationResponse,
    VideoStatusResponse,
    VideoSceneStatus,
    VideoMergeRequest,
    VideoMergeResponse
)
from app.services import session_manager
from app.services.video_service import get_video_service
from app.services.ffmpeg_service import get_ffmpeg_service
from app.models.session import SceneVideo
from app.core import (
    SessionNotFoundError,
    ValidationError,
    VideoGenerationError,
    FFmpegError,
    log_error
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/generate-scenes", response_model=VideoGenerationResponse)
async def generate_scenes(request: VideoGenerationRequest):
    """
    Generate video scenes in parallel for all approved scene descriptions.
    
    This endpoint:
    1. Validates session and scene descriptions
    2. Initiates parallel video generation for all scenes
    3. Returns a job ID for tracking progress
    
    The actual video generation happens asynchronously in the background.
    Use the /status/{job_id} endpoint to track progress.
    
    Args:
        request: VideoGenerationRequest with session_id
        
    Returns:
        VideoGenerationResponse with job_id for tracking
        
    Raises:
        HTTPException: 404 if session not found, 400 for missing data, 500 for generation errors
    """
    try:
        # Validate session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise SessionNotFoundError(request.session_id)
        
        # Validate scene descriptions exist
        if not session.scene_descriptions:
            raise ValidationError(
                message="No scene descriptions found. Generate scene descriptions first.",
                field="scene_descriptions"
            )
        
        # Validate we have all four required scenes
        required_scenarios = ["hook", "problem", "solution", "cta"]
        available_scenarios = [scene.scenario for scene in session.scene_descriptions]
        
        missing_scenarios = [s for s in required_scenarios if s not in available_scenarios]
        if missing_scenarios:
            raise ValidationError(
                message=f"Missing scene descriptions for: {', '.join(missing_scenarios)}",
                field="scene_descriptions"
            )
        
        logger.info(f"Starting parallel video generation for session: {request.session_id}")
        logger.info(f"Generating {len(session.scene_descriptions)} video scenes")
        
        # Get video service
        video_service = get_video_service()
        
        # Start parallel video generation
        try:
            job_id = await video_service.generate_videos_parallel(
                scene_descriptions=session.scene_descriptions,
                session_id=request.session_id
            )
            
            logger.info(f"Video generation job created: {job_id}")
            
            return VideoGenerationResponse(
                success=True,
                message=f"Video generation started for {len(session.scene_descriptions)} scenes",
                job_id=job_id
            )
            
        except Exception as e:
            logger.error(f"Failed to start video generation: {str(e)}")
            raise VideoGenerationError(
                message=str(e)
            )
        
    except (SessionNotFoundError, ValidationError, VideoGenerationError):
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/videos/generate-scenes"},
            session_id=request.session_id
        )
        raise


@router.get("/status/{job_id}", response_model=VideoStatusResponse)
async def get_video_status(job_id: str):
    """
    Get the status of a video generation job.
    
    This endpoint returns the current status of all video scenes being generated
    in a job. Poll this endpoint to track progress of parallel video generation.
    
    Args:
        job_id: Job ID returned from /generate-scenes endpoint
        
    Returns:
        VideoStatusResponse with overall status and individual scene statuses
        
    Raises:
        HTTPException: 404 if job not found
    """
    try:
        # Get video service
        video_service = get_video_service()
        
        # Get job status
        job = video_service.get_job_status(job_id)
        
        if not job:
            raise ValidationError(
                message="Job not found",
                field="job_id"
            )
        
        # Build scene status list
        scene_statuses = []
        for scenario, scene_data in job.scenes.items():
            scene_status = VideoSceneStatus(
                scenario=scenario,
                status=scene_data["status"],
                progress=scene_data["progress"],
                video_url=scene_data["video_url"],
                error=scene_data["error"]
            )
            scene_statuses.append(scene_status)
        
        # Get overall status
        overall_status = job.get_overall_status()
        
        # If job is completed, update session with video URLs
        if overall_status == "completed":
            try:
                session = session_manager.get_session(job.session_id)
                if session:
                    # Convert job results to SceneVideo models
                    scene_videos = video_service.get_scene_videos_from_job(job_id)
                    
                    # Update durations from scene descriptions
                    for scene_video in scene_videos:
                        for scene_desc in session.scene_descriptions:
                            if scene_desc.scenario == scene_video.scenario:
                                scene_video.duration = scene_desc.duration
                                break
                    
                    # Store in session
                    session.scene_videos = scene_videos
                    session_manager.update_session(job.session_id, session)
                    logger.info(f"Updated session {job.session_id} with {len(scene_videos)} completed videos")
            except Exception as e:
                logger.error(f"Failed to update session with video results: {str(e)}")
        
        return VideoStatusResponse(
            job_id=job_id,
            overall_status=overall_status,
            scenes=scene_statuses
        )
        
    except ValidationError:
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/videos/status", "job_id": job_id}
        )
        raise


@router.post("/regenerate-scene")
async def regenerate_scene(request: VideoRegenerateRequest):
    """
    Regenerate a single video scene.
    
    This endpoint regenerates a specific video scene using the existing
    scene description from the session.
    
    Args:
        request: VideoRegenerateRequest with session_id and scenario
        
    Returns:
        dict with new video URL
        
    Raises:
        HTTPException: 404 if session not found, 400 for invalid scenario, 500 for generation errors
    """
    try:
        # Validate session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise SessionNotFoundError(request.session_id)
        
        # Validate scenario
        valid_scenarios = ["hook", "problem", "solution", "cta"]
        if request.scenario.lower() not in valid_scenarios:
            raise ValidationError(
                message=f"Invalid scenario. Must be one of: {', '.join(valid_scenarios)}",
                field="scenario"
            )
        
        # Find scene description
        scene_description = None
        for scene in session.scene_descriptions:
            if scene.scenario.lower() == request.scenario.lower():
                scene_description = scene
                break
        
        if not scene_description:
            raise ValidationError(
                message=f"No scene description found for scenario: {request.scenario}",
                field="scenario"
            )
        
        logger.info(f"Regenerating video for scenario: {request.scenario}")
        
        # Get video service
        video_service = get_video_service()
        
        # Regenerate video
        try:
            video_path = await video_service.regenerate_scene(
                scene_description=scene_description,
                session_id=request.session_id
            )
            
            if not video_path:
                raise Exception("Video generation returned no result")
            
            # Update session with new video
            updated_videos = []
            video_found = False
            
            for scene_video in session.scene_videos:
                if scene_video.scenario.lower() == request.scenario.lower():
                    # Replace with new video
                    new_video = SceneVideo(
                        scenario=request.scenario,
                        video_url=video_path,
                        duration=scene_description.duration,
                        status="completed",
                        created_at=scene_video.created_at
                    )
                    updated_videos.append(new_video)
                    video_found = True
                else:
                    updated_videos.append(scene_video)
            
            # If video wasn't in list, add it
            if not video_found:
                new_video = SceneVideo(
                    scenario=request.scenario,
                    video_url=video_path,
                    duration=scene_description.duration,
                    status="completed",
                    created_at=session.created_at
                )
                updated_videos.append(new_video)
            
            session.scene_videos = updated_videos
            session_manager.update_session(request.session_id, session)
            
            logger.info(f"Successfully regenerated video for {request.scenario}")
            
            return {
                "success": True,
                "message": f"Video regenerated successfully for {request.scenario}",
                "video_url": video_path,
                "scenario": request.scenario
            }
            
        except Exception as e:
            logger.error(f"Video regeneration failed: {str(e)}")
            raise VideoGenerationError(
                message=str(e),
                scenario=request.scenario
            )
        
    except (SessionNotFoundError, ValidationError, VideoGenerationError):
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/videos/regenerate-scene", "scenario": request.scenario},
            session_id=request.session_id
        )
        raise



@router.post("/merge", response_model=VideoMergeResponse)
async def merge_videos(request: VideoMergeRequest):
    """
    Merge approved video scenes into a final 30-second video.
    
    This endpoint:
    1. Validates session and scene videos
    2. Merges videos in the correct order (hook, problem, solution, cta)
    3. Uses FFmpeg concat demuxer for lossless merging
    4. Stores final video in outputs/ directory
    5. Updates session with final video URL
    
    Args:
        request: VideoMergeRequest with session_id and scene_videos mapping
        
    Returns:
        VideoMergeResponse with final video URL and duration
        
    Raises:
        HTTPException: 404 if session not found, 400 for missing/invalid data, 500 for merge errors
    """
    try:
        # Validate session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise SessionNotFoundError(request.session_id)
        
        # Validate scene_videos provided
        if not request.scene_videos:
            raise ValidationError(
                message="No scene videos provided for merging",
                field="scene_videos"
            )
        
        # Validate all required scenarios are present
        required_scenarios = ["hook", "problem", "solution", "cta"]
        provided_scenarios = [s.lower() for s in request.scene_videos.keys()]
        
        missing_scenarios = [s for s in required_scenarios if s not in provided_scenarios]
        if missing_scenarios:
            raise ValidationError(
                message=f"Missing video scenes for: {', '.join(missing_scenarios)}",
                field="scene_videos"
            )
        
        logger.info(f"Starting video merge for session: {request.session_id}")
        logger.info(f"Merging {len(request.scene_videos)} video scenes")
        
        # Get FFmpeg service
        ffmpeg_service = get_ffmpeg_service()
        
        # Check FFmpeg availability
        if not ffmpeg_service.check_ffmpeg_installed():
            raise FFmpegError(
                message="FFmpeg is not installed or not available. Cannot merge videos."
            )
        
        # Prepare scene videos list for merging
        scene_videos_list = []
        total_duration = 0
        
        for scenario in required_scenarios:
            video_url = request.scene_videos.get(scenario)
            if video_url:
                scene_videos_list.append({
                    "scenario": scenario,
                    "video_url": video_url
                })
                
                # Get duration from session scene descriptions
                for scene_desc in session.scene_descriptions:
                    if scene_desc.scenario.lower() == scenario:
                        total_duration += scene_desc.duration
                        break
        
        logger.info(f"Total expected duration: {total_duration} seconds")
        
        # Merge videos
        try:
            final_video_url = ffmpeg_service.merge_scene_videos(
                scene_videos=scene_videos_list,
                session_id=request.session_id
            )
            
            if not final_video_url:
                raise Exception("Video merging returned no result")
            
            # Update session with final video URL
            session.final_video_url = final_video_url
            session_manager.update_session(request.session_id, session)
            
            logger.info(f"Successfully merged videos: {final_video_url}")
            
            return VideoMergeResponse(
                success=True,
                message="Videos merged successfully into final video",
                final_video_url=final_video_url,
                duration=total_duration
            )
            
        except Exception as e:
            logger.error(f"Video merge failed: {str(e)}")
            raise FFmpegError(
                message=str(e)
            )
        
    except (SessionNotFoundError, ValidationError, FFmpegError):
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/videos/merge"},
            session_id=request.session_id
        )
        raise
