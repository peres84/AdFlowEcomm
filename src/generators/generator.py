"""
Main generator module that combines Runware and Mirelo for complete asset generation.
"""

import os
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from .runware_client import RunwareClient
from .mirelo_client import MireloClient


class AssetGenerator:
    """
    Main class for generating images, videos, and audio using Runware and Mirelo.
    """
    
    def __init__(
        self,
        runware_api_key: str,
        mirelo_api_key: str,
        runware_image_model: str = "bfl:2@1",  # Default: Flux 1.1 Pro (user can override)
        runware_video_model: str = "klingai:6@1",  # Default for videos (user can override)
        output_dir: str = "output"
    ):
        """
        Initialize asset generator.
        
        Args:
            runware_api_key: Runware API key
            mirelo_api_key: Mirelo API key
            runware_image_model: Default Runware image model (default: "bfl:2@1" for Flux 1.1 Pro, user can override)
            runware_video_model: Default Runware video model (default: "klingai:6@1", user can override)
            output_dir: Directory to save generated files
        """
        self.runware = RunwareClient(runware_api_key)
        self.mirelo = MireloClient(mirelo_api_key)
        self.runware_image_model = runware_image_model
        self.runware_video_model = runware_video_model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _extract_last_frame(self, video_path: str) -> Optional[str]:
        """
        Extract the last frame from a video using FFmpeg.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted frame image, or None if failed
        """
        try:
            # Create temporary file for frame - always use PNG format for Runware compatibility
            frame_path = str(self.output_dir / f"last_frame_{os.path.basename(video_path).replace('.mp4', '')}.png")
            
            # Use FFmpeg to extract last frame
            # -ss -0.1 means go to 0.1 seconds before the end
            # -vframes 1 means extract 1 frame
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", "select=eq(n\\,$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 " + video_path + ")-1)",
                "-vframes", "1",
                "-y",  # Overwrite output file
                frame_path
            ]
            
            # Simpler approach: get video duration and extract frame near the end
            # First, get duration
            probe_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            
            result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            
            # Extract frame 0.1 seconds before the end and scale to 1920x1080
            # This ensures the frame matches video dimensions for Runware
            # Force PNG format for better compatibility with Runware
            extract_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(max(0, duration - 0.1)),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                "-vframes", "1",
                "-f", "image2",  # Force image format
                "-y",
                frame_path
            ]
            
            # Ensure output is PNG format
            if not frame_path.endswith('.png'):
                frame_path = frame_path.replace('.jpg', '.png').replace('.jpeg', '.png')
            
            subprocess.run(extract_cmd, capture_output=True, check=True)
            
            if os.path.exists(frame_path):
                return frame_path
            else:
                print(f"   ⚠️  Failed to extract last frame from {video_path}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  FFmpeg error extracting last frame: {e}")
            return None
        except Exception as e:
            print(f"   ⚠️  Error extracting last frame: {e}")
            return None
    
    def _generate_single_image(
        self,
        prompt_data: Dict[str, str],
        index: int,
        total: int,
        model: str,
        width: int,
        height: int,
        reference_images: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        Generate a single image (helper for parallel generation).
        
        Args:
            prompt_data: Dictionary with 'runware_prompt' and 'use_case'
            index: Image index (1-based)
            total: Total number of images
            model: Runware image model
            width: Image width
            height: Image height
            reference_images: Optional list of reference image UUIDs
            
        Returns:
            Dictionary with generated image information
        """
        prompt = prompt_data.get("runware_prompt", "")
        use_case = prompt_data.get("use_case", f"Image {index}")
        
        print(f"🔄 Generating image {index}/{total}: {use_case}")
        
        # Generate image with optional reference images
        result = self.runware.generate_image(
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            num_images=1,
            reference_images=reference_images
        )
        
        # Check if image is already ready or needs polling
        task_uuid = result.get("taskUUID")
        status = result.get("status")
        
        # If image is not ready yet, poll for completion
        if task_uuid and status != "completed" and not result.get("url") and not result.get("imageURL"):
            print(f"   ⏳ Waiting for image generation to complete...")
            result = self.runware.wait_for_completion(task_uuid, poll_interval=3, max_wait=300)
        elif result.get("url") or result.get("imageURL"):
            print(f"   ✅ Image ready immediately")
        
        # Download image if URL provided
        image_url = result.get("url") or result.get("imageURL") or result.get("image_url")
        if image_url:
            filename = f"image_{index}_{use_case.replace(' ', '_').lower()}.png"
            save_path = self.output_dir / filename
            self.runware.download_file(image_url, str(save_path))
            result["local_path"] = str(save_path)
            print(f"   ✅ Image saved: {save_path}")
        else:
            print(f"   ⚠️  No image URL in result: {result.keys()}")
        
        # Upload image to Runware to get UUID for video generation
        image_uuid = None
        if result.get("local_path"):
            try:
                print(f"   📤 Uploading image to Runware for video generation...")
                image_uuid = self.runware.upload_image(result["local_path"])
                print(f"   ✅ Image UUID: {image_uuid}")
            except Exception as e:
                print(f"   ⚠️  Failed to upload image for video generation: {e}")
        
        return {
            "use_case": use_case,
            "prompt": prompt,
            "result": result,
            "local_path": result.get("local_path"),
            "image_uuid": image_uuid,
            "index": index  # Preserve original order
        }
    
    def generate_images(
        self,
        prompts: List[Dict[str, str]],
        model: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        product_image_uuid: Optional[str] = None,
        logo_image_uuid: Optional[str] = None,
        use_reference_images: bool = True,
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate images from Runware prompts.
        Supports image-to-image generation with reference images (like scripts/testing_image).
        Can generate images in parallel for faster processing.
        
        Args:
            prompts: List of prompt dictionaries with 'runware_prompt' and 'use_case'
            model: Runware image model to use (default: self.runware_image_model)
            width: Image width (default: 1024)
            height: Image height (default: 1024)
            product_image_uuid: Optional product image UUID for referenceImages (image-to-image)
            logo_image_uuid: Optional logo image UUID for referenceImages (image-to-image)
            use_reference_images: Whether to use reference images if available (default: True)
            parallel: Whether to generate images in parallel (default: True)
            
        Returns:
            List of dictionaries with generated image information (in original order)
        """
        model = model or self.runware_image_model
        
        # Build reference images list
        # NOTE: Runware API only allows 1 reference image, not multiple
        reference_images = None
        if use_reference_images:
            # Prioritize product image, fallback to logo if product not available
            if product_image_uuid:
                reference_images = [product_image_uuid]
                print(f"🖼️  Using product image as reference for image-to-image generation")
            elif logo_image_uuid:
                reference_images = [logo_image_uuid]
                print(f"🖼️  Using logo as reference for image-to-image generation")
        
        if parallel and len(prompts) > 1:
            # Generate images in parallel using ThreadPoolExecutor
            print(f"🚀 Generating {len(prompts)} images in parallel...")
            results = []
            with ThreadPoolExecutor(max_workers=min(len(prompts), 4)) as executor:
                # Submit all tasks
                futures = {
                    executor.submit(
                        self._generate_single_image,
                        prompt_data,
                        i + 1,
                        len(prompts),
                        model,
                        width,
                        height,
                        reference_images
                    ): i
                    for i, prompt_data in enumerate(prompts)
                }
                
                # Collect results as they complete
                completed_results = {}
                for future in as_completed(futures):
                    original_index = futures[future]
                    try:
                        result = future.result()
                        completed_results[original_index] = result
                    except Exception as e:
                        print(f"   ❌ Error generating image {original_index + 1}: {e}")
                        completed_results[original_index] = None
                
                # Reorder results to match original prompt order
                results = [completed_results[i] for i in range(len(prompts)) if completed_results.get(i) is not None]
            
            return results
        else:
            # Sequential generation (original behavior)
            results = []
            for i, prompt_data in enumerate(prompts, 1):
                result = self._generate_single_image(
                    prompt_data,
                    i,
                    len(prompts),
                    model,
                    width,
                    height,
                    reference_images
                )
                results.append(result)
            
            return results
    
    def generate_video_scenes(
        self,
        scenes: List[Dict[str, Any]],
        generated_images: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        generate_audio: bool = True,
        use_last_frame: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate video scenes with audio using Runware and Mirelo.
        Videos are generated sequentially, with the last frame of each video
        used as the first frame of the next video (if use_last_frame=True).
        Audio generation can happen in parallel after videos are generated.
        
        Args:
            scenes: List of scene dictionaries with visual descriptions and audio design
            generated_images: Optional list of generated images with image_uuid for frameImages
            model: Runware video model to use (default: self.runware_video_model)
            width: Video width (default: 1920 for KlingAI)
            height: Video height (default: 1080 for KlingAI)
            generate_audio: Whether to generate audio with Mirelo (default: True)
            use_last_frame: Whether to use last frame of previous video as first frame of next (default: True)
            
        Returns:
            List of dictionaries with generated video scene information
        """
        model = model or self.runware_video_model
        results = []
        previous_video_path = None
        previous_frame_uuid = None
        
        for i, scene in enumerate(scenes, 1):
            scene_num = scene.get("scene_number", i)
            original_duration = scene.get("duration", 7)
            visual_desc = scene.get("visual_description", "")
            audio_design = scene.get("audio_design", {})
            
            # KlingAI only supports 5 or 10 seconds - adjust duration
            # For 25s video: Scene 1=5s, Scene 2=5s, Scene 3=10s, Scene 4=5s
            if model and "klingai" in model.lower():
                if original_duration <= 5:
                    duration = 5  # Keep 5s as 5s
                elif original_duration <= 10:
                    duration = 10  # Keep 10s as 10s
                else:
                    duration = 10  # Cap at 10
                if duration != original_duration:
                    print(f"   ⚠️  Adjusted duration from {original_duration}s to {duration}s (KlingAI requirement)")
            else:
                duration = original_duration
            
            print(f"🔄 Generating video scene {scene_num}/{len(scenes)} ({duration}s)")
            
            # Build video prompt from scene description
            video_prompt = self._build_video_prompt(scene)
            
            # Determine which image to use as first frame
            image_uuid = None
            
            # Priority 1: Use last frame of previous video (if use_last_frame=True)
            if use_last_frame and previous_frame_uuid:
                image_uuid = previous_frame_uuid
                print(f"   🖼️  Using last frame from previous video as first frame")
            # Priority 2: Use generated image matching this scene
            if not image_uuid and generated_images and len(generated_images) > 0:
                # Use modulo to cycle through images if more scenes than images
                image_index = (i - 1) % len(generated_images)
                matched_image = generated_images[image_index]
                image_uuid = matched_image.get("image_uuid")
                
                if image_uuid:
                    print(f"   🖼️  Using generated image {image_index + 1} as first frame")
                else:
                    print(f"   ⚠️  No image UUID available for scene {scene_num}, using text-only generation")
            
            # Generate video with optional image as first frame
            # If previous_frame_uuid fails, retry with generated image
            max_retries = 2
            retry_count = 0
            video_result = None
            
            while retry_count <= max_retries:
                try:
                    video_result = self.runware.generate_video(
                        prompt=video_prompt,
                        model=model,
                        duration=duration,
                        width=width,
                        height=height,
                        image_uuid=image_uuid
                    )
                    break  # Success, exit retry loop
                except Exception as e:
                    error_str = str(e)
                    # Check if it's a failedToTransferImage error (400)
                    if "failedToTransferImage" in error_str or ("400" in error_str and "failedToTransfer" in error_str):
                        retry_count += 1
                        # If using previous_frame_uuid failed, try with generated image instead
                        if image_uuid == previous_frame_uuid and generated_images and len(generated_images) > 0:
                            print(f"   ⚠️  Failed to use last frame (attempt {retry_count}/{max_retries}), trying generated image...")
                            image_index = (i - 1) % len(generated_images)
                            matched_image = generated_images[image_index]
                            fallback_uuid = matched_image.get("image_uuid")
                            if fallback_uuid:
                                image_uuid = fallback_uuid
                                print(f"   🖼️  Using generated image {image_index + 1} as first frame (fallback)")
                                continue  # Retry with fallback image
                        elif retry_count <= max_retries:
                            # Wait a bit longer and retry with same image
                            import time
                            wait_time = 2 * retry_count  # Exponential backoff: 2s, 4s
                            print(f"   ⏳ Image may not be ready yet, waiting {wait_time}s before retry {retry_count}/{max_retries}...")
                            time.sleep(wait_time)
                            continue
                    # If it's not a transfer error or we've exhausted retries, raise
                    if retry_count > max_retries:
                        raise
                    else:
                        retry_count += 1
            
            if video_result is None:
                raise Exception("Failed to generate video after all retries")
            
            # Handle async task - Runware always uses async for videos
            task_uuid = video_result.get("taskUUID")
            if task_uuid:
                print(f"   ⏳ Waiting for video generation to complete...")
                video_result = self.runware.wait_for_completion(task_uuid, poll_interval=5, max_wait=600)
            
            # Download video if URL provided
            video_url = (
                video_result.get("url") or 
                video_result.get("videoURL") or 
                video_result.get("video_url") or
                video_result.get("outputURL")
            )
            video_path = None
            if video_url:
                filename = f"scene_{scene_num}.mp4"
                save_path = self.output_dir / filename
                self.runware.download_file(video_url, str(save_path))
                video_path = str(save_path)
                print(f"   ✅ Video saved: {save_path}")
            else:
                print(f"   ⚠️  No video URL in result: {video_result.keys()}")
            
            # Extract last frame for next video (if use_last_frame=True and not last scene)
            if use_last_frame and video_path and i < len(scenes) - 1:
                print(f"   🎬 Extracting last frame for next video...")
                last_frame_path = self._extract_last_frame(video_path)
                if last_frame_path:
                    try:
                        previous_frame_uuid = self.runware.upload_image(last_frame_path)
                        print(f"   ✅ Last frame uploaded: {previous_frame_uuid}")
                        # Longer delay to ensure image is fully processed by Runware before use
                        # Runware needs time to process the uploaded image and make it accessible
                        import time
                        time.sleep(3)  # Increased from 1s to 3s for better reliability
                        # Clean up temporary frame file
                        try:
                            os.unlink(last_frame_path)
                        except:
                            pass
                    except Exception as e:
                        print(f"   ⚠️  Failed to upload last frame: {e}")
                        previous_frame_uuid = None
                else:
                    previous_frame_uuid = None
            
            previous_video_path = video_path
            
            # Store result (audio will be generated in parallel after all videos are done)
            results.append({
                "scene_number": scene_num,
                "duration": duration,
                "video_result": video_result,
                "video_path": video_path,
                "audio_design": audio_design,  # Store for later audio generation
                "audio_files": {}  # Will be populated after audio generation
            })
        
        # Generate audio in parallel after all videos are generated
        if generate_audio:
            print(f"\n🎵 Generating audio for {len(results)} videos in parallel...")
            with ThreadPoolExecutor(max_workers=min(len(results), 4)) as executor:
                futures = {
                    executor.submit(
                        self._generate_scene_audio_from_video,
                        result["video_path"],
                        result["audio_design"],
                        result["duration"]
                    ): i
                    for i, result in enumerate(results)
                    if result.get("video_path")
                }
                
                for future in as_completed(futures):
                    index = futures[future]
                    try:
                        audio_files = future.result()
                        results[index]["audio_files"] = audio_files
                    except Exception as e:
                        print(f"   ❌ Error generating audio for scene {results[index]['scene_number']}: {e}")
                        results[index]["audio_files"] = {}
            
            # Merge video and audio for each scene (like testing_mirelo.py)
            print(f"\n🎬 Merging video and audio for {len(results)} scenes...")
            for result in results:
                video_path = result.get("video_path")
                audio_files = result.get("audio_files", {})
                scene_num = result.get("scene_number", "?")
                
                # Get audio file path
                audio_path = audio_files.get("audio")
                
                if video_path and audio_path and os.path.exists(video_path) and os.path.exists(audio_path):
                    # Create output filename (like testing_mirelo.py)
                    video_basename = os.path.splitext(os.path.basename(video_path))[0]
                    output_filename = f"{video_basename}_with_audio.mp4"
                    output_path = str(self.output_dir / output_filename)
                    
                    print(f"   🎬 Merging scene {scene_num}...")
                    success = self.merge_video_audio(video_path, audio_path, output_path)
                    
                    if success:
                        result["final_video_path"] = output_path
                        print(f"   ✅ Scene {scene_num} merged: {output_filename}")
                    else:
                        print(f"   ⚠️  Failed to merge scene {scene_num}")
                else:
                    if not video_path:
                        print(f"   ⚠️  No video path for scene {scene_num}")
                    if not audio_path:
                        print(f"   ⚠️  No audio path for scene {scene_num}")
        
        return results
    
    def _build_video_prompt(self, scene: Dict[str, Any]) -> str:
        """
        Build comprehensive video prompt from scene description.
        
        Args:
            scene: Scene dictionary with all details
            
        Returns:
            Complete video generation prompt
        """
        parts = []
        
        # Visual description
        if scene.get("visual_description"):
            parts.append(f"Visual: {scene['visual_description']}")
        
        # Camera movement
        if scene.get("camera_movement"):
            parts.append(f"Camera: {scene['camera_movement']}")
        
        # Lighting & mood
        if scene.get("lighting_mood"):
            parts.append(f"Lighting: {scene['lighting_mood']}")
        
        # Image integration
        if scene.get("image_integration"):
            parts.append(f"Image: {scene['image_integration']}")
        
        return ". ".join(parts)
    
    def _generate_scene_audio_from_video(
        self,
        video_path: str,
        audio_design: Dict[str, str],
        duration: int
    ) -> Dict[str, str]:
        """
        Generate audio from video using Mirelo video-to-sfx (like testing_mirelo.py).
        
        Args:
            video_path: Path to generated video file
            audio_design: Dictionary with music, sfx, dialog descriptions
            duration: Duration in seconds
            
        Returns:
            Dictionary with paths to generated audio files
        """
        audio_files = {}
        
        try:
            # Build text prompt from audio_design (like testing_mirelo.py)
            # Combine music, sfx, and dialog descriptions
            prompt_parts = []
            if audio_design.get("music"):
                prompt_parts.append(f"Background music: {audio_design['music']}")
            if audio_design.get("sfx"):
                prompt_parts.append(f"Sound effects: {audio_design['sfx']}")
            if audio_design.get("dialog"):
                prompt_parts.append(f"Dialog/narration: {audio_design['dialog']}")
            
            text_prompt = ". ".join(prompt_parts) if prompt_parts else "Professional background music and sound effects that synchronize with the video"
            
            print(f"  🎵 Generating audio from video with Mirelo...")
            print(f"     Prompt: {text_prompt[:100]}...")
            
            # Step 1: Create customer asset (like testing_mirelo.py)
            customer_asset_id, upload_url = self.mirelo.create_customer_asset()
            
            # Step 2: Upload video
            self.mirelo.upload_video(upload_url, video_path)
            
            # Step 3: Generate SFX from video (like testing_mirelo.py)
            audio_urls = self.mirelo.generate_sfx_from_video(
                customer_asset_id=customer_asset_id,
                text_prompt=text_prompt,
                model_version="1.5",
                num_samples=1,
                duration=min(duration, 10),  # Max 10 seconds
                creativity_coef=5
            )
            
            # Step 4: Download audio
            if audio_urls:
                audio_url = audio_urls[0]  # Use first audio file
                filename = f"audio_{customer_asset_id}_scene.mp3"
                save_path = self.output_dir / filename
                self.mirelo.download_file(audio_url, str(save_path))
                audio_files["audio"] = str(save_path)
                print(f"  ✅ Audio saved: {save_path}")
            else:
                print(f"  ⚠️  No audio files generated")
        
        except Exception as e:
            print(f"  ⚠️  Failed to generate audio with Mirelo: {e}")
            import traceback
            traceback.print_exc()
        
        return audio_files
    
    def merge_video_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> bool:
        """
        Merge video and audio using FFmpeg (like testing_mirelo.py).
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path for output video with audio
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # FFmpeg command to merge video and audio (like testing_mirelo.py)
            cmd = [
                "ffmpeg",
                "-i", video_path,      # Input video
                "-i", audio_path,      # Input audio
                "-c:v", "copy",        # Copy video codec (no re-encoding)
                "-c:a", "aac",         # Convert audio to AAC
                "-map", "0:v:0",       # Map video from first input
                "-map", "1:a:0",       # Map audio from second input
                "-shortest",           # End when shortest stream ends
                "-y",                  # Overwrite output file
                output_path
            ]
            
            # Run FFmpeg
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ FFmpeg error: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"   ❌ FFmpeg not found. Please install FFmpeg:")
            print(f"      Windows: choco install ffmpeg")
            print(f"      Mac: brew install ffmpeg")
            print(f"      Linux: apt-get install ffmpeg")
            return False
        except Exception as e:
            print(f"   ❌ Merge failed: {str(e)}")
            return False
