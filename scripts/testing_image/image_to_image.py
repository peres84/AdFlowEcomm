"""
Advertisement Mockup Generator - FLUX KONTEXT MAX APPROACH
Focus: Seamlessly place logo brand onto products using FLUX.1 Kontext [max]
Strategy: Use FLUX Kontext for precise iterative editing with reference images
"""

import asyncio
import os
import sys
from datetime import datetime
import aiohttp
import aiofiles
from dotenv import load_dotenv

load_dotenv()

try:
    from runware import Runware, IImageInference
except ImportError:
    print("Error: runware package not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)


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


async def test_scene1_hook():
    """
    Scene 1: HOOK - Eye-catching product presentation
    Strategy: Use FLUX Redux to incorporate logo brand into product scene
    """
    print("\n" + "="*60)
    print("SCENE 1: HOOK - Attention-Grabbing Product Shot")
    print("="*60)

    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set")
        return False

    product_path = "product-image.jpg"
    logo_path = "logo-brand.png"
    
    if not os.path.exists(product_path):
        print(f"⚠ Product image not found: {product_path}")
        return False
    
    if not os.path.exists(logo_path):
        print(f"⚠ Logo brand not found: {logo_path}")
        return False

    try:
        runware = Runware(api_key=api_key)
        await runware.connect()
        print("✓ Connected to Runware API")

        print(f"Uploading: {product_path}")
        product = await runware.uploadImage(product_path)
        print(f"✓ Uploaded product UUID: {product.imageUUID}")
        
        print(f"Uploading: {logo_path}")
        logo = await runware.uploadImage(logo_path)
        print(f"✓ Uploaded logo UUID: {logo.imageUUID}")

        output_dir = "output/ad_mockups"
        os.makedirs(output_dir, exist_ok=True)

        # Use FLUX.1 Kontext [max] for precise logo placement
        # Kontext uses referenceImages to guide the generation
        request = IImageInference(
            positivePrompt="""Seamlessly place the provided logo onto the front surface of the product in the image, 
            aligned with its perspective and curvature. Make it look realistically printed or embossed on the product housing, 
            with correct reflections, texture, and lighting. Preserve the professional studio lighting and the color balance 
            of the original photo. Subtly integrate the brand colors #FF5C85 and #FFEBC0 in the background or accent lights, 
            maintaining a clean, modern aesthetic. Do not distort the product shape or obscure details. 
            The result should look like a real branded product photo ready for marketing use.""",
            model="bfl:4@1",  # FLUX.1 Kontext [max] - best quality for editing
            referenceImages=[product.imageUUID, logo.imageUUID],  # Product + Logo as references
            height=1024,
            width=1024,
            numberResults=1,
            includeCost=True
        )

        print("\nGenerating HOOK scene (incorporating logo brand)...")
        images = await runware.imageInference(requestImage=request)

        for image in images:
            print(f"\n✓ Generated:")
            print(f"  URL: {image.imageURL}")
            if hasattr(image, 'cost'):
                print(f"  Cost: ${image.cost}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/scene1_hook_{timestamp}.png"
            await save_image(image.imageURL, filename)

        print("\n✓ Scene 1 complete - Logo brand incorporated into product")
        return True

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scene2_lifestyle():
    """
    Scene 2: SOLUTION - Lifestyle context with person
    Strategy: Generate person using product with logo brand visible
    """
    print("\n" + "="*60)
    print("SCENE 2: SOLUTION - Lifestyle Product Use")
    print("="*60)

    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set")
        return False

    product_path = "product-image.jpg"
    logo_path = "logo-brand.png"
    
    if not os.path.exists(product_path):
        print(f"⚠ Product image not found: {product_path}")
        return False
    
    if not os.path.exists(logo_path):
        print(f"⚠ Logo brand not found: {logo_path}")
        return False

    try:
        runware = Runware(api_key=api_key)
        await runware.connect()
        print("✓ Connected to Runware API")

        print(f"Uploading: {product_path}")
        product = await runware.uploadImage(product_path)
        print(f"✓ Uploaded product UUID: {product.imageUUID}")
        
        print(f"Uploading: {logo_path}")
        logo = await runware.uploadImage(logo_path)
        print(f"✓ Uploaded logo UUID: {logo.imageUUID}")

        output_dir = "output/ad_mockups"
        os.makedirs(output_dir, exist_ok=True)

        # Use FLUX.1 Kontext [max] for lifestyle scene with branded products
        request = IImageInference(
            positivePrompt="""Create a lifestyle beauty photography scene with a woman in white bathrobe applying skincare cream, 
            peaceful satisfied expression, clean white bathroom setting. Place branded cosmetic products on the counter with the 
            provided logo seamlessly integrated onto the product surfaces, aligned with perspective and curvature. 
            Make the branding look realistically printed with correct reflections and lighting. Natural morning light through window, 
            fresh green plants visible. Subtly integrate brand colors #FF5C85 and #FFEBC0 in accent lights or background elements. 
            Professional lifestyle magazine photography quality. The branded products should look authentic and ready for marketing use.""",
            model="bfl:4@1",  # FLUX.1 Kontext [max]
            referenceImages=[product.imageUUID, logo.imageUUID],  # Product + Logo as references
            height=1024,
            width=1024,
            numberResults=1,
            includeCost=True
        )

        print("\nGenerating SOLUTION scene (lifestyle with branded products)...")
        images = await runware.imageInference(requestImage=request)

        for image in images:
            print(f"\n✓ Generated:")
            print(f"  URL: {image.imageURL}")
            if hasattr(image, 'cost'):
                print(f"  Cost: ${image.cost}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/scene2_lifestyle_{timestamp}.png"
            await save_image(image.imageURL, filename)

        print("\n✓ Scene 2 complete - Lifestyle with branded products")
        return True

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scene3_hero():
    """
    Scene 3: CTA - Clean product hero shot
    Strategy: Showcase product with prominent logo branding
    """
    print("\n" + "="*60)
    print("SCENE 3: CTA - Product Hero Shot")
    print("="*60)

    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set")
        return False

    product_path = "product-image.jpg"
    logo_path = "logo-brand.png"
    
    if not os.path.exists(product_path):
        print(f"⚠ Product image not found: {product_path}")
        return False
    
    if not os.path.exists(logo_path):
        print(f"⚠ Logo brand not found: {logo_path}")
        return False

    try:
        runware = Runware(api_key=api_key)
        await runware.connect()
        print("✓ Connected to Runware API")

        print(f"Uploading: {product_path}")
        product = await runware.uploadImage(product_path)
        print(f"✓ Uploaded product UUID: {product.imageUUID}")
        
        print(f"Uploading: {logo_path}")
        logo = await runware.uploadImage(logo_path)
        print(f"✓ Uploaded logo UUID: {logo.imageUUID}")

        output_dir = "output/ad_mockups"
        os.makedirs(output_dir, exist_ok=True)

        # Use FLUX.1 Kontext [max] for hero product shot with prominent branding
        request = IImageInference(
            positivePrompt="""Professional e-commerce product photography of luxury cosmetic products elegantly arranged. 
            Seamlessly place the provided logo onto the front surface of each product, aligned with perspective and curvature. 
            Make the branding look realistically printed or embossed with correct reflections, texture, and lighting. 
            Clean white background with soft professional studio lighting. Green botanical styling elements for natural aesthetic. 
            Subtly integrate brand colors #FF5C85 and #FFEBC0 in accent lights or background glow. 
            Premium brand presentation with sharp, clear product packaging. Commercial quality ready for marketing use. 
            Do not distort product shapes or obscure details.""",
            model="bfl:4@1",  # FLUX.1 Kontext [max]
            referenceImages=[product.imageUUID, logo.imageUUID],  # Product + Logo as references
            height=1024,
            width=1024,
            numberResults=1,
            includeCost=True
        )

        print("\nGenerating CTA scene (branded hero shot)...")
        images = await runware.imageInference(requestImage=request)

        for image in images:
            print(f"\n✓ Generated:")
            print(f"  URL: {image.imageURL}")
            if hasattr(image, 'cost'):
                print(f"  Cost: ${image.cost}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/scene3_hero_{timestamp}.png"
            await save_image(image.imageURL, filename)

        print("\n✓ Scene 3 complete - Branded hero shot with logo")
        return True

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all scenes."""
    print("\n" + "="*60)
    print("ADVERTISEMENT MOCKUP GENERATOR")
    print("Strategy: Preserve Product, Enhance Context")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 FLUX KONTEXT MAX APPROACH:")
    print("  • Using FLUX.1 Kontext [max] - best quality iterative editing")
    print("  • Logo seamlessly placed with realistic reflections & texture")
    print("  • Reference images guide precise logo integration")
    print("  • Brand colors #FF5C85 & #FFEBC0 subtly integrated")
    print("\n📽 Scenes:")
    print("  1. HOOK     - Enhanced product presentation")
    print("  2. SOLUTION - Lifestyle usage context")
    print("  3. CTA      - Clean hero product shot")

    results = {
        "Scene 1 - HOOK": await test_scene1_hook(),
        "Scene 2 - SOLUTION": await test_scene2_lifestyle(),
        "Scene 3 - CTA": await test_scene3_hero(),
    }

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    for scene, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{scene}: {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\nScenes: {passed}/{total}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Saved to: output/ad_mockups/")

    return all(results.values())


if __name__ == "__main__":
    print("="*60)
    print("RUNWARE AD MOCKUP GENERATOR v4.0")
    print("FLUX.1 Kontext [max] - Precise Logo Placement")
    print("="*60)
    print("\nRequires:")
    print("  ✓ RUNWARE_API_KEY in .env")
    print("  ✓ product-image.jpg (base product)")
    print("  ✓ logo-brand.png (your logo to incorporate)")
    print("-" * 60)

    if not os.getenv("RUNWARE_API_KEY"):
        print("\n⚠ ERROR: RUNWARE_API_KEY not found")
        sys.exit(1)

    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
