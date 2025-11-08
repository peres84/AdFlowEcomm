"""
Runware API Client for Image and Video Generation.
Supports flexible models with default: minimax:4@1

IMPORTANT: Runware API uses a specific structure:
- All requests go to base_url (not sub-endpoints)
- Payload MUST be an array: [{...}]
- Each request needs taskType and taskUUID
"""

import requests
import time
import uuid
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path


class RunwareClient:
    """
    Client for Runware.ai API to generate images and videos.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.runware.ai/v1"):
        """
        Initialize Runware client.
        
        Args:
            api_key: Runware API key
            base_url: Base URL for Runware API (default: https://api.runware.ai/v1)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(
        self,
        prompt: str,
        model: str = "bfl:2@1",  # Default: Flux 1.1 Pro (user can override)
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        reference_images: Optional[List[str]] = None,  # List of image UUIDs for image-to-image
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using Runware API.
        Supports both text-to-image and image-to-image (with referenceImages).
        
        Args:
            prompt: Image generation prompt
            model: Image model to use (default: "bfl:2@1" for Flux 1.1 Pro, user can override)
            width: Image width (default: 1024)
            height: Image height (default: 1024)
            num_images: Number of images to generate (default: 1)
            reference_images: Optional list of image UUIDs for image-to-image generation (like scripts/testing_image)
            negative_prompt: Optional negative prompt to exclude unwanted elements
            **kwargs: Additional parameters for Runware API
            
        Returns:
            Dictionary with image generation result including taskUUID
        """
        # Runware API uses base_url directly, not sub-endpoints
        url = self.base_url
        
        # Generate unique task UUID
        task_uuid = str(uuid.uuid4())
        
        # Build payload - similar to scripts/testing_image/dynamic_campaign.py
        payload_data = {
            "taskType": "imageInference",
            "taskUUID": task_uuid,
            "model": model,
            "positivePrompt": prompt,  # Runware uses positivePrompt, not prompt
            "width": width,
            "height": height,
            "numberResults": num_images,  # Runware uses numberResults, not num_images
            "outputType": "URL",  # Return image as URL
            **kwargs
        }
        
        # Add referenceImages if provided (for image-to-image, like in scripts)
        if reference_images:
            payload_data["referenceImages"] = reference_images
        
        # Add negativePrompt if provided
        if negative_prompt:
            payload_data["negativePrompt"] = negative_prompt
        
        payload = [payload_data]
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            # Zeige detaillierte Fehlerinformationen
            if not response.ok:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                
                print(f"❌ Runware API Error Details:")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {error_detail}")
                print(f"   Request Payload: {payload}")
                
            response.raise_for_status()
            result = response.json()
            
            # Extract data from response (can be in "data" or "results" key)
            data_list = result.get("data") or result.get("results") or []
            if data_list and len(data_list) > 0:
                task_data = data_list[0]
                
                # Check if image is already ready (like testing_runware_.py checks for videos)
                # Images might be returned immediately or need async polling
                image_url = (
                    task_data.get("imageURL") or 
                    task_data.get("imageUrl") or 
                    task_data.get("url") or
                    task_data.get("outputURL")
                )
                
                if image_url:
                    # Image is ready immediately - return it
                    return {
                        "taskUUID": task_data.get("taskUUID", task_uuid),
                        "taskType": task_data.get("taskType", "imageInference"),
                        "url": image_url,
                        "imageURL": image_url,
                        "status": "completed",
                        "response": result
                    }
                
                # Image not ready yet - return taskUUID for polling
                return {
                    "taskUUID": task_data.get("taskUUID", task_uuid),
                    "taskType": task_data.get("taskType", "imageInference"),
                    "status": "processing",
                    "response": result
                }
            
            return {"taskUUID": task_uuid, "status": "processing", "response": result}
            
        except requests.exceptions.RequestException as e:
            # Zeige mehr Details über den Fehler
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"❌ Runware API Error: {error_detail}")
                except:
                    print(f"❌ Runware API Error: {e.response.text}")
            raise Exception(f"Runware image generation failed: {str(e)}")
    
    def generate_video(
        self,
        prompt: str,
        model: str = "klingai:6@1",
        duration: int = 5,
        width: int = 1920,
        height: int = 1080,
        image_uuid: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using Runware API.
        
        Args:
            prompt: Video generation prompt (scene description)
            model: Model to use (default: "klingai:6@1")
            duration: Video duration in seconds (default: 5)
            width: Video width (default: 1920 for KlingAI)
            height: Video height (default: 1080 for KlingAI)
            image_uuid: Optional image UUID to use as first frame
            **kwargs: Additional parameters for Runware API
            
        Returns:
            Dictionary with video generation result including taskUUID
        """
        # Runware API uses base_url directly, not sub-endpoints
        url = self.base_url
        
        # Generate unique task UUID
        task_uuid = str(uuid.uuid4())
        
        # Build payload - MUST be an array (similar to testing_runware_.py)
        payload_data = {
            "taskType": "videoInference",
            "taskUUID": task_uuid,
            "model": model,
            "positivePrompt": prompt,  # Runware uses positivePrompt
            "duration": duration,
            "width": width,
            "height": height,
            "outputType": "URL",
            "outputFormat": "MP4",
            "deliveryMethod": "async",  # REQUIRED for video
            "numberResults": 1,
            **kwargs
        }
        
        # Add frameImages if image_uuid provided (exactly like testing_runware_.py)
        if image_uuid:
            payload_data["frameImages"] = [
                {
                    "inputImage": image_uuid,
                    "frame": "first"
                }
            ]
        
        payload = [payload_data]
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=300  # Videos take longer
            )
            
            # Zeige detaillierte Fehlerinformationen
            if not response.ok:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                
                print(f"❌ Runware API Error Details:")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {error_detail}")
                print(f"   Request Payload: {payload}")
                
            response.raise_for_status()
            result = response.json()
            
            # Extract data from response
            data_list = result.get("data") or result.get("results") or []
            if data_list and len(data_list) > 0:
                task_data = data_list[0]
                return {
                    "taskUUID": task_data.get("taskUUID", task_uuid),
                    "taskType": task_data.get("taskType", "videoInference"),
                    "response": result
                }
            
            return {"taskUUID": task_uuid, "response": result}
            
        except requests.exceptions.RequestException as e:
            # Zeige mehr Details über den Fehler
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"❌ Runware API Error: {error_detail}")
                except:
                    print(f"❌ Runware API Error: {e.response.text}")
            raise Exception(f"Runware video generation failed: {str(e)}")
    
    def check_task_status(self, task_uuid: str) -> Dict[str, Any]:
        """
        Check status of a generation task.
        
        Args:
            task_uuid: Task UUID from generation request
            
        Returns:
            Dictionary with task status
        """
        # Runware uses POST for status checks too, with taskUUID in payload
        url = self.base_url
        
        payload = [
            {
                "taskType": "getResponse",  # Runware uses getResponse for status checks
                "taskUUID": task_uuid
            }
        ]
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if not response.ok:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                print(f"⚠️  Status check error: {error_detail}")
            
            response.raise_for_status()
            result = response.json()
            
            # Check for errors array FIRST (Runware returns errors separately)
            if "errors" in result and result["errors"]:
                # Return error info but don't raise yet (let wait_for_completion handle it)
                return {
                    "status": "error",
                    "errors": result["errors"],
                    **result
                }
            
            # Extract data from response
            data_list = result.get("data") or result.get("results") or []
            if data_list and len(data_list) > 0:
                # Find task by UUID if multiple items
                for item in data_list:
                    if item.get("taskUUID") == task_uuid:
                        return item
                # Return first item if UUID not found
                return data_list[0]
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to check task status: {str(e)}")
    
    def wait_for_completion(
        self,
        task_uuid: str,
        poll_interval: int = 5,
        max_wait: int = 600
    ) -> Dict[str, Any]:
        """
        Wait for a task to complete.
        
        Args:
            task_uuid: Task UUID from generation request
            poll_interval: Seconds between status checks (default: 5)
            max_wait: Maximum seconds to wait (default: 600 = 10 minutes)
            
        Returns:
            Dictionary with completed task result including URLs
        """
        start_time = time.time()
        
        while True:
            status_result = self.check_task_status(task_uuid)
            
            # Runware returns data in "data" or "results" array, or directly
            # Also check for errors array
            if isinstance(status_result, dict):
                # Check for errors first
                if "errors" in status_result and status_result["errors"]:
                    for error in status_result["errors"]:
                        if error.get("taskUUID") == task_uuid:
                            error_msg = error.get("error") or error.get("message") or "Unknown error"
                            raise Exception(f"Task failed: {error_msg}")
                
                # Check data array
                data_list = status_result.get("data") or status_result.get("results") or []
                if data_list:
                    # Find our task in the data list
                    for item in data_list:
                        if item.get("taskUUID") == task_uuid:
                            status = item
                            break
                    else:
                        status = data_list[0] if data_list else status_result
                else:
                    status = status_result
            else:
                status = status_result
            
            # Check various status fields that Runware might use (like testing_runware_.py)
            task_status = (
                status.get("status") or 
                status.get("taskStatus") or 
                status.get("state") or
                status.get("taskState")
            )
            
            # Check if completed by looking for URLs (completed tasks have URLs)
            has_url = any(key in status for key in ["url", "imageURL", "videoURL", "outputURL", "imageUrl", "videoUrl"])
            
            # If status is "processing" or "pending", continue polling (like testing_runware_.py)
            if task_status in ["processing", "pending"]:
                # Still processing, continue polling
                elapsed = time.time() - start_time
                if elapsed > max_wait:
                    raise Exception(f"Task timeout after {max_wait} seconds")
                print(f"   ⏳ Status: {task_status}... ({int(elapsed)}s / {max_wait}s)")
                time.sleep(poll_interval)
                continue
            
            if task_status in ["completed", "success", "done"] or has_url:
                # Extract URLs from response
                result = {
                    "status": "completed",
                    "taskUUID": task_uuid,
                    **status
                }
                
                # Try to extract image/video URLs
                if "imageURL" in status or "imageUrl" in status:
                    result["url"] = status.get("imageURL") or status.get("imageUrl")
                elif "videoURL" in status or "videoUrl" in status:
                    result["url"] = status.get("videoURL") or status.get("videoUrl")
                elif "url" in status:
                    result["url"] = status["url"]
                elif "outputURL" in status or "outputUrl" in status:
                    result["url"] = status.get("outputURL") or status.get("outputUrl")
                
                return result
            elif task_status in ["failed", "error"]:
                error_msg = status.get("error") or status.get("errorMessage") or status.get("message") or "Unknown error"
                raise Exception(f"Task failed: {error_msg}")
            
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                raise Exception(f"Task timeout after {max_wait} seconds")
            
            # Show progress
            print(f"   ⏳ Waiting... ({int(elapsed)}s / {max_wait}s)")
            time.sleep(poll_interval)
    
    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to Runware and return its UUID.
        
        Args:
            image_path: Path to local image file
            
        Returns:
            Image UUID from Runware
            
        Raises:
            Exception: If upload fails
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read and encode image as base64
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        # Generate unique task UUID
        task_uuid = str(uuid.uuid4())
        
        # Payload MUST be an array
        payload = [
            {
                "taskType": "imageUpload",
                "taskUUID": task_uuid,
                "image": image_b64
            }
        ]
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if not response.ok:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                print(f"❌ Runware Image Upload Error: {error_detail}")
            
            response.raise_for_status()
            result = response.json()
            
            # Extract imageUUID from response
            data_list = result.get("data") or result.get("results") or []
            if not data_list or "imageUUID" not in data_list[0]:
                raise Exception(f"Unexpected upload response: {result}")
            
            image_uuid = data_list[0]["imageUUID"]
            return image_uuid
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload image: {str(e)}")
    
    def download_file(self, url: str, save_path: str) -> str:
        """
        Download a file from URL.
        
        Args:
            url: URL to download from
            save_path: Local path to save file
            
        Returns:
            Path to saved file
        """
        try:
            response = requests.get(url, timeout=120, stream=True)
            response.raise_for_status()
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return save_path
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download file: {str(e)}")
