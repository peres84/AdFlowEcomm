"""
Image Generation Prompts
Tested prompt templates from scripts/testing_image/dynamic_campaign.py
Functions to generate prompts with form data injection for Runware image generation
"""

from typing import Dict, Any, Optional


def generate_hook_image_prompt(
    product_name: str,
    product_type: str,
    product_description: str,
    scene_description: str,
    brand_colors: list,
    brand_tone: str,
    target_platform: str,
    has_logo: bool = False
) -> str:
    """
    Generate image prompt for HOOK scenario - attention grabber.
    
    Args:
        product_name: Name of the product
        product_type: Type of product (from analysis)
        product_description: Detailed visual description (from analysis)
        scene_description: User-provided visual style description
        brand_colors: List of brand colors
        brand_tone: Brand tone (Professional/Casual/Energetic/Luxury)
        target_platform: Target platform
        has_logo: Whether logo should be integrated
        
    Returns:
        str: Complete prompt for Runware image generation
    """
    brand_color_str = ', '.join(brand_colors) if brand_colors else 'brand colors'
    logo_instruction = """
Seamlessly place the provided logo onto the product surface, aligned with perspective and curvature.
Make the branding look realistically printed or embossed with correct reflections, texture, and lighting.
""" if has_logo else ""
    
    prompt = f"""Professional product photography featuring ONLY the {product_name}.

Product to showcase: {product_description}

IMPORTANT: Focus exclusively on THIS specific product - the {product_type}.
Do not add other products, accessories, or unrelated items.

{logo_instruction}

Visual style: {scene_description}
Brand colors: Subtly integrate {brand_color_str} in the scene

The product is the sole hero - clearly visible, beautifully presented, nothing else competing for attention.
Clean composition focusing on the product's design and branding.
Commercial quality ready for {target_platform}.
{brand_tone} tone.
Do not distort product shape or obscure details."""
    
    return prompt


def generate_problem_image_prompt(
    product_name: str,
    product_type: str,
    product_description: str,
    main_benefit: str,
    scene_description: str,
    brand_colors: list,
    brand_tone: str,
    target_platform: str,
    has_logo: bool = False
) -> str:
    """
    Generate image prompt for PROBLEM scenario - showing the pain point.
    
    Args:
        product_name: Name of the product
        product_type: Type of product (from analysis)
        product_description: Detailed visual description (from analysis)
        main_benefit: Main benefit/problem being solved
        scene_description: User-provided visual style description
        brand_colors: List of brand colors
        brand_tone: Brand tone
        target_platform: Target platform
        has_logo: Whether logo should be integrated
        
    Returns:
        str: Complete prompt for Runware image generation
    """
    brand_color_str = ', '.join(brand_colors) if brand_colors else 'brand colors'
    logo_instruction = """
The logo can appear subtly in the background or on related items, but should not be the focus.
""" if has_logo else ""
    
    prompt = f"""Lifestyle scene showing the problem or pain point that {product_name} solves.

Context: The problem being addressed is related to {main_benefit}

SCENE COMPOSITION:
Show a realistic scenario where the problem is evident.
The scene should convey frustration, inconvenience, or the need for a solution.
Can show the product in context or the situation before the product is used.

Product details: {product_description}
Visual style: {scene_description}
Brand colors: Subtly integrate {brand_color_str} in the scene

{logo_instruction}

Authentic {brand_tone.lower()} tone with genuine emotions.
Professional lifestyle photography quality for {target_platform}.
The scene should make viewers recognize the problem and desire a solution."""
    
    return prompt


def generate_solution_image_prompt(
    product_name: str,
    product_type: str,
    product_description: str,
    target_audience: str,
    main_benefit: str,
    scene_description: str,
    brand_colors: list,
    brand_tone: str,
    target_platform: str,
    has_logo: bool = False
) -> str:
    """
    Generate image prompt for SOLUTION scenario - product in action.
    
    Args:
        product_name: Name of the product
        product_type: Type of product (from analysis)
        product_description: Detailed visual description (from analysis)
        target_audience: Target audience description
        main_benefit: Main benefit being demonstrated
        scene_description: User-provided visual style description
        brand_colors: List of brand colors
        brand_tone: Brand tone
        target_platform: Target platform
        has_logo: Whether logo should be integrated
        
    Returns:
        str: Complete prompt for Runware image generation
    """
    brand_color_str = ', '.join(brand_colors) if brand_colors else 'brand colors'
    
    # Extract environment from scene description or use default
    environment = 'real-world setting'
    if 'office' in scene_description.lower():
        environment = 'office environment'
    elif 'home' in scene_description.lower():
        environment = 'home environment'
    elif 'outdoor' in scene_description.lower():
        environment = 'outdoor setting'
    
    logo_instruction = """
CRITICAL BRANDING REQUIREMENT:
Take the provided logo image and seamlessly place it onto the {product_type} surface.
The logo MUST be clearly visible on the product, aligned with its perspective and curvature.
Make the logo look realistically printed or embossed with correct reflections, shadows, texture, and lighting.
The branding should appear as if it was professionally manufactured onto the product.
""" if has_logo else ""
    
    prompt = f"""Lifestyle scene showing a person using {product_name} in real-world setting.

{logo_instruction}

SCENE COMPOSITION:
Show a real person (target audience: {target_audience}) relaxed and happy, doing other activities.
Person reading, relaxing, working, or enjoying free time.
The {product_type} works effectively, demonstrating the benefit.

Product details: {product_description}
Setting: {environment}
Benefit being demonstrated: {main_benefit}

Visual style: {scene_description}
Brand colors: Subtly integrate {brand_color_str} in the scene

Authentic {brand_tone.lower()} tone with genuine emotions.
The product should be clearly visible{"with the logo prominently displayed" if has_logo else ""}.
Professional lifestyle photography quality for {target_platform}."""
    
    return prompt


def generate_cta_image_prompt(
    product_name: str,
    product_type: str,
    product_description: str,
    scene_description: str,
    brand_colors: list,
    brand_tone: str,
    target_platform: str,
    has_logo: bool = False
) -> str:
    """
    Generate image prompt for CTA (Call-to-Action) scenario - hero product shot.
    
    Args:
        product_name: Name of the product
        product_type: Type of product (from analysis)
        product_description: Detailed visual description (from analysis)
        scene_description: User-provided visual style description
        brand_colors: List of brand colors
        brand_tone: Brand tone
        target_platform: Target platform
        has_logo: Whether logo should be integrated
        
    Returns:
        str: Complete prompt for Runware image generation
    """
    brand_color_str = ', '.join(brand_colors) if brand_colors else 'brand colors'
    
    logo_instruction = """
CRITICAL BRANDING REQUIREMENT - HIGHEST PRIORITY:
Take the provided logo image and place it PROMINENTLY and CLEARLY onto the {product_type} surface.
The logo MUST be the most visible branding element, aligned perfectly with the product's perspective and curvature.
Make the logo look realistically printed or embossed with perfect reflections, shadows, texture, and lighting.
The branding should appear professionally manufactured, sharp, and crystal clear.
This is a marketing hero shot - the logo visibility is ESSENTIAL.
""" if has_logo else ""
    
    prompt = f"""Hero product shot featuring ONLY the {product_name} for call-to-action.

{logo_instruction}

PRODUCT FOCUS:
Show exclusively THIS product: {product_description}
No other products, no accessories, no additional items.
Just the product as the sole focus.

Visual style: {scene_description}
Brand colors: Prominently integrate {brand_color_str} in the scene

Clean, impactful presentation with the product as the absolute hero.
{"The logo should be large enough to read clearly and positioned prominently." if has_logo else ""}
Premium {brand_tone.lower()} aesthetic.
Perfect for final frame of {target_platform} ad - drives viewers to take action.
Commercial quality, marketing-ready, professional product photography{"with clear branding" if has_logo else ""}."""
    
    return prompt


def generate_image_prompt_for_scenario(
    scenario: str,
    form_data: Dict[str, Any],
    product_analysis: Dict[str, Any],
    has_logo: bool = False
) -> str:
    """
    Generate image prompt for a specific scenario using form data and product analysis.
    
    Args:
        scenario: Scenario type (hook, problem, solution, cta)
        form_data: Dictionary containing all form data
        product_analysis: Dictionary containing product analysis results
        has_logo: Whether logo should be integrated
        
    Returns:
        str: Complete prompt for Runware image generation
    """
    # Extract common data
    product_name = form_data.get('product_name', 'product')
    product_type = product_analysis.get('product_type', 'product')
    product_description = product_analysis.get('description', 'product')
    scene_description = form_data.get('scene_description', 'professional setting')
    brand_colors = form_data.get('brand_colors', [])
    brand_tone = form_data.get('brand_tone', 'Professional')
    target_platform = form_data.get('target_platform', 'social media')
    
    # Generate prompt based on scenario
    if scenario.lower() == 'hook':
        return generate_hook_image_prompt(
            product_name=product_name,
            product_type=product_type,
            product_description=product_description,
            scene_description=scene_description,
            brand_colors=brand_colors,
            brand_tone=brand_tone,
            target_platform=target_platform,
            has_logo=has_logo
        )
    
    elif scenario.lower() == 'problem':
        main_benefit = form_data.get('main_benefit', 'solving problems')
        return generate_problem_image_prompt(
            product_name=product_name,
            product_type=product_type,
            product_description=product_description,
            main_benefit=main_benefit,
            scene_description=scene_description,
            brand_colors=brand_colors,
            brand_tone=brand_tone,
            target_platform=target_platform,
            has_logo=has_logo
        )
    
    elif scenario.lower() == 'solution':
        target_audience = form_data.get('target_audience', 'users')
        main_benefit = form_data.get('main_benefit', 'solving problems')
        return generate_solution_image_prompt(
            product_name=product_name,
            product_type=product_type,
            product_description=product_description,
            target_audience=target_audience,
            main_benefit=main_benefit,
            scene_description=scene_description,
            brand_colors=brand_colors,
            brand_tone=brand_tone,
            target_platform=target_platform,
            has_logo=has_logo
        )
    
    elif scenario.lower() == 'cta':
        return generate_cta_image_prompt(
            product_name=product_name,
            product_type=product_type,
            product_description=product_description,
            scene_description=scene_description,
            brand_colors=brand_colors,
            brand_tone=brand_tone,
            target_platform=target_platform,
            has_logo=has_logo
        )
    
    else:
        raise ValueError(f"Unknown scenario: {scenario}. Must be one of: hook, problem, solution, cta")
