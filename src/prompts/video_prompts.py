"""
Generate Runware.ai optimized video scene descriptions using OpenAI.
"""

import re
from typing import Dict, List, Optional, Any
from openai import OpenAI

from .system_prompts import VIDEO_GENERATION_SYSTEM_PROMPT


def build_video_generation_user_prompt(
    product_data: Dict[str, Any],
    scene_description: str,
    generated_images: List[Dict[str, str]],
    logo_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build the user prompt for OpenAI to generate Runware video scene descriptions.
    
    Args:
        product_data: Dictionary with product information
        scene_description: User-provided visual style description
        generated_images: List of generated image descriptions (use_case, runware_prompt, etc.)
        logo_info: Optional logo information dictionary
        
    Returns:
        Formatted user prompt string
    """
    prompt = f"""**PRODUCT INFORMATION:**
- Product Name: {product_data.get('product_name', 'Unknown')}
- Main Benefit: {product_data.get('benefit', 'Unknown')}
- Target Audience: {product_data.get('audience', 'Unknown')}
- Brand Tone: {product_data.get('tone', 'Unknown')}
- Brand Color: {product_data.get('brand_color', 'Unknown')}
- Website: {product_data.get('website', 'Unknown')}

**VISUAL STYLE & SCENE ATMOSPHERE:**
- Scene Description from User: {scene_description}
- ALL 4 VIDEO SCENES must maintain this visual style and atmosphere consistently
- Environment, mood, aesthetic consistency throughout video
- Example: If scene description is "luxury minimalist office", all scenes should maintain this aesthetic

**AVAILABLE VISUAL ASSETS:**
"""
    
    # Add original product image description (if available)
    if product_data.get('product_image_description'):
        prompt += f"- Original Product Image: {product_data.get('product_image_description')}\n"
    
    # Add generated use-case images
    for i, img in enumerate(generated_images, 1):
        use_case = img.get('use_case', f'Use-Case {i}')
        prompt += f"- Generated Use-Case Image {i}: {use_case}\n"
        # Optionally add more details if available
        if img.get('description'):
            prompt += f"  Description: {img.get('description')}\n"
    
    # Add logo information
    if logo_info:
        prompt += f"""- Logo Provided: YES
- Logo Description: {logo_info.get('description', 'Logo available')}
- Logo Integration Strategy: {logo_info.get('integration_strategy', 'Natural integration in scenes')}
"""
    else:
        prompt += "- Logo Provided: NO\n"
    
    prompt += """
**TASK:** Generate 4 complete scene descriptions optimized for Runware.ai video generation.

Each scene must include:
1. Vivid visual sequence description (2-3 sentences)
2. Camera work and transitions (specific techniques)
3. Lighting and mood (professional lighting details)
4. Image Integration (which visual asset featured)
5. Audio Design: Background music style, Sound effects descriptions, Dialog/Narration (REQUIRED), Music + Dialog balance specifications
6. Engagement elements for viewer retention

**CRITICAL: ENGAGEMENT AUDIO**
- Every scene must have either background music OR dialog/narration (or both)
- Dialog/Narration should be natural, conversational, not robotic
- Music should match emotional tone of scene
- Sound should create emotional engagement throughout video

**SCENE REQUIREMENTS:**

**SCENE 1: HOOK (7 seconds)**
Goal: Capture attention, create curiosity, stop the scroll
- Must have compelling visual opening
- Must include engaging audio (music + dialog/narration)
- Must match scene description aesthetic

**SCENE 2: PROBLEM (7 seconds)**
Goal: Identify pain point, show struggle, create emotional connection
- Must show realistic problem scenario
- Must have tension-building audio
- Must match scene description aesthetic

**SCENE 3: SOLUTION (10 seconds)**
Goal: Demonstrate benefits, show transformation, build excitement
- Must showcase 2-3 specific benefits
- Must have uplifting, inspiring audio
- Must match scene description aesthetic

**SCENE 4: CALL-TO-ACTION (6 seconds)**
Goal: Drive immediate action, create urgency, memorable brand close
- Must have professional product hero shot
- Must include clear call-to-action in dialog
- Must match scene description aesthetic

Generate the 4 scene descriptions now in the required format."""
    
    return prompt


def parse_video_scenes_response(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse OpenAI response to extract video scene descriptions.
    
    Args:
        response_text: Raw response from OpenAI
        
    Returns:
        List of dictionaries with scene details
    """
    scenes = []
    
    # Pattern to match scene sections
    scene_pattern = r'\*\*SCENE\s+(\d+):\s*(.+?)\s*\((\d+)\s+seconds?\)\*\*(.+?)(?=\*\*SCENE\s+\d+:|$)'
    
    matches = re.finditer(scene_pattern, response_text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        scene_num = int(match.group(1))
        scene_name = match.group(2).strip()
        duration = int(match.group(3))
        scene_content = match.group(4).strip()
        
        # Parse scene content
        scene_data = {
            "scene_number": scene_num,
            "scene_name": scene_name,
            "duration": duration,
            "visual_description": "",
            "camera_movement": "",
            "lighting_mood": "",
            "image_integration": "",
            "audio_design": {
                "music": "",
                "sfx": "",
                "dialog": "",
                "balance": ""
            },
            "engagement_target": "",
            "emotional_tone": ""
        }
        
        # Extract Visual Description
        visual_match = re.search(r'Visual\s+Description:\s*(.+?)(?=Camera|Lighting|Image|Audio|Engagement|Emotional|$)', scene_content, re.DOTALL | re.IGNORECASE)
        if visual_match:
            scene_data["visual_description"] = visual_match.group(1).strip()
        
        # Extract Camera/Movement
        camera_match = re.search(r'Camera/Movement:\s*(.+?)(?=Lighting|Image|Audio|Engagement|Emotional|$)', scene_content, re.DOTALL | re.IGNORECASE)
        if camera_match:
            scene_data["camera_movement"] = camera_match.group(1).strip()
        
        # Extract Lighting & Mood
        lighting_match = re.search(r'Lighting\s+&\s+Mood:\s*(.+?)(?=Image|Audio|Engagement|Emotional|$)', scene_content, re.DOTALL | re.IGNORECASE)
        if lighting_match:
            scene_data["lighting_mood"] = lighting_match.group(1).strip()
        
        # Extract Image Integration
        image_match = re.search(r'Image\s+Integration:\s*(.+?)(?=Audio|Engagement|Emotional|$)', scene_content, re.DOTALL | re.IGNORECASE)
        if image_match:
            scene_data["image_integration"] = image_match.group(1).strip()
        
        # Extract Audio Design
        audio_section = re.search(r'Audio\s+Design:\s*(.+?)(?=Engagement|Emotional|$)', scene_content, re.DOTALL | re.IGNORECASE)
        if audio_section:
            audio_text = audio_section.group(1)
            
            # Extract Music
            music_match = re.search(r'Background\s+Music:\s*(.+?)(?=Sound|Dialog|Audio\s+Balance|$)', audio_text, re.DOTALL | re.IGNORECASE)
            if music_match:
                scene_data["audio_design"]["music"] = music_match.group(1).strip()
            
            # Extract Sound Effects
            sfx_match = re.search(r'Sound\s+Effects:\s*(.+?)(?=Dialog|Audio\s+Balance|$)', audio_text, re.DOTALL | re.IGNORECASE)
            if sfx_match:
                scene_data["audio_design"]["sfx"] = sfx_match.group(1).strip()
            
            # Extract Dialog/Narration
            dialog_match = re.search(r'Dialog/Narration:\s*(.+?)(?=Audio\s+Balance|$)', audio_text, re.DOTALL | re.IGNORECASE)
            if dialog_match:
                scene_data["audio_design"]["dialog"] = dialog_match.group(1).strip()
            
            # Extract Audio Balance
            balance_match = re.search(r'Audio\s+Balance:\s*(.+?)(?=$)', audio_text, re.DOTALL | re.IGNORECASE)
            if balance_match:
                scene_data["audio_design"]["balance"] = balance_match.group(1).strip()
        
        # Extract Engagement Target
        engagement_match = re.search(r'Engagement\s+Target:\s*(.+?)(?=Emotional|$)', scene_content, re.DOTALL | re.IGNORECASE)
        if engagement_match:
            scene_data["engagement_target"] = engagement_match.group(1).strip()
        
        # Extract Emotional Tone
        emotional_match = re.search(r'Emotional\s+Tone:\s*(.+?)(?=$)', scene_content, re.DOTALL | re.IGNORECASE)
        if emotional_match:
            scene_data["emotional_tone"] = emotional_match.group(1).strip()
        
        # Extract Benefits Showcased (for Scene 3)
        if scene_num == 3:
            benefits_match = re.search(r'Benefits\s+Showcased:\s*(.+?)(?=Camera|Lighting|Image|Audio|Engagement|Emotional|$)', scene_content, re.DOTALL | re.IGNORECASE)
            if benefits_match:
                scene_data["benefits_showcased"] = benefits_match.group(1).strip()
        
        scenes.append(scene_data)
    
    # Fallback parsing if regex doesn't match
    if not scenes:
        # Try to split by "SCENE" markers
        scene_sections = re.split(r'SCENE\s+\d+:', response_text, flags=re.IGNORECASE)
        if len(scene_sections) > 1:
            for i, section in enumerate(scene_sections[1:], 1):
                scene_data = {
                    "scene_number": i,
                    "scene_name": f"Scene {i}",
                    "duration": 7 if i <= 2 else (10 if i == 3 else 6),
                    "visual_description": section[:500] if len(section) > 500 else section,
                    "camera_movement": "",
                    "lighting_mood": "",
                    "image_integration": "",
                    "audio_design": {
                        "music": "",
                        "sfx": "",
                        "dialog": "",
                        "balance": ""
                    },
                    "engagement_target": "",
                    "emotional_tone": ""
                }
                scenes.append(scene_data)
    
    return scenes


def generate_runware_video_scenes(
    client: OpenAI,
    product_data: Dict[str, Any],
    scene_description: str,
    generated_images: List[Dict[str, str]],
    logo_info: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Generate Runware.ai optimized video scene descriptions using OpenAI.
    
    Args:
        client: OpenAI client instance
        product_data: Dictionary with product information (name, benefit, audience, tone, brand_color, website)
        scene_description: User-provided visual style description
        generated_images: List of generated image descriptions (use_case, runware_prompt, etc.)
        logo_info: Optional logo information dictionary
        
    Returns:
        List of dictionaries with scene details (scene_number, duration, visual_description, etc.)
    """
    # Build user prompt
    user_prompt = build_video_generation_user_prompt(
        product_data=product_data,
        scene_description=scene_description,
        generated_images=generated_images,
        logo_info=logo_info
    )
    
    # Call OpenAI to generate scene descriptions
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": VIDEO_GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=3000
    )
    
    response_text = response.choices[0].message.content
    
    # Parse response
    scenes = parse_video_scenes_response(response_text)
    
    # Ensure we have exactly 4 scenes
    if len(scenes) < 4:
        raise ValueError(f"Expected 4 scenes, but got {len(scenes)}. Response: {response_text}")
    
    # Ensure correct durations: 5s, 5s, 10s, 5s = 25s total
    expected_durations = [5, 5, 10, 5]
    for i, scene in enumerate(scenes[:4]):
        scene["duration"] = expected_durations[i]  # Force correct duration
    
    return scenes[:4]  # Return first 4 if more were generated
