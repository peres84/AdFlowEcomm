"""
OpenAI Vision Analysis Prompts
Prompts for analyzing product images and extracting characteristics
"""

from typing import Dict, Any


def get_product_analysis_prompt() -> str:
    """
    Get the prompt for analyzing a product image using OpenAI Vision API.
    
    Returns:
        str: Prompt text for product image analysis
    """
    return """Analyze this product image and provide a JSON response with:
{
  "product_type": "specific product type",
  "description": "detailed visual description",
  "colors": ["main colors"],
  "materials": ["materials visible"],
  "style": "visual style"
}"""


def get_selected_image_analysis_prompt(scenario: str) -> str:
    """
    Get the prompt for analyzing a selected image for video scene generation.
    
    Args:
        scenario: The scenario type (hook, problem, solution, cta)
        
    Returns:
        str: Prompt text for selected image analysis
    """
    return f"""Analyze this {scenario} image and extract visual characteristics including:
- Composition and layout
- Colors and color palette
- Lighting style and direction
- Mood and atmosphere
- Objects and elements present
- Visual style and aesthetic
- Camera angle and perspective

Provide a detailed description that can be used to generate a video scene matching this visual style."""


def get_image_prompt_generation_request(
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
) -> str:
    """
    Generate the OpenAI prompt for creating Runware image generation prompts.
    
    Args:
        product_name: Name of the product
        category: Product category
        target_audience: Target audience description
        main_benefit: Main benefit/problem solved
        brand_colors: List of brand colors
        brand_tone: Brand tone (Professional/Casual/Energetic/Luxury)
        target_platform: Target platform (Instagram/TikTok/etc)
        scene_description: User-provided visual style description
        product_analysis: Dictionary with product analysis results
        has_logo: Whether a logo was uploaded
        
    Returns:
        str: Complete prompt for OpenAI to generate image prompts
    """
    brand_colors_str = ', '.join(brand_colors) if brand_colors else 'Not specified'
    logo_status = "YES" if has_logo else "NO"
    
    product_type = product_analysis.get('product_type', 'Unknown')
    product_desc = product_analysis.get('description', 'No description available')
    product_colors = ', '.join(product_analysis.get('colors', [])) if product_analysis.get('colors') else 'Not analyzed'
    product_materials = ', '.join(product_analysis.get('materials', [])) if product_analysis.get('materials') else 'Not analyzed'
    product_style = product_analysis.get('style', 'Not analyzed')
    
    return f"""You are a professional product photographer and visual strategist analyzing images and data for AI image generation.

Your task: Analyze the provided product image and generate 4 detailed image generation prompts for Runware.ai.

**PRODUCT INFORMATION:**
- Product Name: {product_name}
- Category: {category}
- Main Benefit: {main_benefit}
- Target Audience: {target_audience}
- Brand Tone: {brand_tone}
- Brand Colors: {brand_colors_str}
- Target Platform: {target_platform}

**VISUAL STYLE & SCENE DESCRIPTION:**
- User-provided description: {scene_description}
- This describes how the user wants scenes to look and feel
- Visual atmosphere, environment, mood, aesthetic

**PRODUCT IMAGE ANALYSIS:**
- Product Type: {product_type}
- Description: {product_desc}
- Colors: {product_colors}
- Materials: {product_materials}
- Style: {product_style}

**LOGO ANALYSIS:**
- Logo Provided: {logo_status}
{"- Logo Integration Strategy: Naturally place logo on product surface, packaging, or branded elements in scene" if has_logo else "- No logo integration needed"}

**TASK:**
Generate exactly 4 image prompts specifically optimized for Runware.ai. Each prompt should:

1. Create a realistic, professional product showcase scene
2. Show the product in an authentic use-case scenario for one of these scenarios: Hook, Problem, Solution, CTA
3. {"Integrate logo naturally if provided (on packaging, signage, branded display)" if has_logo else "Focus on product and brand colors"}
4. Use vivid visual language perfectly suited for AI image generation
5. Include specific lighting, textures, materials, and colors
6. Reference brand colors subtly in composition
7. Match brand tone exactly
8. Produce professional, social-media-ready quality
9. Match the scene description aesthetic provided by the user

**OUTPUT FORMAT:**

Scenario: [Hook/Problem/Solution/CTA]
Use-Case: [Use-Case Name]
Runware Prompt: [Detailed, vivid prompt - 3-5 sentences with specific visual direction for Runware]
{"Logo Integration: [How/where logo appears]" if has_logo else ""}

[Repeat for all 4 scenarios]

---

**GUIDANCE FOR RUNWARE.AI PROMPTS:**
- Use concrete, descriptive language (Runware excels with specific visual details)
- **Incorporate scene description:** Each image should match the user-provided visual style
- Lighting: Always specify lighting type (studio, golden hour, bright daylight, soft diffused, etc.)
- Composition: Mention specific framing (close-up, mid-shot, wide angle, rule of thirds, etc.)
- Materials/Textures: Reference specific textures visible in the product image
- Background: Describe realistic, professional backgrounds suitable for the product **AND matching scene description**
- Style: Commercial photography, professional quality, polished
- Brand Colors: Subtle integration of brand colors in the scene
{"- Logo Placement: Natural, professional, enhances rather than distracts" if has_logo else ""}
- **Scene Atmosphere:** Match the feeling described in scene_description
- Target Quality: All prompts should generate minimum 1024x1024 high-quality images"""
