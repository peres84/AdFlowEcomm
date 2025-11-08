"""
Test script for text-to-image generation using Runware AI.
This script demonstrates basic text-to-image generation for creating advertisement images.
"""

import asyncio
import os
import sys
from datetime import datetime
import aiohttp
import aiofiles
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from runware import Runware, IImageInference
except ImportError:
    print("Error: runware package not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)


async def save_image(image_url: str, filename: str):
    """Download and save image from URL to local file."""
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                async with aiofiles.open(filename, 'wb') as f:
                    await f.write(await response.read())
                print(f"✓ Saved: {filename}")
                return True
            else:
                print(f"✗ Failed to download: {filename} (Status: {response.status})")
                return False


async def test_basic_text_to_image():
    """Test 1: Basic text-to-image generation."""
    print("\n" + "="*60)
    print("TEST 1: Basic Text-to-Image Generation")
    print("="*60)

    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY environment variable not set")
        return False

    try:
        runware = Runware(api_key=api_key)
        await runware.connect()
        print("✓ Connected to Runware API")

        request = IImageInference(
            positivePrompt="professional product photography, luxury perfume bottle, elegant marble surface, soft studio lighting, high quality, commercial photography",
            model="civitai:140737@329420",
            numberResults=2,
            negativePrompt="blurry, low quality, distorted, amateur, ugly",
            height=1024,
            width=1024,
            steps=30,
            CFGScale=7.5,
            seed=42,
            includeCost=True
        )

        print("Generating images... (this may take 30-60 seconds)")
        images = await runware.imageInference(requestImage=request)

        # Create output directory
        output_dir = "output/text_to_image"
        os.makedirs(output_dir, exist_ok=True)

        print(f"\n✓ Generated {len(images)} images")
        for i, image in enumerate(images):
            print(f"\nImage {i+1}:")
            print(f"  URL: {image.imageURL}")
            print(f"  UUID: {image.imageUUID}")
            print(f"  Seed: {image.seed}")
            if hasattr(image, 'cost'):
                print(f"  Cost: ${image.cost}")

            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/basic_{timestamp}_{i+1}.png"
            await save_image(image.imageURL, filename)

        print("\n✓ Test 1 completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Test 1 failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_branded_text_to_image():
    """Test 2: Text-to-image with branding/commercial focus."""
    print("\n" + "="*60)
    print("TEST 2: Branded Commercial Text-to-Image")
    print("="*60)

    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY environment variable not set")
        return False

    try:
        runware = Runware(api_key=api_key)
        await runware.connect()
        print("✓ Connected to Runware API")

        # Commercial product scenario
        prompt = """professional advertisement photography,
        premium cosmetic product, elegant white background, studio lighting,
        minimalist design, luxury branding, high-end aesthetic,
        commercial quality, soft shadows, 8k resolution"""

        output_dir = "output/text_to_image"
        os.makedirs(output_dir, exist_ok=True)

        request = IImageInference(
            positivePrompt=prompt,
            model="civitai:140737@329420",
            numberResults=1,
            negativePrompt="cluttered, dark, unprofessional, low quality, watermark, text, logo",
            height=1024,
            width=1024,
            steps=30,
            CFGScale=7.5,
            outputFormat="PNG",
            includeCost=True
        )

        print("Generating branded commercial image...")
        images = await runware.imageInference(requestImage=request)

        for image in images:
            print(f"\nBranded Image:")
            print(f"  URL: {image.imageURL}")
            print(f"  UUID: {image.imageUUID}")
            if hasattr(image, 'cost'):
                print(f"  Cost: ${image.cost}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/branded_{timestamp}.png"
            await save_image(image.imageURL, filename)

        print("\n✓ Test 2 completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Test 2 failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_variations():
    """Test 3: Generate multiple variations of the same prompt."""
    print("\n" + "="*60)
    print("TEST 3: Multiple Variations with Different Seeds")
    print("="*60)

    api_key = os.getenv("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY environment variable not set")
        return False

    try:
        runware = Runware(api_key=api_key)
        await runware.connect()
        print("✓ Connected to Runware API")

        prompt = """professional advertisement,
        luxury watch on dark velvet, dramatic lighting,
        commercial photography, high-end product, elegant composition,
        premium quality, studio photography"""

        output_dir = "output/text_to_image"
        os.makedirs(output_dir, exist_ok=True)

        # Generate with different seeds
        seeds = [42, 123, 456]

        for seed in seeds:
            print(f"\n--- Generating with seed: {seed} ---")

            request = IImageInference(
                positivePrompt=prompt,
                model="civitai:140737@329420",
                numberResults=1,
                negativePrompt="blurry, low quality, amateur",
                height=1024,
                width=1024,
                steps=30,
                CFGScale=7.5,
                seed=seed
            )

            images = await runware.imageInference(requestImage=request)

            for image in images:
                print(f"  Generated with seed {seed}")
                print(f"  URL: {image.imageURL}")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{output_dir}/variation_seed_{seed}_{timestamp}.png"
                await save_image(image.imageURL, filename)

        print("\n✓ Test 3 completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Test 3 failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all text-to-image tests."""
    print("\n" + "="*60)
    print("RUNWARE TEXT-TO-IMAGE TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "Test 1 - Basic": await test_basic_text_to_image(),
        "Test 2 - Branded": await test_branded_text_to_image(),
    }

    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return all(results.values())


if __name__ == "__main__":
    print("Runware Text-to-Image Test Script")
    print("Make sure RUNWARE_API_KEY environment variable is set")
    print("-" * 60)

    # Check for API key
    if not os.getenv("RUNWARE_API_KEY"):
        print("\n⚠ WARNING: RUNWARE_API_KEY not found in environment variables")
        print("Please set it using:")
        print("  export RUNWARE_API_KEY='your_api_key_here'")
        sys.exit(1)

    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
