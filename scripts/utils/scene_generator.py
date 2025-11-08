"""
Multi-Scene Video Generator

Handles the complete 4-scene video generation workflow:
1. Generate 4 separate video scenes
2. Stitch them together with FFmpeg
3. Produce final 30-second video

Scene structure:
- Scene 1: HOOK (7s)
- Scene 2: PROBLEM (7s)
- Scene 3: SOLUTION (10s)
- Scene 4: CTA (6s)
Total: 30 seconds
"""

import os
import time
from typing import List, Dict, Optional
from .video_helpers import RunwareVideoHelper, stitch_videos_ffmpeg, MODEL_CONFIGS


class SceneConfig:
    """Configuration for a single video scene."""
    
    def __init__(
        self,
        name: str,
        duration: int,
        prompt: str,
        image_id: str,
        description: str = ""
    ):
        self.name = name
        self.duration = duration
        self.prompt = prompt
        self.image_id = image_id
        self.description = description


class MultiSceneGenerator:
    """Generate and stitch multiple video scenes."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "minimax:1@1",
        output_dir: str = "results"
    ):
        """
        Initialize multi-scene generator.
        
        Args:
            api_key: Runware API key
            model: Video model to use (default: minimax:1@1)
            output_dir: Directory for output files
        """
        self.helper = RunwareVideoHelper(api_key)
        self.model = model
        self.output_dir = output_dir
        
        # Get model config
        model_key = self._get_model_key(model)
        self.config = MODEL_CONFIGS.get(model_key, MODEL_CONFIGS["minimax"])
        
        os.makedirs(output_dir, exist_ok=True)
    
    def _get_model_key(self, model: str) -> str:
        """Map model string to config key."""
        if "minimax" in model.lower():
            if "hailuo" in model.lower():
                return "minimax_hailuo"
            return "minimax"
        elif "klingai" in model.lower():
            return "klingai_standard"
        elif "pixverse" in model.lower():
            return "pixverse"
        return "minimax"
    
    def generate_scene(
        self,
        scene: SceneConfig,
        verbose: bool = True
    ) -> Optional[str]:
        """
        Generate a single video scene.
        
        Args:
            scene: Scene configuration
            verbose: Print progress updates
            
        Returns:
            str: Path to generated video file, or None if failed
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"🎬 Generating: {scene.name} ({scene.duration}s)")
            if scene.description:
                print(f"   {scene.description}")
            print(f"{'='*60}")
        
        try:
            # Submit video generation
            task_uuid, _ = self.helper.generate_video(
                prompt=scene.prompt,
                image_id=scene.image_id,
                model=self.model,
                duration=scene.duration,
                width=self.config['width'],
                height=self.config['height']
            )
            
            if verbose:
                print(f"✅ Request submitted (UUID: {task_uuid})")
                print(f"⏳ Waiting for completion...")
            
            # Poll until complete
            result = self.helper.poll_until_complete(
                task_uuid,
                poll_interval=5,
                timeout=600,
                verbose=verbose
            )
            
            # Handle result
            if result.get("status") == "success":
                video_url = result.get("videoURL")
                
                if video_url:
                    # Download video
                    filename = f"{scene.name.lower().replace(' ', '_')}.mp4"
                    save_path = os.path.join(self.output_dir, filename)
                    
                    if verbose:
                        print(f"⬇️  Downloading...")
                    
                    if self.helper.download_video(video_url, save_path):
                        if verbose:
                            print(f"✅ Scene saved: {save_path}")
                        return save_path
                    else:
                        if verbose:
                            print(f"❌ Download failed")
                        return None
            
            elif result.get("status") == "error":
                error = result.get("error", {})
                if verbose:
                    print(f"❌ Generation failed: {error.get('message', 'Unknown error')}")
                return None
            
        except Exception as e:
            if verbose:
                print(f"❌ Error: {str(e)}")
            return None
    
    def generate_all_scenes(
        self,
        scenes: List[SceneConfig],
        verbose: bool = True
    ) -> List[Optional[str]]:
        """
        Generate all scenes sequentially.
        
        Args:
            scenes: List of scene configurations
            verbose: Print progress updates
            
        Returns:
            List of video file paths (None for failed scenes)
        """
        video_paths = []
        
        if verbose:
            print(f"\n🎬 Starting multi-scene generation")
            print(f"   Model: {self.config['description']}")
            print(f"   Total scenes: {len(scenes)}")
            total_duration = sum(s.duration for s in scenes)
            print(f"   Total duration: {total_duration}s")
        
        start_time = time.time()
        
        for i, scene in enumerate(scenes, 1):
            if verbose:
                print(f"\n📍 Scene {i}/{len(scenes)}")
            
            video_path = self.generate_scene(scene, verbose=verbose)
            video_paths.append(video_path)
            
            if video_path is None and verbose:
                print(f"⚠️  Scene {i} failed, continuing...")
        
        elapsed = time.time() - start_time
        
        if verbose:
            successful = sum(1 for p in video_paths if p is not None)
            print(f"\n{'='*60}")
            print(f"📊 Generation Summary")
            print(f"   Successful: {successful}/{len(scenes)}")
            print(f"   Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
            print(f"{'='*60}")
        
        return video_paths
    
    def stitch_scenes(
        self,
        video_paths: List[str],
        output_filename: str = "final_video.mp4",
        verbose: bool = True
    ) -> Optional[str]:
        """
        Stitch multiple video scenes into final video.
        
        Args:
            video_paths: List of video file paths in order
            output_filename: Name for final video file
            verbose: Print progress updates
            
        Returns:
            str: Path to final stitched video, or None if failed
        """
        # Filter out None values
        valid_paths = [p for p in video_paths if p is not None]
        
        if not valid_paths:
            if verbose:
                print("❌ No valid videos to stitch")
            return None
        
        if len(valid_paths) < len(video_paths):
            if verbose:
                print(f"⚠️  Only {len(valid_paths)}/{len(video_paths)} scenes available for stitching")
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        if verbose:
            print(f"\n🔗 Stitching {len(valid_paths)} scenes...")
            print(f"   Output: {output_path}")
        
        success = stitch_videos_ffmpeg(valid_paths, output_path)
        
        if success:
            if verbose:
                print(f"✅ Final video created: {output_path}")
            return output_path
        else:
            if verbose:
                print(f"❌ Stitching failed")
            return None
    
    def generate_complete_video(
        self,
        scenes: List[SceneConfig],
        output_filename: str = "final_video.mp4",
        verbose: bool = True
    ) -> Optional[str]:
        """
        Complete workflow: Generate all scenes and stitch them.
        
        Args:
            scenes: List of scene configurations
            output_filename: Name for final video file
            verbose: Print progress updates
            
        Returns:
            str: Path to final video, or None if failed
        """
        # Generate all scenes
        video_paths = self.generate_all_scenes(scenes, verbose=verbose)
        
        # Stitch them together
        final_path = self.stitch_scenes(video_paths, output_filename, verbose=verbose)
        
        return final_path


def create_standard_scenes(
    product_name: str,
    benefit: str,
    image_id: str,
    scene_vibe: str = "professional, clean aesthetic"
) -> List[SceneConfig]:
    """
    Create standard 4-scene configuration for product video.
    
    Args:
        product_name: Name of the product
        benefit: Main product benefit
        image_id: Runware image UUID
        scene_vibe: Visual style description
        
    Returns:
        List of 4 SceneConfig objects
    """
    scenes = [
        SceneConfig(
            name="Scene 1 - Hook",
            duration=7,
            prompt=f"Opening shot of {product_name}. {scene_vibe}. Attention-grabbing, "
                   f"dynamic camera movement, professional lighting. Cinematic quality.",
            image_id=image_id,
            description="Capture attention, stop the scroll"
        ),
        SceneConfig(
            name="Scene 2 - Problem",
            duration=7,
            prompt=f"Problem scenario without {product_name}. {scene_vibe}. "
                   f"Showing frustration, struggle, unmet need. Relatable situation.",
            image_id=image_id,
            description="Identify pain point, create connection"
        ),
        SceneConfig(
            name="Scene 3 - Solution",
            duration=10,
            prompt=f"{product_name} solving the problem. {scene_vibe}. "
                   f"Demonstrating {benefit}. Multiple use cases, satisfaction visible. "
                   f"Transformation moment, professional quality.",
            image_id=image_id,
            description="Demonstrate benefits, show transformation"
        ),
        SceneConfig(
            name="Scene 4 - CTA",
            duration=6,
            prompt=f"Final hero shot of {product_name}. {scene_vibe}. "
                   f"Professional, premium presentation. Call-to-action moment. "
                   f"Confident, memorable brand close.",
            image_id=image_id,
            description="Drive action, memorable close"
        )
    ]
    
    return scenes
