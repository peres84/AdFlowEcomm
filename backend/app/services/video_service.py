"""
Video Generation Service
Handles parallel video generation using Runware SDK
"""

import os
import logging
import uuid
import asyncio
import aiofiles
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
from runware import Runware, IVideoInference
from app.models.session import SceneDescription, SceneVideo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoGenerationJob:
    """Represents a video generation job with multiple scenes"""
    
    def __init__(self, job_id: str, session_id: str):
        self.job_id = job_id
        self.session_id = session_id
        self.scenes: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()
    
    def add_scene(self, scenario: str):
        """Add a scene to track"""
        self.scenes[scenario] = {
            "status": "generating",
            "progress": 0,
            "video_url": None,
            "error": None
        }
    
    def update_scene(self, scenario: str, status: str, progress: int = 0, 
                     video_url: Optional[str] = None, error: Optional[str] = None):
        """Update scene status"""
        if scenario in self.scenes:
            self.scenes[scenario]["status"] = status
            self.scenes[scenario]["progress"] = progress
            if video_url:
                self.scenes[scenario]["video_url"] = video_url
            if error:
                self.scenes[scenario]["error"] = error
    
    def get_overall_status(self) -> str:
        """Get overall job status"""
        if not self.scenes:
            return "unknown"
        
        statuses = [scene["status"] for scene in self.scenes.values()]
        
        if all(s == "completed" for s in statuses):
            return "completed"
        elif all(s == "failed" for s in statuses):
            return "failed"
        elif any(s == "generating" for s in statuses):
            return "generating"
        else:
            return "partial"


class VideoService:
    """Service for parallel video generation using Runware SDK"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Video service.
        
        Args:
            api_key: Runware API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("RUNWARE_API_KEY")
        if not self.api_key:
            raise ValueError("RUNWARE_API_KEY not found in environment variables")
        
        self.runware = None
        self._connected = False
        self.jobs: Dict[str, VideoGenerationJob] = {}
        self.output_dir = os.getenv("OUTPUT_DIR", "outputs")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def connect(self):
        """Establish connection to Runware API"""
        if not self._connected:
            self.runware = Runware(api_key=self.api_key)
            await self.runware.connect()
            self._connected = True
            logger.info("Connected to Runware API for video generation")
    
    async def disconnect(self):
        """Close connection to Runware API"""
        if self._connected and self.runware:
            await self.runware.disconnect()
            self._connected = False
            logger.info("Disconnected from Runware API")
    
    async def download_video(self, video_url: str, output_path: str) -> bool:
        """
        Download video from URL to local file.
        
        Args:
            video_url: URL of the video to download
            output_path: Local path to save the video
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading video from {video_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(output_path, 'wb') as f:
                            await f.write(await response.read())
                        logger.info(f"Video downloaded successfully to {output_path}")
                        return True
                    else:
                        logger.error(f"Failed to download video: HTTP {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return False
    
    async def generate_single_video(
        self,
        scene_description: SceneDescription,
        job: VideoGenerationJob
    ) -> Optional[str]:
        """
        Generate a single video scene.
        
        Args:
            scene_description: Scene description with visual and audio details
            job: Video generation job for tracking progress
            
        Returns:
            Optional[str]: Local path to downloaded video, or None if failed
        """
        scenario = scene_description.scenario
        
        try:
            logger.info(f"Starting video generation for scenario: {scenario}")
            job.update_scene(scenario, "generating", 10)
            
            # Ensure connection
            await self.connect()
            
            # Create video inference request
            # Combine all scene elements into a comprehensive prompt
            visual_prompt = f"""{scene_description.visual_description}

Camera work: {scene_description.camera_work}
Lighting: {scene_description.lighting}

Audio design: {scene_description.audio_design}
Background music: {scene_description.background_music}
Sound effects: {scene_description.sound_effects}
Dialog/Narration: {scene_description.dialog_narration}"""
            
            request = IVideoInference(
                positivePrompt=visual_prompt,
                model="minimax:1@1",  # Using minimax model for video generation
                duration=scene_description.duration,
                width=1366,
                height=768
            )
            
            logger.info(f"Sending video generation request for {scenario}")
            job.update_scene(scenario, "generating", 30)
            
            # Generate video using Runware SDK
            # The SDK automatically handles polling and waiting for completion
            results = await self.runware.videoInference(requestVideo=request)
            
            if not results:
                raise Exception("No results returned from Runware")
            
            job.update_scene(scenario, "generating", 70)
            
            # Extract video URL
            video_url = None
            for result in results:
                if hasattr(result, 'videoURL'):
                    video_url = result.videoURL
                    break
            
            if not video_url:
                raise Exception("No video URL in results")
            
            logger.info(f"Video generated successfully for {scenario}: {video_url}")
            job.update_scene(scenario, "generating", 80)
            
            # Download video to local storage
            filename = f"{job.session_id}_{scenario}_{uuid.uuid4().hex[:8]}.mp4"
            output_path = os.path.join(self.output_dir, filename)
            
            download_success = await self.download_video(video_url, output_path)
            
            if not download_success:
                raise Exception("Failed to download video")
            
            # Return relative path for serving via static files
            relative_path = f"/outputs/{filename}"
            
            job.update_scene(scenario, "completed", 100, video_url=relative_path)
            logger.info(f"Video for {scenario} completed and saved to {output_path}")
            
            return relative_path
            
        except Exception as e:
            error_msg = f"Failed to generate video for {scenario}: {str(e)}"
            logger.error(error_msg)
            job.update_scene(scenario, "failed", 0, error=str(e))
            return None
    
    async def generate_videos_parallel(
        self,
        scene_descriptions: List[SceneDescription],
        session_id: str
    ) -> str:
        """
        Generate multiple video scenes in parallel.
        
        Args:
            scene_descriptions: List of scene descriptions to generate
            session_id: Session ID for tracking
            
        Returns:
            str: Job ID for tracking progress
        """
        # Create job
        job_id = str(uuid.uuid4())
        job = VideoGenerationJob(job_id, session_id)
        
        # Add all scenes to job
        for scene in scene_descriptions:
            job.add_scene(scene.scenario)
        
        # Store job
        self.jobs[job_id] = job
        
        logger.info(f"Starting parallel video generation for {len(scene_descriptions)} scenes")
        logger.info(f"Job ID: {job_id}")
        
        # Create tasks for parallel generation
        tasks = [
            self.generate_single_video(scene, job)
            for scene in scene_descriptions
        ]
        
        # Execute all tasks concurrently in background
        # We don't await here - let them run in background
        asyncio.create_task(self._execute_parallel_generation(tasks, job_id))
        
        return job_id
    
    async def _execute_parallel_generation(self, tasks: List, job_id: str):
        """
        Execute parallel generation tasks in background.
        
        Args:
            tasks: List of generation tasks
            job_id: Job ID for logging
        """
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"Parallel video generation completed for job {job_id}")
            
            # Log any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed with exception: {result}")
        except Exception as e:
            logger.error(f"Error in parallel video generation for job {job_id}: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Optional[VideoGenerationJob]:
        """
        Get status of a video generation job.
        
        Args:
            job_id: Job ID to query
            
        Returns:
            Optional[VideoGenerationJob]: Job object or None if not found
        """
        return self.jobs.get(job_id)
    
    async def regenerate_scene(
        self,
        scene_description: SceneDescription,
        session_id: str
    ) -> Optional[str]:
        """
        Regenerate a single video scene.
        
        Args:
            scene_description: Scene description to regenerate
            session_id: Session ID for file naming
            
        Returns:
            Optional[str]: Local path to downloaded video, or None if failed
        """
        # Create a temporary job for tracking
        job_id = str(uuid.uuid4())
        job = VideoGenerationJob(job_id, session_id)
        job.add_scene(scene_description.scenario)
        
        # Generate the video
        video_path = await self.generate_single_video(scene_description, job)
        
        return video_path
    
    def get_scene_videos_from_job(self, job_id: str) -> List[SceneVideo]:
        """
        Convert job results to SceneVideo models.
        
        Args:
            job_id: Job ID to convert
            
        Returns:
            List[SceneVideo]: List of scene videos
        """
        job = self.jobs.get(job_id)
        if not job:
            return []
        
        scene_videos = []
        for scenario, scene_data in job.scenes.items():
            if scene_data["status"] == "completed" and scene_data["video_url"]:
                scene_video = SceneVideo(
                    scenario=scenario,
                    video_url=scene_data["video_url"],
                    duration=0,  # Duration will be set from scene description
                    status="completed",
                    created_at=datetime.now()
                )
                scene_videos.append(scene_video)
        
        return scene_videos


# Create a singleton instance
_video_service = None


def get_video_service() -> VideoService:
    """
    Get or create the Video service singleton.
    
    Returns:
        VideoService: The Video service instance
    """
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
