"""
Video Generation Helper Functions

Professional utilities for video generation workflows including:
- Image upload and management
- Video generation requests
- Task polling and status checking
- Video downloading
- FFmpeg stitching operations
"""

import requests
import uuid
import json
import os
import time
import base64
from typing import Dict, Optional, Tuple, List
from PIL import Image


class RunwareVideoHelper:
    """Helper class for Runware video generation operations."""
    
    def __init__(self, api_key: str, api_url: str = "https://api.runware.ai/v1"):
        """
        Initialize Runware helper.
        
        Args:
            api_key: Runware API key
            api_url: Runware API endpoint (default: production)
        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to Runware and return its UUID.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Image UUID from Runware
            
        Raises:
            Exception: If upload fails
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        payload = [{
            "taskType": "imageUpload",
            "taskUUID": str(uuid.uuid4()),
            "image": image_b64
        }]
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Image upload failed: {response.status_code}, {response.text}")
        
        data = response.json()
        data_list = data.get("results") or data.get("data") or []
        
        if not data_list or "imageUUID" not in data_list[0]:
            raise Exception(f"Unexpected upload response: {data}")
        
        return data_list[0]["imageUUID"]
    
    def generate_video(
        self,
        prompt: str,
        image_id: str,
        model: str = "minimax:1@1",
        duration: int = 6,
        width: int = 1366,
        height: int = 768,
        output_format: str = "MP4"
    ) -> Tuple[str, Dict]:
        """
        Submit a video generation request.
        
        Args:
            prompt: Text prompt describing the video
            image_id: UUID of uploaded image
            model: Model identifier (default: minimax:1@1)
            duration: Video duration in seconds
            width: Video width in pixels
            height: Video height in pixels
            output_format: Output format (MP4 or WEBM)
            
        Returns:
            Tuple[str, Dict]: (task_uuid, response_data)
            
        Raises:
            Exception: If request fails
        """
        task_uuid = str(uuid.uuid4())
        
        payload = [{
            "taskType": "videoInference",
            "taskUUID": task_uuid,
            "model": model,
            "positivePrompt": prompt,
            "duration": duration,
            "width": width,
            "height": height,
            "outputType": "URL",
            "outputFormat": output_format,
            "deliveryMethod": "async",
            "frameImages": [
                {"inputImage": image_id, "frame": "first"}
            ],
            "numberResults": 1
        }]
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Video request failed: {response.status_code}, {response.text}")
        
        data = response.json()
        
        # Verify acknowledgment
        if "data" not in data or not data["data"]:
            raise Exception(f"Unexpected response structure: {json.dumps(data, indent=2)}")
        
        task_data = data["data"][0]
        returned_uuid = task_data.get("taskUUID")
        returned_type = task_data.get("taskType")
        
        if returned_uuid != task_uuid:
            raise Exception(f"Task UUID mismatch! Sent: {task_uuid}, Received: {returned_uuid}")
        
        if returned_type != "videoInference":
            raise Exception(f"Unexpected task type: {returned_type}")
        
        return task_uuid, data
    
    def check_status(self, task_uuid: str) -> Dict:
        """
        Check the status of a video generation task.
        
        Args:
            task_uuid: UUID of the task to check
            
        Returns:
            Dict with status info:
            - status: "processing", "success", or "error"
            - data: Task data if available
            - error: Error info if failed
            
        Raises:
            Exception: If status check request fails
        """
        payload = [{
            "taskType": "getResponse",
            "taskUUID": task_uuid
        }]
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Status check failed: {response.status_code}, {response.text}")
        
        result = response.json()
        
        # Check errors array
        if "errors" in result and result["errors"]:
            for error in result["errors"]:
                if error.get("taskUUID") == task_uuid:
                    return {
                        "status": "error",
                        "error": error
                    }
        
        # Check data array
        if "data" in result and result["data"]:
            for item in result["data"]:
                if item.get("taskUUID") == task_uuid:
                    return item
        
        # No matching task found
        return {
            "status": "unknown",
            "message": "Task not found in response",
            "full_response": result
        }
    
    def poll_until_complete(
        self,
        task_uuid: str,
        poll_interval: int = 5,
        timeout: int = 600,
        verbose: bool = True
    ) -> Dict:
        """
        Poll a task until it completes or times out.
        
        Args:
            task_uuid: UUID of the task to poll
            poll_interval: Seconds between polls (default: 5)
            timeout: Maximum seconds to wait (default: 600 = 10 minutes)
            verbose: Print status updates (default: True)
            
        Returns:
            Dict: Final task data with status "success" or "error"
            
        Raises:
            TimeoutError: If task doesn't complete within timeout
        """
        start_time = time.time()
        poll_count = 0
        
        while True:
            time.sleep(poll_interval)
            poll_count += 1
            
            status_data = self.check_status(task_uuid)
            status = status_data.get("status")
            
            if verbose:
                elapsed = time.time() - start_time
                print(f"   Poll #{poll_count} ({elapsed:.0f}s): {status}")
            
            if status == "success":
                return status_data
            
            elif status == "error":
                return status_data
            
            elif status == "processing":
                # Check timeout
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Task timed out after {timeout}s")
                continue
            
            else:
                # Unknown status, continue polling but check timeout
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Task timed out after {timeout}s")
                continue
    
    def download_video(self, url: str, save_path: str) -> bool:
        """
        Download a video from URL to local file.
        
        Args:
            url: Video URL
            save_path: Local path to save video
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            return False
        except Exception as e:
            print(f"Download error: {str(e)}")
            return False


def resize_for_model(
    image_path: str,
    target_width: int,
    target_height: int,
    output_path: Optional[str] = None
) -> str:
    """
    Resize an image to model-specific dimensions.
    
    Args:
        image_path: Path to source image
        target_width: Required width
        target_height: Required height
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        str: Path to resized image
    """
    img = Image.open(image_path)
    img_resized = img.resize((target_width, target_height), Image.LANCZOS)
    
    if output_path is None:
        directory = os.path.dirname(image_path)
        output_path = os.path.join(directory, f"resized_{target_width}x{target_height}.jpeg")
    
    img_resized.save(output_path, format="JPEG", quality=95)
    return output_path


def stitch_videos_ffmpeg(
    video_paths: List[str],
    output_path: str,
    temp_dir: Optional[str] = None
) -> bool:
    """
    Stitch multiple videos together using FFmpeg concat demuxer.
    
    Args:
        video_paths: List of video file paths in order
        output_path: Path for final stitched video
        temp_dir: Directory for temporary concat file (default: same as output)
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> videos = ["scene1.mp4", "scene2.mp4", "scene3.mp4", "scene4.mp4"]
        >>> stitch_videos_ffmpeg(videos, "final.mp4")
    """
    import subprocess
    
    if temp_dir is None:
        temp_dir = os.path.dirname(output_path)
    
    # Create concat file
    concat_file = os.path.join(temp_dir, "concat_list.txt")
    
    try:
        with open(concat_file, "w") as f:
            for video_path in video_paths:
                # FFmpeg concat requires absolute paths or paths relative to concat file
                abs_path = os.path.abspath(video_path)
                f.write(f"file '{abs_path}'\n")
        
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
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up concat file
        if os.path.exists(concat_file):
            os.remove(concat_file)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"FFmpeg stitching error: {str(e)}")
        if os.path.exists(concat_file):
            os.remove(concat_file)
        return False


def get_video_info(video_path: str) -> Dict:
    """
    Get video metadata using FFprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dict with video info (duration, width, height, format, etc.)
    """
    import subprocess
    
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        
        return {}
        
    except Exception as e:
        print(f"FFprobe error: {str(e)}")
        return {}


# Model configurations for easy reference
MODEL_CONFIGS = {
    "minimax": {
        "model": "minimax:1@1",
        "duration": 6,
        "width": 1366,
        "height": 768,
        "description": "MiniMax 01 Base - Fastest (6s)"
    },
    "minimax_hailuo": {
        "model": "minimax:hailuo@2",
        "duration": 10,
        "width": 1366,
        "height": 768,
        "description": "MiniMax Hailuo 02 (10s)"
    },
    "klingai_standard": {
        "model": "klingai:3@2",
        "duration": 10,
        "width": 1280,
        "height": 720,
        "description": "KlingAI Standard (10s, HD)"
    },
    "pixverse": {
        "model": "pixverse:3.5@1",
        "duration": 5,
        "width": 1080,
        "height": 1080,
        "description": "PixVerse V3.5 (5s, square)"
    }
}
