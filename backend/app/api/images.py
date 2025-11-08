"""
Images API Router
Handles image generation and regeneration endpoints
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import List, Optional
from app.services import session_manager
from app.services.runware_service import get_runware_service
from app.services.openai_service import analyze_product_image
from app.core import (
    SessionNotFoundError,
    ValidationError,
    ImageGenerationError,
    ExternalAPIError,
    log_error
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/images", tags=["images"])


class ImageGenerateRequest(BaseModel):
    """Request model for image generation"""
    session_id: str


class ImageRegenerateRequest(BaseModel):
    """Request model for image regeneration"""
    session_id: str
    scenario: str
    prompt_modifications: Optional[str] = ""


class GeneratedImageResponse(BaseModel):
    """Response model for a single generated image"""
    id: str
    scenario: str
    use_case: str
    prompt: str
    image_url: str
    has_logo: bool


class ImageGenerateResponse(BaseModel):
    """Response model for image generation"""
    success: bool
    message: str
    images: List[GeneratedImageResponse]


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_images(request: ImageGenerateRequest):
    """
    Generate images for all four scenarios (hook, problem, solution, cta).
    
    This endpoint:
    1. Retrieves session data including form data and uploaded images
    2. Analyzes the product image using OpenAI Vision (if not already analyzed)
    3. Generates 4+ images using Runware API with scenario-specific prompts
    4. Stores generated images in the session
    
    Args:
        request: ImageGenerateRequest with session_id
        
    Returns:
        ImageGenerateResponse with list of generated images
        
    Raises:
        HTTPException: 404 if session not found, 400 for missing data, 500 for generation errors
    """
    try:
        # Validate session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise SessionNotFoundError(request.session_id)
        
        # Validate required data
        if not session.product_image_path:
            raise ValidationError(
                message="Product image not uploaded",
                field="product_image"
            )
        
        if not session.product_name:
            raise ValidationError(
                message="Form data not submitted",
                field="form_data"
            )
        
        logger.info(f"Starting image generation for session: {request.session_id}")
        
        # Analyze product image if not already done
        if not session.product_analysis:
            logger.info("Analyzing product image with OpenAI Vision")
            try:
                product_analysis = await analyze_product_image(session.product_image_path)
                session.product_analysis = product_analysis
                session_manager.update_session(request.session_id, session)
                logger.info("Product analysis completed")
            except Exception as e:
                logger.error(f"Product analysis failed: {str(e)}")
                raise ExternalAPIError(
                    service="OpenAI Vision",
                    message="Failed to analyze product image",
                    original_error=str(e)
                )
        else:
            logger.info("Using existing product analysis")
            product_analysis = session.product_analysis
        
        # Prepare form data for prompt generation
        form_data = {
            "product_name": session.product_name,
            "category": session.category,
            "target_audience": session.target_audience,
            "main_benefit": session.main_benefit,
            "brand_colors": session.brand_colors or [],
            "brand_tone": session.brand_tone,
            "target_platform": session.target_platform,
            "scene_description": session.scene_description,
            "website_url": session.website_url
        }
        
        # Check if logo was uploaded
        has_logo = bool(session.logo_image_path)
        logo_image_uuid = None
        
        # Upload logo to Runware if present (for future use in image generation)
        if has_logo:
            logger.info("Logo detected, will be integrated in prompts")
            # Note: Logo integration is handled via prompts, not direct image manipulation
            # The Runware API will incorporate logo based on prompt instructions
        
        # Generate images for all scenarios
        logger.info("Generating images with Runware API")
        runware_service = get_runware_service()
        
        try:
            generated_images = await runware_service.generate_images_for_scenarios(
                form_data=form_data,
                product_analysis=product_analysis,
                has_logo=has_logo,
                logo_image_uuid=logo_image_uuid
            )
            
            # Store generated images in session
            session.generated_images = generated_images
            session_manager.update_session(request.session_id, session)
            
            logger.info(f"Successfully generated {len(generated_images)} images")
            
            # Convert to response format
            image_responses = [
                GeneratedImageResponse(
                    id=img.id,
                    scenario=img.scenario,
                    use_case=img.use_case,
                    prompt=img.prompt,
                    image_url=img.image_url,
                    has_logo=img.has_logo
                )
                for img in generated_images
            ]
            
            return ImageGenerateResponse(
                success=True,
                message=f"Successfully generated {len(generated_images)} images",
                images=image_responses
            )
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise ImageGenerationError(
                message=str(e)
            )
        finally:
            # Disconnect from Runware
            await runware_service.disconnect()
        
    except (SessionNotFoundError, ValidationError, ImageGenerationError, ExternalAPIError):
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/images/generate"},
            session_id=request.session_id
        )
        raise


@router.post("/regenerate", response_model=GeneratedImageResponse)
async def regenerate_image(request: ImageRegenerateRequest):
    """
    Regenerate a single image with modified prompt.
    
    This endpoint allows users to regenerate an image for a specific scenario
    by providing modifications to the original prompt. The modifications are
    appended to the original prompt to create a new image.
    
    Args:
        request: ImageRegenerateRequest with session_id, scenario, and prompt_modifications
        
    Returns:
        GeneratedImageResponse with the new generated image
        
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
        
        # Find original image for this scenario
        original_image = None
        for img in session.generated_images:
            if img.scenario.lower() == request.scenario.lower():
                original_image = img
                break
        
        if not original_image:
            raise ValidationError(
                message=f"No image found for scenario: {request.scenario}",
                field="scenario"
            )
        
        logger.info(f"Regenerating image for scenario: {request.scenario}")
        
        # Regenerate image
        runware_service = get_runware_service()
        
        try:
            new_image = await runware_service.regenerate_image(
                scenario=request.scenario,
                original_prompt=original_image.prompt,
                prompt_modifications=request.prompt_modifications or "",
                has_logo=original_image.has_logo
            )
            
            # Update session with new image (replace old one)
            updated_images = []
            for img in session.generated_images:
                if img.scenario.lower() == request.scenario.lower():
                    updated_images.append(new_image)
                else:
                    updated_images.append(img)
            
            session.generated_images = updated_images
            session_manager.update_session(request.session_id, session)
            
            logger.info(f"Successfully regenerated image for {request.scenario}")
            
            return GeneratedImageResponse(
                id=new_image.id,
                scenario=new_image.scenario,
                use_case=new_image.use_case,
                prompt=new_image.prompt,
                image_url=new_image.image_url,
                has_logo=new_image.has_logo
            )
            
        except Exception as e:
            logger.error(f"Image regeneration failed: {str(e)}")
            raise ImageGenerationError(
                message=str(e),
                scenario=request.scenario
            )
        finally:
            # Disconnect from Runware
            await runware_service.disconnect()
        
    except (SessionNotFoundError, ValidationError, ImageGenerationError):
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/images/regenerate", "scenario": request.scenario},
            session_id=request.session_id
        )
        raise
