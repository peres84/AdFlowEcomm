"""
Mirelo API Client for Audio/Music Generation.
Based on scripts/testing_audio/testing_mirelo.py
"""

import requests
import time
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class MireloClient:
    """
    Client for Mirelo API to generate audio/music.
    Uses the same API structure as testing_mirelo.py
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.mirelo.ai"):
        """
        Initialize Mirelo client.
        
        Args:
            api_key: Mirelo API key
            base_url: Base URL for Mirelo API (default: https://api.mirelo.ai)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key  # Mirelo uses x-api-key header (like testing_mirelo.py)
        }
    
    def create_customer_asset(self, content_type: str = "video/mp4") -> tuple:
        """
        Step 1: Create a customer asset and get upload URL (like testing_mirelo.py).
        
        Args:
            content_type: Content type (default: "video/mp4")
            
        Returns:
            tuple: (customer_asset_id, upload_url)
        """
        url = f"{self.base_url}/create-customer-asset"
        
        payload = {
            "contentType": content_type
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to create customer asset: {response.status_code}, {response.text}")
            
            data = response.json()
            customer_asset_id = data.get("customer_asset_id")
            upload_url = data.get("upload_url")
            
            if not customer_asset_id or not upload_url:
                raise Exception(f"Unexpected response: {data}")
            
            return customer_asset_id, upload_url
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mirelo create customer asset failed: {str(e)}")
    
    def upload_video(self, upload_url: str, video_path: str) -> bool:
        """
        Step 2: Upload video file to the pre-signed URL (like testing_mirelo.py).
        
        Args:
            upload_url: Pre-signed URL from create_customer_asset
            video_path: Path to local video file
            
        Returns:
            bool: True if successful
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        with open(video_path, "rb") as f:
            video_data = f.read()
        
        headers = {
            "Content-Type": "video/mp4"
        }
        
        try:
            response = requests.put(
                upload_url,
                data=video_data,
                headers=headers,
                timeout=300
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Upload failed: {response.status_code}, {response.text}")
            
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mirelo video upload failed: {str(e)}")
    
    def generate_sfx_from_video(
        self,
        customer_asset_id: str,
        text_prompt: str,
        model_version: str = "1.5",
        num_samples: int = 1,
        duration: int = 10,
        creativity_coef: int = 5
    ) -> List[str]:
        """
        Step 3: Generate sound effects from uploaded video (like testing_mirelo.py).
        
        Args:
            customer_asset_id: ID from create_customer_asset
            text_prompt: Text description for audio generation (from our prompts)
            model_version: Model version ("1.0" or "1.5", default: "1.5")
            num_samples: Number of audio variations (1-4, default: 1)
            duration: Duration in seconds (1-10, default: 10)
            creativity_coef: Creativity coefficient (1-10, default: 5)
        
        Returns:
            list: URLs to generated audio files
        """
        url = f"{self.base_url}/video-to-sfx"
        
        payload = {
            "customer_asset_id": customer_asset_id,
            "text_prompt": text_prompt,
            "model_version": model_version,
            "num_samples": num_samples,
            "duration": duration,
            "creativity_coef": creativity_coef,
            "return_audio_only": False
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=300
            )
            
            if response.status_code != 201:
                raise Exception(f"SFX generation failed: {response.status_code}, {response.text}")
            
            data = response.json()
            output_paths = data.get("output_paths", [])
            
            if not output_paths:
                raise Exception(f"No audio files generated: {data}")
            
            return output_paths
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mirelo SFX generation failed: {str(e)}")
    
    def generate_music(
        self,
        description: str,
        duration: int = 7,
        style: Optional[str] = None,
        tempo: Optional[int] = None,
        mood: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate background music using Mirelo API (legacy method, use generate_sfx_from_video for video-based).
        
        Args:
            description: Description of desired music (e.g., "upbeat modern electronic, 128 BPM, energetic")
            duration: Duration in seconds (default: 7)
            style: Music style (optional)
            tempo: BPM (optional)
            mood: Mood/emotion (optional)
            **kwargs: Additional parameters for Mirelo API
            
        Returns:
            Dictionary with music generation result
        """
        # For now, use the video-to-sfx endpoint if we have a video
        # This is a placeholder - actual implementation would need video upload
        raise NotImplementedError("Use generate_sfx_from_video with uploaded video instead")
    
    def generate_sound_effect(
        self,
        description: str,
        duration: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate sound effect using Mirelo API.
        
        Args:
            description: Description of desired sound effect (e.g., "subtle mechanical whir, satisfying click")
            duration: Duration in seconds (optional)
            **kwargs: Additional parameters for Mirelo API
            
        Returns:
            Dictionary with sound effect generation result
        """
        url = f"{self.base_url}/audio/sound-effects"
        
        payload = {
            "description": description,
            **kwargs
        }
        
        if duration:
            payload["duration"] = duration
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mirelo sound effect generation failed: {str(e)}")
    
    def generate_voice(
        self,
        text: str,
        voice_style: Optional[str] = None,
        speed: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate voice/narration using Mirelo API.
        
        Args:
            text: Text to convert to speech (dialog/narration)
            voice_style: Voice style (e.g., "natural", "professional", "energetic")
            speed: Speech speed (optional)
            **kwargs: Additional parameters for Mirelo API
            
        Returns:
            Dictionary with voice generation result
        """
        url = f"{self.base_url}/audio/voice"
        
        payload = {
            "text": text,
            **kwargs
        }
        
        if voice_style:
            payload["voice_style"] = voice_style
        if speed:
            payload["speed"] = speed
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mirelo voice generation failed: {str(e)}")
    
    def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check status of a generation task.
        
        Args:
            task_id: Task ID from generation request
            
        Returns:
            Dictionary with task status
        """
        url = f"{self.base_url}/tasks/{task_id}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to check task status: {str(e)}")
    
    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 3,
        max_wait: int = 300
    ) -> Dict[str, Any]:
        """
        Wait for a task to complete.
        
        Args:
            task_id: Task ID from generation request
            poll_interval: Seconds between status checks (default: 3)
            max_wait: Maximum seconds to wait (default: 300 = 5 minutes)
            
        Returns:
            Dictionary with completed task result
        """
        start_time = time.time()
        
        while True:
            status = self.check_task_status(task_id)
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                raise Exception(f"Task failed: {status.get('error', 'Unknown error')}")
            
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                raise Exception(f"Task timeout after {max_wait} seconds")
            
            time.sleep(poll_interval)
    
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
