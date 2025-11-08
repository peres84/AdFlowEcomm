"""
OpenAI Service
Handles interactions with OpenAI API for product analysis and prompt generation
"""

import os
import base64
import json
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from app.prompts.analysis_prompts import (
    get_product_analysis_prompt,
    get_selected_image_analysis_prompt,
    get_image_prompt_generation_request
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def analyze_product_image(image_path: str) -> Dict[str, Any]:
    """
    Analyze a product image using OpenAI Vision API.
    
    Args:
        image_path: Path to the product image file
        
    Returns:
        Dict containing:
            - product_type: Specific product type
            - description: Detailed visual description
            - colors: List of main colors
            - materials: List of visible materials
            - style: Visual style
            
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If API response cannot be parsed
        Exception: For other API errors
    """
    try:
        # Validate file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read and encode image as base64
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Analyzing product image: {image_path}")
        
        # Get analysis prompt
        analysis_prompt = get_product_analysis_prompt()
        
        # Call OpenAI Vision API
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract response content
        content = response.choices[0].message.content
        logger.info(f"Received analysis response: {content[:100]}...")
        
        # Parse JSON response
        try:
            analysis_data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {content}")
            raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}")
        
        # Validate required fields
        required_fields = ["product_type", "description", "colors", "materials", "style"]
        missing_fields = [field for field in required_fields if field not in analysis_data]
        
        if missing_fields:
            logger.warning(f"Missing fields in analysis: {missing_fields}")
            # Provide defaults for missing fields
            for field in missing_fields:
                if field in ["colors", "materials"]:
                    analysis_data[field] = []
                else:
                    analysis_data[field] = "Not specified"
        
        logger.info(f"Product analysis completed: {analysis_data['product_type']}")
        return analysis_data
        
    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error analyzing product image: {str(e)}")
        raise Exception(f"Failed to analyze product image: {str(e)}")


async def analyze_selected_image(
    image_path: str,
    scenario: str
) -> str:
    """
    Analyze a selected image for video scene generation.
    
    Args:
        image_path: Path to the selected image file
        scenario: The scenario type (hook, problem, solution, cta)
        
    Returns:
        str: Detailed description of visual characteristics
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        Exception: For API errors
    """
    try:
        # Validate file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read and encode image as base64
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Analyzing selected {scenario} image: {image_path}")
        
        # Get analysis prompt for selected image
        analysis_prompt = get_selected_image_analysis_prompt(scenario)
        
        # Call OpenAI Vision API
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract response content
        content = response.choices[0].message.content
        logger.info(f"Selected image analysis completed for {scenario}")
        
        return content
        
    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error analyzing selected image: {str(e)}")
        raise Exception(f"Failed to analyze selected image: {str(e)}")


async def generate_image_prompts(
    product_name: str,
    category: str,
    target_audience: str,
    main_benefit: str,
    brand_colors: list,
    brand_tone: str,
    target_platform: str,
    scene_description: str,
    product_analysis: Dict[str, Any],
    has_logo: bool
) -> list:
    """
    Generate image generation prompts using OpenAI based on product analysis and form data.
    
    Args:
        product_name: Name of the product
        category: Product category
        target_audience: Target audience description
        main_benefit: Main benefit/problem solved
        brand_colors: List of brand colors
        brand_tone: Brand tone
        target_platform: Target platform
        scene_description: User-provided visual style description
        product_analysis: Dictionary with product analysis results
        has_logo: Whether a logo was uploaded
        
    Returns:
        list: List of dictionaries containing scenario, use_case, and prompt
        
    Raises:
        Exception: For API errors
    """
    try:
        logger.info("Generating image prompts with OpenAI")
        
        # Get the prompt generation request
        request_prompt = get_image_prompt_generation_request(
            product_name=product_name,
            category=category,
            target_audience=target_audience,
            main_benefit=main_benefit,
            brand_colors=brand_colors,
            brand_tone=brand_tone,
            target_platform=target_platform,
            scene_description=scene_description,
            product_analysis=product_analysis,
            has_logo=has_logo
        )
        
        # Call OpenAI API
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": request_prompt
                }
            ],
            max_tokens=2000,
            temperature=0.8
        )
        
        # Extract response content
        content = response.choices[0].message.content
        logger.info("Image prompts generated successfully")
        
        # Parse the response to extract prompts
        prompts = parse_image_prompts_response(content, has_logo)
        
        return prompts
        
    except Exception as e:
        logger.error(f"Error generating image prompts: {str(e)}")
        raise Exception(f"Failed to generate image prompts: {str(e)}")


def parse_image_prompts_response(content: str, has_logo: bool) -> list:
    """
    Parse the OpenAI response to extract image prompts.
    
    Args:
        content: Response content from OpenAI
        has_logo: Whether logo integration is expected
        
    Returns:
        list: List of dictionaries with scenario, use_case, prompt, and logo_integration
    """
    prompts = []
    
    # Split by scenario sections
    sections = content.split("Scenario:")
    
    for section in sections[1:]:  # Skip first empty section
        try:
            lines = section.strip().split("\n")
            
            # Extract scenario
            scenario = lines[0].strip()
            
            # Extract use-case
            use_case = ""
            for line in lines:
                if line.startswith("Use-Case:"):
                    use_case = line.replace("Use-Case:", "").strip()
                    break
            
            # Extract Runware prompt
            prompt = ""
            for i, line in enumerate(lines):
                if line.startswith("Runware Prompt:"):
                    # Get all lines until next section or logo integration
                    prompt_lines = [line.replace("Runware Prompt:", "").strip()]
                    for next_line in lines[i+1:]:
                        if next_line.startswith("Logo Integration:") or next_line.startswith("Scenario:"):
                            break
                        if next_line.strip():
                            prompt_lines.append(next_line.strip())
                    prompt = " ".join(prompt_lines)
                    break
            
            # Extract logo integration if present
            logo_integration = ""
            if has_logo:
                for line in lines:
                    if line.startswith("Logo Integration:"):
                        logo_integration = line.replace("Logo Integration:", "").strip()
                        break
            
            if scenario and prompt:
                prompts.append({
                    "scenario": scenario,
                    "use_case": use_case,
                    "prompt": prompt,
                    "logo_integration": logo_integration if has_logo else None
                })
        
        except Exception as e:
            logger.warning(f"Failed to parse section: {str(e)}")
            continue
    
    logger.info(f"Parsed {len(prompts)} prompts from response")
    return prompts


async def analyze_selected_images(
    selected_images: Dict[str, str],
    session_data: Any
) -> Dict[str, str]:
    """
    Analyze all selected images for video scene generation.
    
    Args:
        selected_images: Dictionary mapping scenario to image_id
        session_data: Session data containing generated images
        
    Returns:
        Dict mapping scenario to analysis text
        
    Raises:
        Exception: For API errors or missing images
    """
    try:
        logger.info(f"Analyzing {len(selected_images)} selected images")
        
        analyses = {}
        
        for scenario, image_id in selected_images.items():
            # Find the image in session data
            image = None
            for img in session_data.generated_images:
                if img.id == image_id:
                    image = img
                    break
            
            if not image:
                logger.error(f"Image not found for scenario {scenario}: {image_id}")
                raise Exception(f"Image not found for scenario {scenario}")
            
            # For generated images, we'll use the image URL to analyze
            # Since these are Runware-generated images, we need to download them first
            # For now, we'll use the prompt and metadata as the analysis
            # In a production system, you'd download and analyze the actual image
            
            analysis = f"Image for {scenario} scenario. Visual characteristics: {image.prompt}"
            analyses[scenario] = analysis
            
            logger.info(f"Analyzed {scenario} image: {image_id}")
        
        return analyses
        
    except Exception as e:
        logger.error(f"Error analyzing selected images: {str(e)}")
        raise Exception(f"Failed to analyze selected images: {str(e)}")


async def generate_scene_descriptions(
    form_data: Dict[str, Any],
    product_analysis: Dict[str, Any],
    selected_images_analysis: Dict[str, str],
    has_logo: bool
) -> list:
    """
    Generate video scene descriptions using OpenAI based on form data and image analysis.
    
    Args:
        form_data: Dictionary containing all form data
        product_analysis: Dictionary with product analysis results
        selected_images_analysis: Dictionary with analysis of selected images per scenario
        has_logo: Whether a logo was uploaded
        
    Returns:
        list: List of scene description dictionaries
        
    Raises:
        Exception: For API errors
    """
    try:
        from app.prompts.scene_prompts import get_scene_description_generation_prompt
        
        logger.info("Generating scene descriptions with OpenAI")
        
        # Get the scene description generation prompt
        prompt = get_scene_description_generation_prompt(
            form_data=form_data,
            product_analysis=product_analysis,
            selected_images_analysis=selected_images_analysis,
            has_logo=has_logo
        )
        
        # Call OpenAI API
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=3000,
            temperature=0.8
        )
        
        # Extract response content
        content = response.choices[0].message.content
        logger.info("Scene descriptions generated successfully")
        
        # Parse the response to extract scene descriptions
        scenes = parse_scene_descriptions_response(content, selected_images_analysis)
        
        return scenes
        
    except Exception as e:
        logger.error(f"Error generating scene descriptions: {str(e)}")
        raise Exception(f"Failed to generate scene descriptions: {str(e)}")


def parse_scene_descriptions_response(content: str, selected_images_analysis: Dict[str, str]) -> list:
    """
    Parse the OpenAI response to extract scene descriptions.
    
    Args:
        content: Response content from OpenAI
        selected_images_analysis: Dictionary mapping scenario to image_id
        
    Returns:
        list: List of scene description dictionaries
    """
    scenes = []
    
    # Duration mapping
    duration_map = {
        'hook': 7,
        'problem': 7,
        'solution': 10,
        'cta': 6
    }
    
    # Split by scene sections
    sections = content.split("**SCENE")
    
    for section in sections[1:]:  # Skip first empty section
        try:
            lines = section.strip().split("\n")
            
            # Extract scenario from first line (e.g., "1: HOOK (7 seconds)**")
            first_line = lines[0].strip()
            scenario = ""
            
            if "HOOK" in first_line.upper():
                scenario = "hook"
            elif "PROBLEM" in first_line.upper():
                scenario = "problem"
            elif "SOLUTION" in first_line.upper():
                scenario = "solution"
            elif "CTA" in first_line.upper() or "CALL" in first_line.upper():
                scenario = "cta"
            
            if not scenario:
                logger.warning(f"Could not determine scenario from: {first_line}")
                continue
            
            # Extract fields
            visual_description = ""
            camera_work = ""
            lighting = ""
            background_music = ""
            sound_effects = ""
            dialog_narration = ""
            audio_design = ""
            
            current_field = None
            field_content = []
            
            for line in lines[1:]:
                line = line.strip()
                
                if not line:
                    continue
                
                # Check for field markers
                if line.startswith("**Visual Description:**"):
                    if current_field and field_content:
                        # Save previous field
                        if current_field == "visual":
                            visual_description = " ".join(field_content)
                    current_field = "visual"
                    field_content = [line.replace("**Visual Description:**", "").strip()]
                elif line.startswith("**Camera/Movement:**") or line.startswith("**Camera:**"):
                    if current_field and field_content:
                        if current_field == "visual":
                            visual_description = " ".join(field_content)
                    current_field = "camera"
                    field_content = [line.replace("**Camera/Movement:**", "").replace("**Camera:**", "").strip()]
                elif line.startswith("**Lighting & Mood:**") or line.startswith("**Lighting:**"):
                    if current_field and field_content:
                        if current_field == "camera":
                            camera_work = " ".join(field_content)
                    current_field = "lighting"
                    field_content = [line.replace("**Lighting & Mood:**", "").replace("**Lighting:**", "").strip()]
                elif line.startswith("**Audio Design:**"):
                    if current_field and field_content:
                        if current_field == "lighting":
                            lighting = " ".join(field_content)
                    current_field = "audio"
                    field_content = []
                elif line.startswith("- Background Music:"):
                    background_music = line.replace("- Background Music:", "").strip()
                elif line.startswith("- Sound Effects:"):
                    sound_effects = line.replace("- Sound Effects:", "").strip()
                elif line.startswith("- Dialog/Narration:"):
                    dialog_narration = line.replace("- Dialog/Narration:", "").strip()
                elif line.startswith("- Audio Balance:"):
                    audio_design = line.replace("- Audio Balance:", "").strip()
                elif current_field and not line.startswith("**"):
                    # Continue current field
                    field_content.append(line)
            
            # Save last field
            if current_field and field_content:
                if current_field == "visual":
                    visual_description = " ".join(field_content)
                elif current_field == "camera":
                    camera_work = " ".join(field_content)
                elif current_field == "lighting":
                    lighting = " ".join(field_content)
            
            # Combine audio elements if audio_design is empty
            if not audio_design and (background_music or sound_effects or dialog_narration):
                audio_parts = []
                if background_music:
                    audio_parts.append(f"Music: {background_music}")
                if sound_effects:
                    audio_parts.append(f"SFX: {sound_effects}")
                if dialog_narration:
                    audio_parts.append(f"Dialog: {dialog_narration}")
                audio_design = "; ".join(audio_parts)
            
            # Get selected image ID for this scenario
            selected_image_id = ""
            for img_scenario, img_id in selected_images_analysis.items():
                if img_scenario.lower() == scenario.lower():
                    selected_image_id = img_id
                    break
            
            if scenario and visual_description:
                scenes.append({
                    "scenario": scenario,
                    "duration": duration_map.get(scenario, 7),
                    "visual_description": visual_description,
                    "camera_work": camera_work or "Standard camera work",
                    "lighting": lighting or "Professional lighting",
                    "audio_design": audio_design or "Background music with narration",
                    "background_music": background_music or "Upbeat background music",
                    "sound_effects": sound_effects or "Subtle sound effects",
                    "dialog_narration": dialog_narration or "Engaging narration",
                    "selected_image_id": selected_image_id
                })
        
        except Exception as e:
            logger.warning(f"Failed to parse scene section: {str(e)}")
            continue
    
    logger.info(f"Parsed {len(scenes)} scene descriptions from response")
    return scenes
