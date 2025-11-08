"""
Example usage of Runware Prompt Generator.

This demonstrates how to use the prompt generation system to create
high-quality prompts for Runware.ai image and video generation.
"""

import os
from dotenv import load_dotenv
from src.prompts.prompt_generator import RunwarePromptGenerator

# Load environment variables
load_dotenv()


def example_image_prompt_generation():
    """Example: Generate image prompts for a product."""
    
    # Initialize generator
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    generator = RunwarePromptGenerator(openai_api_key=api_key)
    
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
    scene_description = "Modern minimalist office. Clean whites and stainless steel. Soft natural light through windows. Professional yet welcoming. Real people, genuine morning moments, not staged. Premium quality aesthetic."
    
    # Generate prompts
    result = generator.generate_image_prompts(
        product_data=product_data,
        scene_description=scene_description,
        product_image_path="path/to/product_image.jpg",  # Replace with actual path
        logo_path="path/to/logo.png",  # Optional
        validate=True
    )
    
    # Print results
    print("Generated Image Prompts:")
    print(f"Total: {result['count']}")
    print("\n" + "="*80 + "\n")
    
    for i, prompt in enumerate(result["prompts"], 1):
        print(f"Use-Case {i}: {prompt['use_case']}")
        print(f"Prompt: {prompt['runware_prompt']}")
        print(f"Logo Integration: {prompt['logo_integration']}")
        print("\n" + "-"*80 + "\n")
    
    # Print validation results
    if result.get("validation"):
        validation = result["validation"]
        print(f"Validation: {'✓ Valid' if validation['is_valid'] else '✗ Invalid'}")
        print(f"Valid prompts: {validation['report']['valid_prompts']}/{validation['report']['total_prompts']}")
        
        for detail in validation["report"]["prompt_details"]:
            if not detail["is_valid"]:
                print(f"  Prompt {detail['prompt_number']} issues: {', '.join(detail['issues'])}")


def example_video_scene_generation():
    """Example: Generate video scene descriptions."""
    
    # Initialize generator
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    generator = RunwarePromptGenerator(openai_api_key=api_key)
    
    # Product data
    product_data = {
        "product_name": "Premium Coffee Maker",
        "benefit": "Perfect coffee in 30 seconds, zero waste",
        "audience": "Millennials",
        "tone": "Professional",
        "brand_color": "#00A896",
        "website": "https://coffeebrand.com"
    }
    
    # Scene description
    scene_description = "Modern minimalist office. Clean whites and stainless steel. Soft natural light through windows. Professional yet welcoming."
    
    # Generated images (from previous step)
    generated_images = [
        {
            "use_case": "Morning Productivity Routine",
            "runware_prompt": "Professional product photography of a sleek black coffee maker...",
            "logo_integration": "Logo on packaging"
        },
        # ... 3 more images
    ]
    
    # Generate video scenes
    result = generator.generate_video_scenes(
        product_data=product_data,
        scene_description=scene_description,
        generated_images=generated_images,
        logo_info={"description": "Logo available"},
        validate=True
    )
    
    # Print results
    print("Generated Video Scenes:")
    print(f"Total: {result['count']} scenes")
    print(f"Total Duration: {result['total_duration']} seconds")
    print("\n" + "="*80 + "\n")
    
    for scene in result["scenes"]:
        print(f"Scene {scene['scene_number']}: {scene['scene_name']} ({scene['duration']}s)")
        print(f"Visual: {scene['visual_description'][:100]}...")
        print(f"Camera: {scene['camera_movement'][:100]}...")
        print(f"Audio - Music: {scene['audio_design']['music'][:100]}...")
        print(f"Audio - Dialog: {scene['audio_design']['dialog']}")
        print("\n" + "-"*80 + "\n")
    
    # Print validation results
    if result.get("validation"):
        validation = result["validation"]
        print(f"Validation: {'✓ Valid' if validation['is_valid'] else '✗ Invalid'}")
        print(f"Valid scenes: {validation['report']['valid_scenes']}/{validation['report']['total_scenes']}")


def example_complete_workflow():
    """Example: Complete workflow - generate both images and video prompts."""
    
    # Initialize generator
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    generator = RunwarePromptGenerator(openai_api_key=api_key)
    
    # Product data
    product_data = {
        "product_name": "Premium Coffee Maker",
        "category": "Appliance",
        "benefit": "Perfect coffee in 30 seconds, zero waste",
        "audience": "Millennials",
        "tone": "Professional",
        "brand_color": "#00A896",
        "website": "https://coffeebrand.com"
    }
    
    # Scene description
    scene_description = "Modern minimalist office. Clean whites and stainless steel. Soft natural light through windows. Professional yet welcoming."
    
    # Generate complete prompts
    result = generator.generate_complete_prompts(
        product_data=product_data,
        scene_description=scene_description,
        product_image_path="path/to/product_image.jpg",  # Replace with actual path
        logo_path="path/to/logo.png",  # Optional
        validate=True
    )
    
    # Print summary
    print("Complete Prompt Generation Results:")
    print(f"Image Prompts: {result['image_prompts']['count']}")
    print(f"Video Scenes: {result['video_scenes']['count']}")
    print(f"Total Video Duration: {result['video_scenes']['total_duration']}s")
    print(f"Overall Valid: {'✓ Yes' if result['overall_valid'] else '✗ No'}")


if __name__ == "__main__":
    # Uncomment the example you want to run:
    # example_image_prompt_generation()
    # example_video_scene_generation()
    # example_complete_workflow()
    
    print("See function examples above. Uncomment to run.")
