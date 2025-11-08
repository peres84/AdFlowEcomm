"""
Generate Runware.ai optimized image prompts using OpenAI.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from openai import OpenAI
from PIL import Image
import base64
import io
import requests
from urllib.parse import urlparse

from .system_prompts import IMAGE_GENERATION_SYSTEM_PROMPT


def _is_url(path_or_url: str) -> bool:
    """Check if the input is a URL."""
    try:
        result = urlparse(path_or_url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _load_image_data(path_or_url: str) -> Tuple[str, str]:
    """
    Load image data from either a local file path or URL.
    
    Args:
        path_or_url: Local file path or URL to image
        
    Returns:
        Tuple of (base64_encoded_data, mime_type)
    """
    if _is_url(path_or_url):
        # Load from URL
        response = requests.get(path_or_url, timeout=30)
        response.raise_for_status()
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        # Determine format from URL or content
        img = Image.open(io.BytesIO(response.content))
        image_format = img.format.lower() if img.format else 'png'
        mime_type = f"image/{image_format}"
    else:
        # Load from local file
        with open(path_or_url, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Determine image format
        img = Image.open(path_or_url)
        image_format = img.format.lower() if img.format else 'png'
        mime_type = f"image/{image_format}"
    
    return image_data, mime_type


def analyze_product_image(
    client: OpenAI,
    product_image_path: str
) -> str:
    """
    Analyze product image using OpenAI Vision API.
    
    Args:
        client: OpenAI client instance
        product_image_path: Path to product image file or URL
        
    Returns:
        String description of product image characteristics
    """
    # Load image data (from file or URL)
    image_data, mime_type = _load_image_data(product_image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this product image in detail. Describe:
1. Colors: What are the primary and secondary colors?
2. Materials: What materials are visible (metal, plastic, fabric, glass, etc.)?
3. Style: What is the design style (minimalist, modern, classic, etc.)?
4. Size: What is the approximate size/scale?
5. Key Features: What are the distinctive features or design elements?
6. Existing Branding: Are there any logos or branding visible?
7. Unique Selling Points: What makes this product visually attractive or unique?

Provide a comprehensive analysis that will help generate professional product photography prompts."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content


def analyze_logo(
    client: OpenAI,
    logo_path: Optional[str]
) -> Optional[str]:
    """
    Analyze logo image using OpenAI Vision API if provided.
    
    Args:
        client: OpenAI client instance
        logo_path: Path to logo image file or URL (optional)
        
    Returns:
        String description of logo characteristics or None
    """
    if not logo_path:
        return None
    
    # Load image data (from file or URL)
    image_data, mime_type = _load_image_data(logo_path)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this logo image. Describe:
1. Colors: What are the logo colors?
2. Style: What is the design style (minimalist, bold, elegant, etc.)?
3. Shape: What is the shape/format (circular, rectangular, wordmark, etc.)?
4. Design Elements: Any distinctive design elements or symbols?
5. Placement Strategy: How could this logo be naturally integrated into product photography (packaging, signage, display, etc.)?

Provide a concise analysis for logo integration in product images."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content


def build_image_generation_user_prompt(
    product_data: Dict[str, Any],
    scene_description: str,
    product_image_analysis: str,
    logo_analysis: Optional[str]
) -> str:
    """
    Build the user prompt for OpenAI to generate Runware image prompts.
    
    Args:
        product_data: Dictionary with product information
        scene_description: User-provided visual style description
        product_image_analysis: Analysis of product image
        logo_analysis: Analysis of logo (if provided)
        
    Returns:
        Formatted user prompt string
    """
    prompt = f"""**PRODUCT INFORMATION:**
- Product Name: {product_data.get('product_name', 'Unknown')}
- Category: {product_data.get('category', 'Unknown')}
- Main Benefit: {product_data.get('benefit', 'Unknown')}
- Target Audience: {product_data.get('audience', 'Unknown')}
- Brand Tone: {product_data.get('tone', 'Unknown')}
- Brand Color: {product_data.get('brand_color', 'Unknown')}

**VISUAL STYLE & SCENE DESCRIPTION:**
- User-provided description: {scene_description}
- This describes how the user wants scenes to look and feel
- Visual atmosphere, environment, mood, aesthetic
- ALL generated images must match this scene description consistently

**PRODUCT IMAGE ANALYSIS:**
{product_image_analysis}

**LOGO ANALYSIS:**
"""
    
    if logo_analysis:
        prompt += f"""- Logo Provided: YES
- Logo Description: {logo_analysis}
- Logo Integration Strategy: Integrate logo naturally in product photography (packaging, signage, branded display, etc.)
"""
    else:
        prompt += """- Logo Provided: NO
- Logo Integration Strategy: Focus on product image and brand color only
"""
    
    prompt += """
**TASK:**
Generate exactly 4 image prompts specifically optimized for Runware.ai. Each prompt should:

1. Create a realistic, professional product showcase scene
2. Show the product in an authentic use-case scenario
3. Integrate logo naturally if provided (on packaging, signage, branded display)
4. Use vivid visual language perfectly suited for AI image generation
5. Include specific lighting, textures, materials, and colors
6. Reference brand color subtly in composition
7. Match brand tone exactly
8. Produce professional, social-media-ready quality
9. **CRITICAL:** Match the scene description aesthetic consistently

**GUIDANCE FOR RUNWARE.AI PROMPTS:**
- Use concrete, descriptive language (Runware excels with specific visual details)
- **Incorporate scene description:** Each image must match the user-provided visual style
- Lighting: Always specify lighting type (studio, golden hour, bright daylight, soft diffused, etc.)
- Composition: Mention specific framing (close-up, mid-shot, wide angle, rule of thirds, etc.)
- Materials/Textures: Reference specific textures visible in the product image
- Background: Describe realistic, professional backgrounds suitable for the product AND matching scene description
- Style: Commercial photography, professional quality, polished
- Brand Color: Subtle integration of brand color in the scene
- Logo Placement (if provided): Natural, professional, enhances rather than distracts
- **Scene Atmosphere:** Match the feeling described in scene_description (modern/luxury/casual/outdoor/etc.)
- Target Quality: All prompts should generate minimum 1024x1024 high-quality images

Generate the 4 prompts now in the required format."""
    
    return prompt


def parse_image_prompts_response(response_text: str) -> List[Dict[str, str]]:
    """
    Parse OpenAI response to extract image prompts.
    
    Args:
        response_text: Raw response from OpenAI
        
    Returns:
        List of dictionaries with use_case, runware_prompt, and logo_integration
    """
    prompts = []
    
    # Pattern to match: "Use-Case X: [Name]" followed by "Runware Prompt:" and "Logo Integration:"
    pattern = r'Use-Case\s+(\d+):\s*(.+?)\s+Runware\s+Prompt:\s*(.+?)\s+Logo\s+Integration:\s*(.+?)(?=Use-Case\s+\d+:|$)'
    
    matches = re.finditer(pattern, response_text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        use_case_num = match.group(1)
        use_case_name = match.group(2).strip()
        runware_prompt = match.group(3).strip()
        logo_integration = match.group(4).strip()
        
        prompts.append({
            "use_case": use_case_name,
            "runware_prompt": runware_prompt,
            "logo_integration": logo_integration
        })
    
    # Fallback: Try simpler pattern if first one doesn't match
    if not prompts:
        # Try to find numbered use cases
        parts = re.split(r'Use-Case\s+\d+:', response_text, flags=re.IGNORECASE)
        if len(parts) > 1:
            for i, part in enumerate(parts[1:], 1):
                # Extract use case name (first line)
                lines = part.strip().split('\n')
                use_case_name = lines[0].strip() if lines else f"Use-Case {i}"
                
                # Find Runware Prompt section
                runware_prompt = ""
                logo_integration = "No logo"
                
                in_prompt_section = False
                in_logo_section = False
                
                for line in lines[1:]:
                    if 'runware prompt:' in line.lower():
                        in_prompt_section = True
                        in_logo_section = False
                        # Get text after "Runware Prompt:"
                        prompt_text = line.split(':', 1)[1].strip() if ':' in line else ""
                        if prompt_text:
                            runware_prompt += prompt_text + " "
                    elif 'logo integration:' in line.lower():
                        in_prompt_section = False
                        in_logo_section = True
                        logo_text = line.split(':', 1)[1].strip() if ':' in line else ""
                        if logo_text:
                            logo_integration = logo_text
                    elif in_prompt_section and not in_logo_section:
                        runware_prompt += line.strip() + " "
                    elif in_logo_section:
                        logo_integration += " " + line.strip()
                
                if runware_prompt:
                    prompts.append({
                        "use_case": use_case_name,
                        "runware_prompt": runware_prompt.strip(),
                        "logo_integration": logo_integration.strip()
                    })
    
    return prompts


def generate_runware_image_prompts(
    client: OpenAI,
    product_data: Dict[str, Any],
    scene_description: str,
    product_image_path: str,
    logo_path: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Generate Runware.ai optimized image prompts using OpenAI.
    
    Args:
        client: OpenAI client instance
        product_data: Dictionary with product information (name, category, benefit, audience, tone, brand_color)
        scene_description: User-provided visual style description
        product_image_path: Path to product image file or URL
        logo_path: Optional path to logo image file or URL
        
    Returns:
        List of dictionaries with use_case, runware_prompt, and logo_integration
    """
    # Step 1: Analyze product image
    product_image_analysis = analyze_product_image(client, product_image_path)
    
    # Step 2: Analyze logo if provided
    logo_analysis = analyze_logo(client, logo_path) if logo_path else None
    
    # Step 3: Build user prompt
    user_prompt = build_image_generation_user_prompt(
        product_data=product_data,
        scene_description=scene_description,
        product_image_analysis=product_image_analysis,
        logo_analysis=logo_analysis
    )
    
    # Step 4: Call OpenAI to generate prompts
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": IMAGE_GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    response_text = response.choices[0].message.content
    
    # Step 5: Parse response
    prompts = parse_image_prompts_response(response_text)
    
    # Ensure we have exactly 4 prompts
    if len(prompts) < 4:
        raise ValueError(f"Expected 4 prompts, but got {len(prompts)}. Response: {response_text}")
    
    return prompts[:4]  # Return first 4 if more were generated
