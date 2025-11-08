"""
Dynamic Ad Campaign Generator with Image Analysis
Integrates product image analysis with user campaign configuration
"""

import asyncio
import os
import sys
import json
from datetime import datetime
import aiohttp
import aiofiles
from dotenv import load_dotenv

load_dotenv()

try:
    from runware import Runware, IImageInference
    from openai import OpenAI
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install runware openai")
    sys.exit(1)

from campaign_config import CampaignConfig, get_mockup_config
import base64


async def save_image(image_url: str, filename: str):
    """Download and save image from URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                async with aiofiles.open(filename, 'wb') as f:
                    await f.write(await response.read())
                print(f"✓ Saved: {filename}")
                return True
            else:
                print(f"✗ Failed to download (Status: {response.status})")
                return False


def analyze_product_image(image_path: str) -> dict:
    """Analyze product image using OpenAI Vision API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ Warning: OPENAI_API_KEY not set, skipping image analysis")
        return {}
    
    if not os.path.exists(image_path):
        print(f"⚠ Warning: Image not found: {image_path}")
        return {}
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Encode image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        prompt = """Analyze this product image and provide a JSON response with:
{
  "product_type": "specific product type",
  "description": "detailed visual description",
  "colors": ["main colors"],
  "materials": ["materials visible"],
  "style": "visual style"
}"""
        
        print(f"Analyzing product image: {image_path}")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
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
            temperature=0.3
        )
        
        analysis_text = response.choices[0].message.content
        
        # Try to parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in analysis_text:
                json_str = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                json_str = analysis_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = analysis_text
            
            analysis = json.loads(json_str)
            print(f"✓ Product identified: {analysis.get('product_type', 'Unknown')}")
            return analysis
            
        except json.JSONDecodeError:
            print("⚠ Could not parse JSON from analysis")
            return {"raw_response": analysis_text}
            
    except Exception as e:
        print(f"⚠ Image analysis failed: {e}")
        return {}


def generate_scene_prompt(scene_type: str, config: CampaignConfig) -> str:
    """
    Generate dynamic prompt based on scene type and campaign configuration.
    
    Args:
        scene_type: "hook", "solution", or "cta"
        config: Campaign configuration with user preferences
    """
    base_context = config.scene_vibe.to_prompt_context() if config.scene_vibe else ""
    brand_color = config.get_brand_color_integration()
    
    if scene_type == "hook":
        prompt = f"""Professional product photography featuring ONLY the {config.product_name}.
        
        Product to showcase: {config.product_description}
        
        IMPORTANT: Focus exclusively on THIS specific product - the {config.product_type}.
        Do not add other products, accessories, or unrelated items.
        Show only the robot vacuum and its docking station as described.
        
        Seamlessly place the provided logo onto the product surface, aligned with perspective and curvature.
        Make the branding look realistically printed or embossed with correct reflections, texture, and lighting.
        
        Visual style: {base_context}
        {brand_color}
        
        The product is the sole hero - clearly visible, beautifully presented, nothing else competing for attention.
        Clean composition focusing on the product's design and branding.
        Commercial quality ready for {config.target_platform.value}.
        Do not distort product shape or obscure details."""
        
    elif scene_type == "solution":
        environment = config.scene_vibe.environment if config.scene_vibe else 'home environment'
        
        prompt = f"""Lifestyle scene showing a person using {config.product_name} in real-world setting.
        
        CRITICAL BRANDING REQUIREMENT:
        Take the provided logo image and seamlessly place it onto the {config.product_type} surface.
        The logo MUST be clearly visible on the product, aligned with its perspective and curvature.
        Make the logo look realistically printed or embossed with correct reflections, shadows, texture, and lighting.
        The branding should appear as if it was professionally manufactured onto the product.
        
        SCENE COMPOSITION:
        Show a real person (target audience: {config.target_audience}) relaxed and happy, doing other activities.
        Person reading, relaxing on couch, playing with pet, or enjoying free time.
        The {config.product_type} works autonomously in the background or foreground.
        
        Product details: {config.product_description}
        Setting: {environment}
        Benefit being demonstrated: {config.main_benefit}
        
        Visual style: {base_context}
        {brand_color}
        
        Authentic {config.brand_tone.value.lower()} tone with genuine emotions.
        The product should be clearly visible with the logo prominently displayed.
        Professional lifestyle photography quality for {config.target_platform.value}."""
        
    else:  # cta
        prompt = f"""Hero product shot featuring ONLY the {config.product_name} for call-to-action.
        
        CRITICAL BRANDING REQUIREMENT - HIGHEST PRIORITY:
        Take the provided logo image and place it PROMINENTLY and CLEARLY onto the {config.product_type} surface.
        The logo MUST be the most visible branding element, aligned perfectly with the product's perspective and curvature.
        Make the logo look realistically printed or embossed with perfect reflections, shadows, texture, and lighting.
        The branding should appear professionally manufactured, sharp, and crystal clear.
        This is a marketing hero shot - the logo visibility is ESSENTIAL.
        
        PRODUCT FOCUS:
        Show exclusively THIS product: {config.product_description}
        No other products, no accessories, no additional items.
        Just the robot vacuum and docking station as the sole focus.
        
        Visual style: {base_context}
        {brand_color}
        
        Clean, impactful presentation with the product as the absolute hero.
        The logo should be large enough to read clearly and positioned prominently.
        Premium {config.brand_tone.value.lower()} aesthetic.
        Perfect for final frame of {config.target_platform.value} ad - drives viewers to take action.
        Commercial quality, marketing-ready, professional product photography with clear branding."""
    
    return prompt


async def generate_scene(
    scene_type: str,
    config: CampaignConfig,
    product_uuid: str,
    logo_uuid: str,
    output_dir: str
) -> bool:
    """Generate a single scene with dynamic prompts."""
    
    scene_names = {
        "hook": "HOOK - Attention Grabber",
        "solution": "SOLUTION - Product in Action",
        "cta": "CTA - Call to Action"
    }
    
    print("\n" + "="*60)
    print(f"SCENE: {scene_names[scene_type]}")
    print("="*60)
    
    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set")
        return False
    
    try:
        runware = Runware(api_key=api_key)
        await runware.connect()
        
        # Generate dynamic prompt
        prompt = generate_scene_prompt(scene_type, config)
        
        print(f"\nGenerated Prompt:")
        print("-" * 60)
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        print("-" * 60)
        
        # Create request
        request = IImageInference(
            positivePrompt=prompt,
            model="bfl:4@1",  # FLUX.1 Kontext [max]
            referenceImages=[product_uuid, logo_uuid],
            height=1024,
            width=1024,
            numberResults=1,
            includeCost=True
        )
        
        print(f"\nGenerating {scene_type} scene...")
        images = await runware.imageInference(requestImage=request)
        
        for image in images:
            print(f"\n✓ Generated:")
            print(f"  URL: {image.imageURL}")
            if hasattr(image, 'cost'):
                print(f"  Cost: ${image.cost}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/scene_{scene_type}_{timestamp}.png"
            await save_image(image.imageURL, filename)
        
        print(f"\n✓ Scene {scene_type} complete")
        return True
        
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_dynamic_campaign(
    product_image_path: str,
    logo_image_path: str,
    config: CampaignConfig
):
    """Run complete dynamic ad campaign generation."""
    
    print("="*60)
    print("DYNAMIC AD CAMPAIGN GENERATOR")
    print("="*60)
    print(f"Campaign: {config.product_name}")
    print(f"Platform: {config.target_platform.value}")
    print(f"Tone: {config.brand_tone.value}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Analyze product image
    print("\n" + "="*60)
    print("STEP 1: PRODUCT IMAGE ANALYSIS")
    print("="*60)
    
    analysis = analyze_product_image(product_image_path)
    
    if analysis:
        # Update config with analysis
        config.product_type = analysis.get('product_type', config.product_type)
        config.product_description = analysis.get('description', config.product_description)
        config.product_colors = analysis.get('colors', config.product_colors)
        config.product_materials = analysis.get('materials', config.product_materials)
        
        print(f"\nProduct Type: {config.product_type}")
        print(f"Description: {config.product_description[:100]}...")
    
    # Step 2: Upload images
    print("\n" + "="*60)
    print("STEP 2: UPLOAD IMAGES")
    print("="*60)
    
    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set")
        return False
    
    runware = Runware(api_key=api_key)
    await runware.connect()
    
    print(f"Uploading: {product_image_path}")
    product = await runware.uploadImage(product_image_path)
    print(f"✓ Product UUID: {product.imageUUID}")
    
    print(f"Uploading: {logo_image_path}")
    logo = await runware.uploadImage(logo_image_path)
    print(f"✓ Logo UUID: {logo.imageUUID}")
    
    # Step 3: Generate scenes
    print("\n" + "="*60)
    print("STEP 3: GENERATE AD SCENES")
    print("="*60)
    
    output_dir = f"output/campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save campaign config
    config_file = f"{output_dir}/campaign_config.json"
    with open(config_file, 'w') as f:
        json.dump({
            "product_name": config.product_name,
            "product_category": config.product_category,
            "target_audience": config.target_audience,
            "main_benefit": config.main_benefit,
            "brand_color": config.brand_color,
            "brand_tone": config.brand_tone.value,
            "target_platform": config.target_platform.value,
            "scene_vibe": {
                "visual_style": config.scene_vibe.visual_style,
                "lighting": config.scene_vibe.lighting,
                "environment": config.scene_vibe.environment,
                "mood": config.scene_vibe.mood
            } if config.scene_vibe else None,
            "product_analysis": {
                "type": config.product_type,
                "description": config.product_description,
                "colors": config.product_colors,
                "materials": config.product_materials
            }
        }, f, indent=2)
    print(f"\n✓ Config saved: {config_file}")
    
    results = {
        "Hook Scene": await generate_scene("hook", config, product.imageUUID, logo.imageUUID, output_dir),
        "Solution Scene": await generate_scene("solution", config, product.imageUUID, logo.imageUUID, output_dir),
        "CTA Scene": await generate_scene("cta", config, product.imageUUID, logo.imageUUID, output_dir)
    }
    
    # Summary
    print("\n" + "="*60)
    print("CAMPAIGN RESULTS")
    print("="*60)
    for scene, passed in results.items():
        status = "✓ SUCCESS" if passed else "✗ FAILED"
        print(f"{scene}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nScenes Generated: {passed}/{total}")
    print(f"Output Directory: {output_dir}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all(results.values())


if __name__ == "__main__":
    print("="*60)
    print("DYNAMIC AD CAMPAIGN GENERATOR v1.0")
    print("="*60)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        style = sys.argv[1]
    else:
        style = "luxury"
    
    print(f"\nUsing mockup config: {style.upper()}")
    print("\nAvailable styles: luxury, lifestyle, energetic")
    print("Usage: python test_dynamic_campaign.py [luxury|lifestyle|energetic]")
    print("-" * 60)
    
    # Load configuration
    config = get_mockup_config(style)
    
    # Run campaign
    success = asyncio.run(run_dynamic_campaign(
        product_image_path="product-image.jpg",
        logo_image_path="logo-brand.png",
        config=config
    ))
    
    sys.exit(0 if success else 1)
