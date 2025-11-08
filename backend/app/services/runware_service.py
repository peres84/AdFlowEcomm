"""
Runware Service
Handles interactions with Runware API for image and video generation
"""

import os
import base64
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from runware import Runware, IImageInference
from app.models.session import GeneratedImage
from app.prompts.image_prompts import generate_image_prompt_for_scenario

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RunwareService:
    """Service for interacting with Runware API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Runware service.
        
        Args:
            api_key: Runware API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("RUNWARE_API_KEY")
        if not self.api_key:
            raise ValueError("RUNWARE_API_KEY not found in environment variables")
        
        self.runware = None
        self._connected = False
    
    async def connect(self):
        """Establish connection to Runware API"""
        if not self._connected:
            self.runware = Runware(api_key=self.api_key)
            await self.runware.connect()
            self._connected = True
            logger.info("Connected to Runware API")
    
    async def disconnect(self):
        """Close connection to Runware API"""
        if self._connected and self.runware:
            await self.runware.disconnect()
            self._connected = False
            logger.info("Disconnected from Runware API")
    
    async def upload_image(self, image_path: str) -> str:
        """
        Upload an image to Runware and return its UUID.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Image UUID from Runware
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If upload fails
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Ensure connection
        await self.connect()
        
        try:
            # Read and encode image as base64
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            logger.info(f"Uploading image to Runware: {image_path}")
            
            # Upload using Runware SDK
            result = await self.runware.imageUpload(
                image=base64_image
            )
            
            if not result or not hasattr(result, 'imageUUID'):
                raise Exception("Failed to get image UUID from Runware")
            
            image_uuid = result.imageUUID
            logger.info(f"Image uploaded successfully: {image_uuid}")
            
            return image_uuid
            
        except Exception as e:
            logger.error(f"Error uploading image to Runware: {str(e)}")
            raise Exception(f"Failed to upload image to Runware: {str(e)}")

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        model: str = "runware:100@1",
        steps: int = 20,
        number_results: int = 1
    ) -> List[str]:
        """
        Generate an image using Runware API.
        
        Args:
            prompt: Text prompt for image generation
            width: Image width in pixels (default: 1024)
            height: Image height in pixels (default: 1024)
            model: Model identifier (default: runware:100@1)
            steps: Number of inference steps (default: 20)
            number_results: Number of images to generate (default: 1)
            
        Returns:
            List[str]: List of image URLs
            
        Raises:
            Exception: If generation fails
        """
        # Ensure connection
        await self.connect()
        
        try:
            logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            # Create image inference request
            request = IImageInference(
                positivePrompt=prompt,
                width=width,
                height=height,
                model=model,
                steps=steps,
                numberResults=number_results,
                outputType="URL",
                outputFormat="PNG"
            )
            
            # Generate image using Runware SDK
            results = await self.runware.imageInference(requestImage=request)
            
            if not results:
                raise Exception("No results returned from Runware")
            
            # Extract image URLs
            image_urls = []
            for result in results:
                if hasattr(result, 'imageURL'):
                    image_urls.append(result.imageURL)
            
            if not image_urls:
                raise Exception("No image URLs in results")
            
            logger.info(f"Generated {len(image_urls)} image(s) successfully")
            return image_urls
            
        except Exception as e:
            logger.error(f"Error generating image with Runware: {str(e)}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    async def generate_images_for_scenarios(
        self,
        form_data: Dict[str, Any],
        product_analysis: Dict[str, Any],
        has_logo: bool = False,
        logo_image_uuid: Optional[str] = None
    ) -> List[GeneratedImage]:
        """
        Generate images for all four scenarios (hook, problem, solution, cta).
        
        Args:
            form_data: Dictionary containing all form data
            product_analysis: Dictionary containing product analysis results
            has_logo: Whether a logo was uploaded
            logo_image_uuid: UUID of uploaded logo (if has_logo is True)
            
        Returns:
            List[GeneratedImage]: List of generated images with metadata
            
        Raises:
            Exception: If generation fails
        """
        scenarios = ["hook", "problem", "solution", "cta"]
        generated_images = []
        
        # Ensure connection
        await self.connect()
        
        for scenario in scenarios:
            try:
                logger.info(f"Generating image for scenario: {scenario}")
                
                # Generate prompt for this scenario
                prompt = generate_image_prompt_for_scenario(
                    scenario=scenario,
                    form_data=form_data,
                    product_analysis=product_analysis,
                    has_logo=has_logo
                )
                
                # Generate image
                image_urls = await self.generate_image(
                    prompt=prompt,
                    width=1024,
                    height=1024,
                    number_results=1
                )
                
                if not image_urls:
                    logger.error(f"No image generated for scenario: {scenario}")
                    continue
                
                # Create GeneratedImage object
                generated_image = GeneratedImage(
                    id=str(uuid.uuid4()),
                    scenario=scenario,
                    use_case=f"{scenario.capitalize()} scene",
                    prompt=prompt,
                    image_url=image_urls[0],
                    has_logo=has_logo,
                    created_at=datetime.now()
                )
                
                generated_images.append(generated_image)
                logger.info(f"Successfully generated image for {scenario}: {generated_image.id}")
                
            except Exception as e:
                logger.error(f"Failed to generate image for scenario {scenario}: {str(e)}")
                # Continue with other scenarios even if one fails
                continue
        
        # Ensure we have at least 4 images (minimum requirement)
        if len(generated_images) < 4:
            raise Exception(
                f"Failed to generate minimum 4 images. Only generated {len(generated_images)} images."
            )
        
        logger.info(f"Successfully generated {len(generated_images)} images for all scenarios")
        return generated_images
    
    async def regenerate_image(
        self,
        scenario: str,
        original_prompt: str,
        prompt_modifications: str,
        has_logo: bool = False
    ) -> GeneratedImage:
        """
        Regenerate an image with modified prompt.
        
        Args:
            scenario: Scenario type (hook, problem, solution, cta)
            original_prompt: Original prompt used
            prompt_modifications: User's modifications to append
            has_logo: Whether logo integration is expected
            
        Returns:
            GeneratedImage: New generated image
            
        Raises:
            Exception: If generation fails
        """
        # Ensure connection
        await self.connect()
        
        try:
            # Combine original prompt with modifications
            if prompt_modifications:
                combined_prompt = f"{original_prompt}\n\nAdditional requirements: {prompt_modifications}"
            else:
                combined_prompt = original_prompt
            
            logger.info(f"Regenerating image for scenario: {scenario}")
            
            # Generate new image
            image_urls = await self.generate_image(
                prompt=combined_prompt,
                width=1024,
                height=1024,
                number_results=1
            )
            
            if not image_urls:
                raise Exception("No image generated")
            
            # Create GeneratedImage object
            generated_image = GeneratedImage(
                id=str(uuid.uuid4()),
                scenario=scenario,
                use_case=f"{scenario.capitalize()} scene (regenerated)",
                prompt=combined_prompt,
                image_url=image_urls[0],
                has_logo=has_logo,
                created_at=datetime.now()
            )
            
            logger.info(f"Successfully regenerated image for {scenario}: {generated_image.id}")
            return generated_image
            
        except Exception as e:
            logger.error(f"Failed to regenerate image for scenario {scenario}: {str(e)}")
            raise Exception(f"Failed to regenerate image: {str(e)}")


# Create a singleton instance
_runware_service = None


def get_runware_service() -> RunwareService:
    """
    Get or create the Runware service singleton.
    
    Returns:
        RunwareService: The Runware service instance
    """
    global _runware_service
    if _runware_service is None:
        _runware_service = RunwareService()
    return _runware_service
