"""
Scenes API Router
Handles scene description generation and regeneration endpoints
"""

from fastapi import APIRouter, status
from app.models.scene import (
    SceneDescriptionRequest,
    SceneRegenerateRequest,
    SceneDescriptionResponse,
    SceneDescriptionsResponse
)
from app.services import session_manager
from app.services.openai_service import (
    analyze_selected_images,
    generate_scene_descriptions
)
from app.models.session import SceneDescription
from app.core import (
    SessionNotFoundError,
    ValidationError,
    ExternalAPIError,
    log_error
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scenes", tags=["scenes"])


@router.post("/generate-descriptions", response_model=SceneDescriptionsResponse)
async def generate_descriptions(request: SceneDescriptionRequest):
    """
    Generate scene descriptions for all four scenarios based on selected images.
    
    This endpoint:
    1. Validates session and selected images
    2. Analyzes selected images using OpenAI Vision
    3. Generates detailed scene descriptions with audio/visual elements
    4. Stores scene descriptions in session
    
    Args:
        request: SceneDescriptionRequest with session_id and selected_images
        
    Returns:
        SceneDescriptionsResponse with list of scene descriptions
        
    Raises:
        HTTPException: 404 if session not found, 400 for missing data, 500 for generation errors
    """
    try:
        # Validate session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise SessionNotFoundError(request.session_id)
        
        # Validate selected images
        if not request.selected_images:
            raise ValidationError(
                message="No images selected",
                field="selected_images"
            )
        
        # Validate all four scenarios are present
        required_scenarios = ["hook", "problem", "solution", "cta"]
        for scenario in required_scenarios:
            if scenario not in request.selected_images:
                raise ValidationError(
                    message=f"Missing image selection for scenario: {scenario}",
                    field="selected_images"
                )
        
        # Validate required session data
        if not session.product_analysis:
            raise ValidationError(
                message="Product analysis not completed",
                field="product_analysis"
            )
        
        if not session.product_name:
            raise ValidationError(
                message="Form data not submitted",
                field="form_data"
            )
        
        logger.info(f"Starting scene description generation for session: {request.session_id}")
        
        # Store selected images in session
        session.selected_images = request.selected_images
        session_manager.update_session(request.session_id, session)
        
        # Analyze selected images
        logger.info("Analyzing selected images")
        try:
            selected_images_analysis = await analyze_selected_images(
                selected_images=request.selected_images,
                session_data=session
            )
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise ExternalAPIError(
                service="OpenAI Vision",
                message="Failed to analyze selected images",
                original_error=str(e)
            )
        
        # Prepare form data
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
        
        # Generate scene descriptions
        logger.info("Generating scene descriptions with OpenAI")
        try:
            scene_descriptions = await generate_scene_descriptions(
                form_data=form_data,
                product_analysis=session.product_analysis,
                selected_images_analysis=selected_images_analysis,
                has_logo=has_logo
            )
            
            # Convert to SceneDescription models and store in session
            scene_models = []
            for scene_dict in scene_descriptions:
                scene_model = SceneDescription(
                    scenario=scene_dict["scenario"],
                    duration=scene_dict["duration"],
                    visual_description=scene_dict["visual_description"],
                    camera_work=scene_dict["camera_work"],
                    lighting=scene_dict["lighting"],
                    audio_design=scene_dict["audio_design"],
                    background_music=scene_dict["background_music"],
                    sound_effects=scene_dict["sound_effects"],
                    dialog_narration=scene_dict["dialog_narration"],
                    selected_image_id=scene_dict["selected_image_id"]
                )
                scene_models.append(scene_model)
            
            session.scene_descriptions = scene_models
            session_manager.update_session(request.session_id, session)
            
            logger.info(f"Successfully generated {len(scene_models)} scene descriptions")
            
            # Convert to response format
            scene_responses = [
                SceneDescriptionResponse(
                    scenario=scene.scenario,
                    duration=scene.duration,
                    visual_description=scene.visual_description,
                    camera_work=scene.camera_work,
                    lighting=scene.lighting,
                    audio_design=scene.audio_design,
                    background_music=scene.background_music,
                    sound_effects=scene.sound_effects,
                    dialog_narration=scene.dialog_narration,
                    selected_image_id=scene.selected_image_id
                )
                for scene in scene_models
            ]
            
            return SceneDescriptionsResponse(
                success=True,
                message=f"Successfully generated {len(scene_responses)} scene descriptions",
                scenes=scene_responses
            )
            
        except Exception as e:
            logger.error(f"Scene description generation failed: {str(e)}")
            raise ExternalAPIError(
                service="OpenAI",
                message="Failed to generate scene descriptions",
                original_error=str(e)
            )
        
    except (SessionNotFoundError, ValidationError, ExternalAPIError):
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/scenes/generate-descriptions"},
            session_id=request.session_id
        )
        raise


@router.post("/regenerate-description", response_model=SceneDescriptionResponse)
async def regenerate_description(request: SceneRegenerateRequest):
    """
    Regenerate a single scene description based on user feedback.
    
    This endpoint allows users to regenerate a scene description for a specific
    scenario by providing feedback. The feedback is used to guide the regeneration.
    
    Args:
        request: SceneRegenerateRequest with session_id, scenario, and feedback
        
    Returns:
        SceneDescriptionResponse with the new scene description
        
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
        
        # Find original scene description
        original_scene = None
        for scene in session.scene_descriptions:
            if scene.scenario.lower() == request.scenario.lower():
                original_scene = scene
                break
        
        if not original_scene:
            raise ValidationError(
                message=f"No scene description found for scenario: {request.scenario}",
                field="scenario"
            )
        
        logger.info(f"Regenerating scene description for scenario: {request.scenario}")
        
        # Prepare form data
        form_data = {
            "product_name": session.product_name,
            "brand_tone": session.brand_tone,
            "scene_description": session.scene_description
        }
        
        # Generate regeneration prompt
        from app.prompts.scene_prompts import get_scene_regeneration_prompt
        from app.services.openai_service import openai_client
        
        prompt = get_scene_regeneration_prompt(
            original_scene_description=f"""
Visual: {original_scene.visual_description}
Camera: {original_scene.camera_work}
Lighting: {original_scene.lighting}
Audio: {original_scene.audio_design}
Music: {original_scene.background_music}
SFX: {original_scene.sound_effects}
Dialog: {original_scene.dialog_narration}
""",
            scenario=request.scenario,
            user_feedback=request.feedback,
            form_data=form_data
        )
        
        # Call OpenAI API
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            logger.info("Scene description regenerated successfully")
            
            # Parse the regenerated scene
            from app.services.openai_service import parse_scene_descriptions_response
            
            # Create a temporary analysis dict for parsing
            temp_analysis = {request.scenario: original_scene.selected_image_id}
            scenes = parse_scene_descriptions_response(content, temp_analysis)
            
            if not scenes:
                raise Exception("Failed to parse regenerated scene description")
            
            new_scene_dict = scenes[0]
            
            # Create new scene model
            new_scene = SceneDescription(
                scenario=new_scene_dict["scenario"],
                duration=new_scene_dict["duration"],
                visual_description=new_scene_dict["visual_description"],
                camera_work=new_scene_dict["camera_work"],
                lighting=new_scene_dict["lighting"],
                audio_design=new_scene_dict["audio_design"],
                background_music=new_scene_dict["background_music"],
                sound_effects=new_scene_dict["sound_effects"],
                dialog_narration=new_scene_dict["dialog_narration"],
                selected_image_id=original_scene.selected_image_id
            )
            
            # Update session with new scene description
            updated_scenes = []
            for scene in session.scene_descriptions:
                if scene.scenario.lower() == request.scenario.lower():
                    updated_scenes.append(new_scene)
                else:
                    updated_scenes.append(scene)
            
            session.scene_descriptions = updated_scenes
            session_manager.update_session(request.session_id, session)
            
            logger.info(f"Successfully regenerated scene description for {request.scenario}")
            
            return SceneDescriptionResponse(
                scenario=new_scene.scenario,
                duration=new_scene.duration,
                visual_description=new_scene.visual_description,
                camera_work=new_scene.camera_work,
                lighting=new_scene.lighting,
                audio_design=new_scene.audio_design,
                background_music=new_scene.background_music,
                sound_effects=new_scene.sound_effects,
                dialog_narration=new_scene.dialog_narration,
                selected_image_id=new_scene.selected_image_id
            )
            
        except Exception as e:
            logger.error(f"Scene regeneration failed: {str(e)}")
            raise ExternalAPIError(
                service="OpenAI",
                message="Failed to regenerate scene description",
                original_error=str(e)
            )
        
    except (SessionNotFoundError, ValidationError, ExternalAPIError):
        raise
    except Exception as e:
        log_error(
            e,
            context={"endpoint": "/api/scenes/regenerate-description", "scenario": request.scenario},
            session_id=request.session_id
        )
        raise
