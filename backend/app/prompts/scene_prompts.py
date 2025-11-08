"""
Video Scene Description Prompts
Prompts for generating detailed video scene descriptions with audio/visual elements
Based on specifications in documentation/product-guidelines/productflow_spec_no_code.md
"""

from typing import Dict, Any, List


def get_scene_description_generation_prompt(
    form_data: Dict[str, Any],
    product_analysis: Dict[str, Any],
    selected_images_analysis: Dict[str, List[str]],
    has_logo: bool = False
) -> str:
    """
    Generate the OpenAI prompt for creating video scene descriptions.
    
    Args:
        form_data: Dictionary containing all form data
        product_analysis: Dictionary containing product analysis results
        selected_images_analysis: Dictionary with analysis of selected images per scenario
        has_logo: Whether a logo was uploaded
        
    Returns:
        str: Complete prompt for OpenAI to generate scene descriptions
    """
    # Extract form data
    product_name = form_data.get('product_name', 'product')
    main_benefit = form_data.get('main_benefit', 'solving problems')
    target_audience = form_data.get('target_audience', 'users')
    brand_tone = form_data.get('brand_tone', 'Professional')
    brand_colors = form_data.get('brand_colors', [])
    brand_color_str = ', '.join(brand_colors) if brand_colors else 'brand colors'
    website = form_data.get('website', 'website')
    scene_description = form_data.get('scene_description', 'professional setting')
    target_platform = form_data.get('target_platform', 'social media')
    
    # Extract product analysis
    product_type = product_analysis.get('product_type', 'product')
    product_desc = product_analysis.get('description', 'product')
    
    # Format selected images analysis
    hook_analysis = selected_images_analysis.get('hook', ['No analysis available'])[0] if selected_images_analysis.get('hook') else 'No analysis available'
    problem_analysis = selected_images_analysis.get('problem', ['No analysis available'])[0] if selected_images_analysis.get('problem') else 'No analysis available'
    solution_analysis = selected_images_analysis.get('solution', ['No analysis available'])[0] if selected_images_analysis.get('solution') else 'No analysis available'
    cta_analysis = selected_images_analysis.get('cta', ['No analysis available'])[0] if selected_images_analysis.get('cta') else 'No analysis available'
    
    logo_status = "YES" if has_logo else "NO"
    logo_note = "Logo should be prominently featured in appropriate scenes" if has_logo else "No logo integration needed"
    
    return f"""You are a professional video director and copywriter specializing in high-converting product advertisements.

Your task: Create 4 detailed scene descriptions for a 30-second product video.

These descriptions will be used to generate individual video scenes using Runware.ai video generation.

**PRODUCT INFORMATION:**
- Product Name: {product_name}
- Product Type: {product_type}
- Product Description: {product_desc}
- Main Benefit: {main_benefit}
- Target Audience: {target_audience}
- Brand Tone: {brand_tone}
- Brand Colors: {brand_color_str}
- Website: {website}
- Target Platform: {target_platform}

**VISUAL STYLE & SCENE ATMOSPHERE:**
- Scene Description from User: {scene_description}
- All video scenes should follow this visual style and atmosphere
- Environment, mood, aesthetic consistency throughout video

**AVAILABLE VISUAL ASSETS:**
- Hook Image Analysis: {hook_analysis}
- Problem Image Analysis: {problem_analysis}
- Solution Image Analysis: {solution_analysis}
- CTA Image Analysis: {cta_analysis}

**LOGO:**
- Logo Provided: {logo_status}
- {logo_note}

**TASK:** Generate 4 complete scene descriptions optimized for Runware.ai video generation.

Each scene must include:
1. Vivid visual sequence description
2. Camera work and transitions
3. Lighting and mood
4. Audio direction: Background music style
5. Sound effects descriptions
6. Dialog/Narration (REQUIRED): Clear, compelling spoken narrative that matches the scene
7. Music + Dialog balance specifications
8. Engagement elements for viewer retention

**CRITICAL: ENGAGEMENT AUDIO**
- Every scene must have both background music AND dialog/narration
- Dialog/Narration should be natural, conversational, not robotic
- Music should match emotional tone of scene
- Sound should create emotional engagement throughout video

**TIMING:**
- Scene 1 (Hook): 7 seconds
- Scene 2 (Problem): 7 seconds
- Scene 3 (Solution): 10 seconds
- Scene 4 (CTA): 6 seconds
- Total: 30 seconds

---

**OUTPUT FORMAT:**

For each scene, provide:

**SCENE [NUMBER]: [NAME] ([DURATION] seconds)**

**Goal:** [What this scene achieves]

**Visual Description:** [2-3 sentences describing what viewer sees, camera movement, lighting, composition]

**Camera/Movement:** [Specific camera techniques - zoom, pan, tracking, dynamic cuts]

**Lighting & Mood:** [Professional lighting that creates visual impact and emotional pull]

**Audio Design:**
- Background Music: [Specific style and tempo - e.g., "upbeat modern electronic, fast-paced, energetic"]
- Sound Effects: [Audio elements that match visuals]
- Dialog/Narration: [Spoken narrative - compelling, natural, conversational. Max 2-4 sentences depending on scene duration]
- Audio Balance: [How dialog and music mix - e.g., "Music at 60%, narration clear at 40%"]

**Engagement Target:** [What hooks/engages the viewer in this scene]

---

**SCENE 1: HOOK (7 seconds)**
Goal: Capture attention, create curiosity, stop the scroll

[Generate complete scene description following the format above]

---

**SCENE 2: PROBLEM (7 seconds)**
Goal: Identify pain point, show struggle, create emotional connection

[Generate complete scene description following the format above]

Emotional Tone: Frustration, recognition, validation of struggle

---

**SCENE 3: SOLUTION (10 seconds)**
Goal: Demonstrate benefits, show transformation, build excitement, create satisfaction

[Generate complete scene description following the format above]

Benefits to Showcase:
- Primary benefit: {main_benefit}
- Show 2-3 specific ways the product solves problems
- Demonstrate lifestyle improvement

Pacing: Fast but not overwhelming, clearly showing multiple benefits

Emotional Tone: Relief, excitement, satisfaction, aspiration, confidence

---

**SCENE 4: CALL-TO-ACTION (6 seconds)**
Goal: Drive immediate action, create urgency, memorable brand close

[Generate complete scene description following the format above]

On-Screen Text Elements to include in description:
- Headline CTA: [Bold, compelling action - max 5 words]
- Secondary CTA: [Action instruction - max 5 words]
- Website: {website}

Visual Ending: Final memorable frame - product, {"logo," if has_logo else ""} brand, or aspirational customer moment

---

**OVERALL GUIDELINES:**

- Emotional Arc: Curiosity → Recognition → Excitement → Confidence (reflected in music progression)
- Scene Consistency: Music and audio should match the scene description aesthetic ({scene_description})
- Dialog Quality: Natural, conversational, not corporate or robotic
- Music Selection: Professional, matches brand tone ({brand_tone}) AND scene description
- Sound Design: Premium quality, enhances without distracting
- Narration Authenticity: Speaker should sound genuine, passionate about product
- Engagement Continuity: Audio keeps viewer engaged across all 4 scenes
- Music Transitions: Smooth progression between scenes
- Volume Clarity: Dialog always clear and audible over music/SFX
- Visual Audio Match: Audio design supports the visual atmosphere
- Platform Optimization: Optimized for {target_platform} viewing experience"""


def get_scene_regeneration_prompt(
    original_scene_description: str,
    scenario: str,
    user_feedback: str,
    form_data: Dict[str, Any]
) -> str:
    """
    Generate prompt for regenerating a specific scene description based on user feedback.
    
    Args:
        original_scene_description: The original scene description
        scenario: The scenario type (hook, problem, solution, cta)
        user_feedback: User's feedback or requested changes
        form_data: Dictionary containing all form data
        
    Returns:
        str: Complete prompt for OpenAI to regenerate scene description
    """
    product_name = form_data.get('product_name', 'product')
    brand_tone = form_data.get('brand_tone', 'Professional')
    scene_description = form_data.get('scene_description', 'professional setting')
    
    duration_map = {
        'hook': 7,
        'problem': 7,
        'solution': 10,
        'cta': 6
    }
    duration = duration_map.get(scenario.lower(), 7)
    
    return f"""You are a professional video director revising a scene description based on user feedback.

**ORIGINAL SCENE DESCRIPTION:**
{original_scene_description}

**USER FEEDBACK:**
{user_feedback}

**SCENE CONTEXT:**
- Scenario: {scenario.upper()}
- Duration: {duration} seconds
- Product: {product_name}
- Brand Tone: {brand_tone}
- Visual Style: {scene_description}

**TASK:**
Regenerate the scene description incorporating the user's feedback while maintaining:
1. Professional quality and engagement
2. Consistency with brand tone and visual style
3. Proper duration ({duration} seconds)
4. All required elements (visual description, camera work, lighting, audio design with music and dialog)

**OUTPUT FORMAT:**

**SCENE: {scenario.upper()} ({duration} seconds)**

**Goal:** [What this scene achieves]

**Visual Description:** [Updated based on feedback]

**Camera/Movement:** [Specific camera techniques]

**Lighting & Mood:** [Professional lighting]

**Audio Design:**
- Background Music: [Style and tempo]
- Sound Effects: [Audio elements]
- Dialog/Narration: [Natural, conversational spoken narrative]
- Audio Balance: [How dialog and music mix]

**Engagement Target:** [What hooks/engages the viewer]

Ensure the regenerated scene addresses the user's feedback while maintaining professional quality."""


def extract_scene_prompt_for_video_generation(scene_description: Dict[str, Any]) -> str:
    """
    Extract and format a scene description into a prompt for Runware video generation.
    
    Args:
        scene_description: Dictionary containing scene description details
        
    Returns:
        str: Formatted prompt for video generation
    """
    visual = scene_description.get('visual_description', '')
    camera = scene_description.get('camera_work', '')
    lighting = scene_description.get('lighting', '')
    audio = scene_description.get('audio_design', '')
    
    # Combine all elements into a cohesive prompt
    prompt_parts = []
    
    if visual:
        prompt_parts.append(visual)
    
    if camera:
        prompt_parts.append(f"Camera work: {camera}")
    
    if lighting:
        prompt_parts.append(f"Lighting: {lighting}")
    
    if audio:
        prompt_parts.append(f"Audio: {audio}")
    
    return ' '.join(prompt_parts)
