"""
Prompts Package
Contains all prompt templates and generation functions for OpenAI and Runware APIs
"""

from .analysis_prompts import (
    get_product_analysis_prompt,
    get_selected_image_analysis_prompt,
    get_image_prompt_generation_request
)

from .image_prompts import (
    generate_hook_image_prompt,
    generate_problem_image_prompt,
    generate_solution_image_prompt,
    generate_cta_image_prompt,
    generate_image_prompt_for_scenario
)

from .scene_prompts import (
    get_scene_description_generation_prompt,
    get_scene_regeneration_prompt,
    extract_scene_prompt_for_video_generation
)

__all__ = [
    # Analysis prompts
    'get_product_analysis_prompt',
    'get_selected_image_analysis_prompt',
    'get_image_prompt_generation_request',
    
    # Image generation prompts
    'generate_hook_image_prompt',
    'generate_problem_image_prompt',
    'generate_solution_image_prompt',
    'generate_cta_image_prompt',
    'generate_image_prompt_for_scenario',
    
    # Scene description prompts
    'get_scene_description_generation_prompt',
    'get_scene_regeneration_prompt',
    'extract_scene_prompt_for_video_generation',
]
