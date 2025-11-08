"""
Main prompt generator module that ties everything together.
Provides a convenient API for generating and validating Runware prompts.
"""

from typing import Dict, List, Optional, Any
from openai import OpenAI

from .image_prompts import generate_runware_image_prompts
from .video_prompts import generate_runware_video_scenes
from .quality_assurance import generate_quality_report, validate_image_prompts, validate_video_scenes


class RunwarePromptGenerator:
    """
    Main class for generating Runware.ai optimized prompts.
    """
    
    def __init__(self, openai_api_key: str):
        """
        Initialize the prompt generator.
        
        Args:
            openai_api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=openai_api_key)
    
    def generate_image_prompts(
        self,
        product_data: Dict[str, Any],
        scene_description: str,
        product_image_path: str,
        logo_path: Optional[str] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate Runware image prompts with optional validation.
        
        Args:
            product_data: Dictionary with product information
            scene_description: User-provided visual style description
            product_image_path: Path to product image file
            logo_path: Optional path to logo image file
            validate: Whether to validate prompts after generation
            
        Returns:
            Dictionary with prompts and optional validation report
        """
        prompts = generate_runware_image_prompts(
            client=self.client,
            product_data=product_data,
            scene_description=scene_description,
            product_image_path=product_image_path,
            logo_path=logo_path
        )
        
        result = {
            "prompts": prompts,
            "count": len(prompts)
        }
        
        if validate:
            is_valid, validation_report = validate_image_prompts(prompts)
            result["validation"] = {
                "is_valid": is_valid,
                "report": validation_report
            }
        
        return result
    
    def generate_video_scenes(
        self,
        product_data: Dict[str, Any],
        scene_description: str,
        generated_images: List[Dict[str, str]],
        logo_info: Optional[Dict[str, Any]] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate Runware video scene descriptions with optional validation.
        
        Args:
            product_data: Dictionary with product information
            scene_description: User-provided visual style description
            generated_images: List of generated image descriptions
            logo_info: Optional logo information dictionary
            validate: Whether to validate scenes after generation
            
        Returns:
            Dictionary with scenes and optional validation report
        """
        scenes = generate_runware_video_scenes(
            client=self.client,
            product_data=product_data,
            scene_description=scene_description,
            generated_images=generated_images,
            logo_info=logo_info
        )
        
        result = {
            "scenes": scenes,
            "count": len(scenes),
            "total_duration": sum(s.get("duration", 0) for s in scenes)
        }
        
        if validate:
            is_valid, validation_report = validate_video_scenes(scenes)
            result["validation"] = {
                "is_valid": is_valid,
                "report": validation_report
            }
        
        return result
    
    def generate_complete_prompts(
        self,
        product_data: Dict[str, Any],
        scene_description: str,
        product_image_path: str,
        logo_path: Optional[str] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate both image prompts and video scenes in one call.
        
        Args:
            product_data: Dictionary with product information
            scene_description: User-provided visual style description
            product_image_path: Path to product image file
            logo_path: Optional path to logo image file
            validate: Whether to validate prompts after generation
            
        Returns:
            Dictionary with both image prompts and video scenes
        """
        # Step 1: Generate image prompts
        image_result = self.generate_image_prompts(
            product_data=product_data,
            scene_description=scene_description,
            product_image_path=product_image_path,
            logo_path=logo_path,
            validate=validate
        )
        
        # Step 2: Prepare logo info for video generation
        logo_info = None
        if logo_path:
            logo_info = {
                "description": "Logo available for integration",
                "integration_strategy": "Natural integration in video scenes"
            }
        
        # Step 3: Generate video scenes using generated images
        video_result = self.generate_video_scenes(
            product_data=product_data,
            scene_description=scene_description,
            generated_images=image_result["prompts"],
            logo_info=logo_info,
            validate=validate
        )
        
        # Step 4: Generate overall quality report
        quality_report = None
        if validate:
            quality_report = generate_quality_report(
                image_prompts=image_result["prompts"],
                video_scenes=video_result["scenes"]
            )
        
        return {
            "image_prompts": image_result,
            "video_scenes": video_result,
            "quality_report": quality_report,
            "overall_valid": quality_report["overall_valid"] if quality_report else None
        }
