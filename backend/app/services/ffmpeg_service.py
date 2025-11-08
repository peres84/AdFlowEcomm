"""
FFmpeg Service
Handles video merging operations using FFmpeg
"""

import os
import logging
import subprocess
import uuid
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FFmpegService:
    """Service for FFmpeg video operations"""
    
    def __init__(self):
        """Initialize FFmpeg service"""
        self.output_dir = os.getenv("OUTPUT_DIR", "outputs")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Verify FFmpeg is installed
        if not self.check_ffmpeg_installed():
            logger.warning("FFmpeg not found in PATH. Video merging will fail.")
    
    def check_ffmpeg_installed(self) -> bool:
        """
        Check if FFmpeg is installed and available.
        
        Returns:
            bool: True if FFmpeg is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.error(f"FFmpeg check failed: {str(e)}")
            return False
    
    def stitch_videos_ffmpeg(
        self,
        video_paths: List[str],
        output_path: str,
        temp_dir: Optional[str] = None
    ) -> bool:
        """
        Stitch multiple videos together using FFmpeg concat demuxer.
        
        This function uses FFmpeg's concat demuxer for lossless video merging
        without re-encoding. All input videos must have the same codec, resolution,
        and frame rate for best results.
        
        Args:
            video_paths: List of video file paths in order to merge
            output_path: Path for final stitched video
            temp_dir: Directory for temporary concat file (default: same as output)
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            >>> videos = ["scene1.mp4", "scene2.mp4", "scene3.mp4", "scene4.mp4"]
            >>> service.stitch_videos_ffmpeg(videos, "final.mp4")
        """
        if not video_paths:
            logger.error("No video paths provided for stitching")
            return False
        
        if len(video_paths) < 2:
            logger.warning("Only one video provided, copying instead of stitching")
            try:
                import shutil
                shutil.copy(video_paths[0], output_path)
                return True
            except Exception as e:
                logger.error(f"Failed to copy video: {str(e)}")
                return False
        
        if temp_dir is None:
            temp_dir = os.path.dirname(output_path)
        
        # Create concat file
        concat_file = os.path.join(temp_dir, f"concat_list_{uuid.uuid4().hex[:8]}.txt")
        
        try:
            logger.info(f"Creating concat file: {concat_file}")
            
            # Verify all input videos exist
            for video_path in video_paths:
                if not os.path.exists(video_path):
                    logger.error(f"Video file not found: {video_path}")
                    return False
            
            # Write concat file
            with open(concat_file, "w") as f:
                for video_path in video_paths:
                    # FFmpeg concat requires absolute paths or paths relative to concat file
                    abs_path = os.path.abspath(video_path)
                    # Escape single quotes in path for FFmpeg
                    escaped_path = abs_path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
            
            logger.info(f"Stitching {len(video_paths)} videos to {output_path}")
            
            # Run FFmpeg concat
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",  # No re-encoding (lossless)
                output_path,
                "-y"  # Overwrite output file
            ]
            
            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Clean up concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)
                logger.info(f"Cleaned up concat file: {concat_file}")
            
            if result.returncode == 0:
                logger.info(f"Successfully stitched videos to {output_path}")
                return True
            else:
                logger.error(f"FFmpeg failed with return code {result.returncode}")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                return False
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg stitching timed out after 5 minutes")
            if os.path.exists(concat_file):
                os.remove(concat_file)
            return False
        except Exception as e:
            logger.error(f"FFmpeg stitching error: {str(e)}")
            if os.path.exists(concat_file):
                os.remove(concat_file)
            return False
    
    def merge_scene_videos(
        self,
        scene_videos: List[dict],
        session_id: str
    ) -> Optional[str]:
        """
        Merge video scenes in the correct order (hook, problem, solution, cta).
        
        Args:
            scene_videos: List of scene video dictionaries with 'scenario' and 'video_url'
            session_id: Session ID for file naming
            
        Returns:
            Optional[str]: Relative path to merged video, or None if failed
        """
        try:
            # Define the correct order for scenes
            scene_order = ["hook", "problem", "solution", "cta"]
            
            # Create a mapping of scenario to video path
            video_map = {}
            for scene in scene_videos:
                scenario = scene.get("scenario", "").lower()
                video_url = scene.get("video_url", "")
                
                if scenario and video_url:
                    # Convert relative URL to absolute path
                    # video_url format: "/outputs/filename.mp4"
                    if video_url.startswith("/outputs/"):
                        filename = video_url.replace("/outputs/", "")
                        video_path = os.path.join(self.output_dir, filename)
                        video_map[scenario] = video_path
                    else:
                        logger.warning(f"Unexpected video URL format: {video_url}")
            
            # Validate we have all required scenes
            missing_scenes = [s for s in scene_order if s not in video_map]
            if missing_scenes:
                logger.error(f"Missing video scenes: {', '.join(missing_scenes)}")
                return None
            
            # Build ordered list of video paths
            video_paths = [video_map[scenario] for scenario in scene_order]
            
            # Verify all files exist
            for video_path in video_paths:
                if not os.path.exists(video_path):
                    logger.error(f"Video file not found: {video_path}")
                    return None
            
            logger.info(f"Merging {len(video_paths)} scene videos for session {session_id}")
            logger.info(f"Scene order: {' -> '.join(scene_order)}")
            
            # Generate output filename
            output_filename = f"{session_id}_final_{uuid.uuid4().hex[:8]}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Stitch videos
            success = self.stitch_videos_ffmpeg(video_paths, output_path)
            
            if success and os.path.exists(output_path):
                # Return relative path for serving via static files
                relative_path = f"/outputs/{output_filename}"
                logger.info(f"Successfully merged videos to {relative_path}")
                return relative_path
            else:
                logger.error("Video stitching failed")
                return None
            
        except Exception as e:
            logger.error(f"Error merging scene videos: {str(e)}")
            return None
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata using FFprobe.
        
        Args:
            video_path: Path to video file
            
        Returns:
            dict: Video info (duration, width, height, format, etc.)
        """
        try:
            import json
            
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            
            return {}
            
        except Exception as e:
            logger.error(f"FFprobe error: {str(e)}")
            return {}


# Create a singleton instance
_ffmpeg_service = None


def get_ffmpeg_service() -> FFmpegService:
    """
    Get or create the FFmpeg service singleton.
    
    Returns:
        FFmpegService: The FFmpeg service instance
    """
    global _ffmpeg_service
    if _ffmpeg_service is None:
        _ffmpeg_service = FFmpegService()
    return _ffmpeg_service
