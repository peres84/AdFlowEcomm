# Runware Prompt Engineering Module

This module provides a complete system for generating high-quality, optimized prompts for Runware.ai image and video generation using OpenAI.

## Features

- **Image Prompt Generation**: Generate 4 professional product image prompts optimized for Runware.ai
- **Video Scene Generation**: Generate 4 detailed video scene descriptions (Hook, Problem, Solution, CTA)
- **Quality Assurance**: Automatic validation of generated prompts
- **Logo Integration**: Support for natural logo integration in prompts
- **Scene Description Support**: Consistent visual style across all generated content

## Installation

```bash
pip install -r requirements.txt
```

Make sure you have an OpenAI API key set in your environment:

```bash
export OPENAI_API_KEY=your_api_key_here
```

Or use a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

## Quick Start

### Basic Usage

```python
from src.prompts.prompt_generator import RunwarePromptGenerator
import os

# Initialize generator
generator = RunwarePromptGenerator(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Product data
product_data = {
    "product_name": "Premium Coffee Maker",
    "category": "Appliance",
    "benefit": "Perfect coffee in 30 seconds, zero waste",
    "audience": "Millennials",
    "tone": "Professional",
    "brand_color": "#00A896"
}

# Scene description
scene_description = "Modern minimalist office. Clean whites and stainless steel. Soft natural light through windows."

# Generate image prompts
result = generator.generate_image_prompts(
    product_data=product_data,
    scene_description=scene_description,
    product_image_path="path/to/product.jpg",
    logo_path="path/to/logo.png",  # Optional
    validate=True
)

# Access prompts
for prompt in result["prompts"]:
    print(f"Use-Case: {prompt['use_case']}")
    print(f"Prompt: {prompt['runware_prompt']}")
    print(f"Logo: {prompt['logo_integration']}")
```

### Generate Video Scenes

```python
# Generate video scenes
video_result = generator.generate_video_scenes(
    product_data=product_data,
    scene_description=scene_description,
    generated_images=result["prompts"],  # Use generated image prompts
    logo_info={"description": "Logo available"},
    validate=True
)

# Access scenes
for scene in video_result["scenes"]:
    print(f"Scene {scene['scene_number']}: {scene['scene_name']} ({scene['duration']}s)")
    print(f"Visual: {scene['visual_description']}")
    print(f"Audio - Dialog: {scene['audio_design']['dialog']}")
```

### Complete Workflow

```python
# Generate both image prompts and video scenes in one call
complete_result = generator.generate_complete_prompts(
    product_data=product_data,
    scene_description=scene_description,
    product_image_path="path/to/product.jpg",
    logo_path="path/to/logo.png",
    validate=True
)

# Access results
image_prompts = complete_result["image_prompts"]["prompts"]
video_scenes = complete_result["video_scenes"]["scenes"]
quality_report = complete_result["quality_report"]
```

## Module Structure

### Core Modules

- **`system_prompts.py`**: Contains the OpenAI system prompts for image and video generation
- **`image_prompts.py`**: Functions for generating Runware image prompts
- **`video_prompts.py`**: Functions for generating Runware video scene descriptions
- **`quality_assurance.py`**: Quality validation functions
- **`prompt_generator.py`**: Main `RunwarePromptGenerator` class

### Key Functions

#### Image Prompt Generation

- `generate_runware_image_prompts()`: Main function to generate image prompts
- `analyze_product_image()`: Analyzes product image using OpenAI Vision
- `analyze_logo()`: Analyzes logo image if provided
- `parse_image_prompts_response()`: Parses OpenAI response into structured format

#### Video Scene Generation

- `generate_runware_video_scenes()`: Main function to generate video scene descriptions
- `parse_video_scenes_response()`: Parses OpenAI response into structured format

#### Quality Assurance

- `validate_image_prompts()`: Validates all image prompts
- `validate_video_scenes()`: Validates all video scenes
- `generate_quality_report()`: Comprehensive quality report
- `check_image_prompt_quality()`: Check individual image prompt
- `check_video_scene_quality()`: Check individual video scene

## Prompt Quality Requirements

### Image Prompts Must Include:

- ✅ Specific lighting description (studio, golden hour, etc.)
- ✅ Composition details (framing, position, rule of thirds)
- ✅ Materials/textures description
- ✅ Scene description aesthetic match
- ✅ Brand color integration (subtle)
- ✅ Logo integration instructions (if provided)
- ✅ Quality specification (1024x1024, professional, social-media-ready)
- ✅ Minimum 100 characters (3-5 sentences)

### Video Scenes Must Include:

- ✅ Visual description (2-3 sentences, minimum 50 chars)
- ✅ Camera/movement details (specific techniques)
- ✅ Lighting & mood description
- ✅ Image integration (which visual asset)
- ✅ Audio design:
  - Background music (specific style + tempo)
  - Sound effects (concrete description)
  - Dialog/narration (REQUIRED, minimum 10 chars)
  - Audio balance specification
- ✅ Engagement target
- ✅ Correct duration (7s, 7s, 10s, 6s)
- ✅ Scene 3 must include benefits showcased

## Output Format

### Image Prompt Output

```python
[
    {
        "use_case": "Morning Productivity Routine",
        "runware_prompt": "Professional product photography of a sleek black coffee maker...",
        "logo_integration": "Logo naturally integrated on product packaging..."
    },
    # ... 3 more prompts
]
```

### Video Scene Output

```python
[
    {
        "scene_number": 1,
        "scene_name": "HOOK",
        "duration": 7,
        "visual_description": "Opening shot: Extreme close-up...",
        "camera_movement": "Extreme close-up → slow pull-back...",
        "lighting_mood": "Soft natural window lighting...",
        "image_integration": "Generated Use-Case Image 1",
        "audio_design": {
            "music": "Upbeat modern electronic, 128 BPM...",
            "sfx": "Subtle mechanical whir...",
            "dialog": "Meet the future of coffee making...",
            "balance": "Music 60%, Narration 40%, SFX 10%"
        },
        "engagement_target": "Curiosity and visual wow factor",
        "emotional_tone": "Energetic but calm"
    },
    # ... 3 more scenes
]
```

## Scene Description Integration

The `scene_description` parameter is critical for maintaining visual consistency:

- **All generated images** must match the scene description aesthetic
- **All 4 video scenes** must maintain the scene description visual style
- **Audio design** should also match the scene description (e.g., minimalist = clean audio)

Example scene descriptions:
- "Modern minimalist office. Clean whites. Soft natural light."
- "Luxury lifestyle. Golden hour lighting. Premium aesthetic."
- "Outdoor adventure. Natural settings. Energetic atmosphere."

## Error Handling

The module raises `ValueError` if:
- Expected number of prompts/scenes is not generated
- Required fields are missing
- Image files cannot be read

Always wrap calls in try-except blocks:

```python
try:
    result = generator.generate_image_prompts(...)
except ValueError as e:
    print(f"Error: {e}")
```

## Examples

See `examples/prompt_generation_example.py` for complete usage examples.

## Best Practices

1. **Always validate**: Set `validate=True` to catch quality issues early
2. **Check quality reports**: Review validation reports to ensure prompt quality
3. **Iterate on scene descriptions**: Refine scene descriptions based on output quality
4. **Test with different products**: Validate prompts work across product categories
5. **Monitor OpenAI costs**: Image analysis uses Vision API, which has costs

## Next Steps

1. Test with actual Runware API integration
2. Iterate on prompt templates based on Runware output quality
3. Add more sophisticated parsing for edge cases
4. Expand quality assurance checks based on real-world usage
