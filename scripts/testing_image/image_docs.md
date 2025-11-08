# Runware Image Inference Documentation

## Overview
This document covers how to use Runware AI for creating professional advertisement images using text-to-image and image-to-image generation with product images, branding, and logos.

## Installation

```bash
pip install runware
```

## Setup

Set your API key as an environment variable:
```bash
export RUNWARE_API_KEY="your_api_key_here"
```

Get your API key by creating a free account at: https://my.runware.ai/

## Available Models

Runware supports multiple models:
- **Stable Diffusion models** from CivitAI (format: `civitai:MODEL_ID@VERSION_ID`)
- **DALL-E 2/3** models from OpenAI
- **Flux** transformer models
- **Runware optimized models** (format: `runware:MODEL_ID@VERSION`)

Popular models for commercial/product photography:
- `civitai:140737@329420` - Realistic photography
- `runware:101@1` - General purpose high quality
- `runware:102@1` - Required for ACE++ character consistency

## Text-to-Image Generation

### Basic Example

```python
import asyncio
import os
from runware import Runware, IImageInference

async def text_to_image_basic():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    request_image = IImageInference(
        positivePrompt="professional product photography, luxury perfume bottle on marble surface, soft lighting, high resolution, commercial photography",
        model="civitai:140737@329420",
        numberResults=4,
        negativePrompt="blurry, low quality, distorted, amateur",
        height=1024,
        width=1024,
        steps=30,
        CFGScale=7.5,
        seed=42  # For reproducibility
    )

    images = await runware.imageInference(requestImage=request_image)

    for i, image in enumerate(images):
        print(f"Image {i+1} URL: {image.imageURL}")
        print(f"Seed used: {image.seed}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(text_to_image_basic())
```

### Advanced Text-to-Image with Branding

```python
async def text_to_image_branded():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    request_image = IImageInference(
        positivePrompt="""professional advertisement photography,
        premium skincare product, white background, studio lighting,
        minimalist design, luxury branding, high-end cosmetics,
        elegant composition, bokeh background, 8k resolution""",
        model="civitai:140737@329420",
        numberResults=2,
        negativePrompt="cluttered, dark, unprofessional, low quality, watermark",
        height=1024,
        width=1024,
        steps=40,
        CFGScale=8.0,
        outputFormat="PNG",
        includeCost=True
    )

    images = await runware.imageInference(requestImage=request_image)

    for image in images:
        print(f"Image URL: {image.imageURL}")
        if hasattr(image, 'cost'):
            print(f"Generation cost: ${image.cost}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(text_to_image_branded())
```

## Image-to-Image with Product Reference

### Using seedImage for Product Transformation

```python
async def image_to_image_product():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Upload your product image
    product_image = await runware.uploadImage("path/to/product_image.jpg")

    request_image = IImageInference(
        positivePrompt="""professional product photography,
        luxury setting, elegant background, soft studio lighting,
        commercial advertisement quality, high resolution""",
        seedImage=product_image.imageUUID,  # Your product image
        model="runware:101@1",
        strength=0.6,  # Lower = more like original, Higher = more creative
        width=1024,
        height=1024,
        steps=30,
        CFGScale=7.5,
        numberResults=2
    )

    images = await runware.imageInference(requestImage=request_image)

    for image in images:
        print(f"Transformed product image URL: {image.imageURL}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(image_to_image_product())
```

### IP-Adapter for Style Transfer (Brand Consistency)

IP-Adapters allow you to use reference images to guide style and branding:

```python
async def image_to_image_with_brand_style():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Upload your brand reference image (e.g., existing ad with your brand style)
    brand_style = await runware.uploadImage("path/to/brand_reference.jpg")
    # Upload your logo
    logo = await runware.uploadImage("path/to/logo.png")

    request_image = IImageInference(
        positivePrompt="""product advertisement, professional photography,
        clean background, modern aesthetic, commercial quality""",
        model="civitai:140737@329420",
        height=1024,
        width=1024,
        numberResults=1,
        ipAdapters=[
            {
                "model": "runware:55@3",  # IP-Adapter model
                "guideImages": [brand_style.imageUUID],
                "weight": 0.75  # 0.0 to 1.0, higher = stronger influence
            }
        ]
    )

    images = await runware.imageInference(requestImage=request_image)

    for image in images:
        print(f"Brand-styled image URL: {image.imageURL}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(image_to_image_with_brand_style())
```

### Multiple Reference Images for Product Branding

```python
async def multi_reference_product():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Upload multiple reference images
    product = await runware.uploadImage("path/to/product.jpg")
    brand_style = await runware.uploadImage("path/to/brand_aesthetic.jpg")

    request_image = IImageInference(
        positivePrompt="""luxury product advertisement,
        professional studio photography, premium quality,
        brand consistency, elegant composition""",
        model="civitai:140737@329420",
        seedImage=product.imageUUID,  # Main product reference
        strength=0.5,
        height=1024,
        width=1024,
        ipAdapters=[
            {
                "model": "runware:55@3",
                "guideImages": [brand_style.imageUUID],
                "weight": 0.6
            }
        ],
        steps=35,
        CFGScale=7.5
    )

    images = await runware.imageInference(requestImage=request_image)

    for image in images:
        print(f"Multi-reference image URL: {image.imageURL}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(multi_reference_product())
```

## ACE++ for Character-Consistent Product Shots

Use ACE++ when you need consistent character/product identity across multiple scenes:

```python
async def ace_product_consistency():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Upload your product/model reference
    reference = await runware.uploadImage("path/to/reference_product.jpg")

    from runware import IAcePlusPlus

    request_image = IImageInference(
        positivePrompt="""professional advertisement,
        product in outdoor setting, natural lighting, lifestyle photography""",
        model="runware:102@1",  # Required for ACE++
        height=1024,
        width=1024,
        numberResults=1,
        acePlusPlus=IAcePlusPlus(
            inputImages=[reference.imageUUID],
            repaintingScale=0.3  # 0.0-0.5, lower preserves more identity
        )
    )

    images = await runware.imageInference(requestImage=request_image)

    for image in images:
        print(f"Identity-preserved image URL: {image.imageURL}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(ace_product_consistency())
```

## Inpainting for Logo/Branding Integration

Add or modify specific parts of an image (e.g., adding a logo):

```python
async def add_logo_inpainting():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Upload base image and mask
    base_image = await runware.uploadImage("path/to/product_scene.jpg")
    mask_image = await runware.uploadImage("path/to/logo_mask.png")  # White where logo goes

    request_image = IImageInference(
        positivePrompt="company logo, brand mark, clean design, professional",
        model="runware:101@1",
        seedImage=base_image.imageUUID,
        maskImage=mask_image.imageUUID,
        strength=0.8,
        height=1024,
        width=1024,
        steps=30
    )

    images = await runware.imageInference(requestImage=request_image)

    for image in images:
        print(f"Logo-integrated image URL: {image.imageURL}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(add_logo_inpainting())
```

## Background Removal

Remove backgrounds for product isolation:

```python
async def remove_background():
    from runware import IImageBackgroundRemoval

    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Upload image or use existing UUID
    product_image = await runware.uploadImage("path/to/product.jpg")

    payload = IImageBackgroundRemoval(
        inputImage=product_image.imageUUID,
        outputFormat="PNG",
        rgba=(255, 255, 255, 0)  # Transparent background
    )

    images = await runware.imageBackgroundRemoval(
        removeImageBackgroundPayload=payload
    )

    for image in images:
        print(f"Background removed image URL: {image.imageURL}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(remove_background())
```

## Upscaling for High-Resolution Output

```python
async def upscale_image():
    from runware import IImageUpscale

    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Upload image to upscale
    image = await runware.uploadImage("path/to/image.jpg")

    payload = IImageUpscale(
        inputImage=image.imageUUID,
        upscaleFactor=4,  # 2x or 4x
        outputFormat="PNG"
    )

    upscaled = await runware.imageUpscale(upscaleGanPayload=payload)

    for img in upscaled:
        print(f"Upscaled image URL: {img.imageURL}")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(upscale_image())
```

## Performance Optimization

### Using teaCache for Faster Generation

```python
from runware import IAcceleratorOptions

request_image = IImageInference(
    positivePrompt="product advertisement",
    model="runware:101@1",
    height=1024,
    width=1024,
    acceleratorOptions=IAcceleratorOptions(
        teaCache=True,
        teaCacheDistance=0.6  # 0.1 (conservative) to 1.0 (aggressive)
    )
)
```

## Async Processing for Long Tasks

For batch processing or long tasks, use webhooks:

```python
async def async_processing():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    request_image = IImageInference(
        positivePrompt="professional product photography",
        model="civitai:140737@329420",
        height=1024,
        width=1024,
        webhookURL="https://your-server.com/webhook/runware"  # Results sent here
    )

    response = await runware.imageInference(requestImage=request_image)
    print(f"Task UUID: {response.taskUUID}")
    # Results will be posted to your webhook

    await runware.close()
```

## Key Parameters for Advertisement Images

- **positivePrompt**: Detailed description of desired image
- **negativePrompt**: What to avoid (blurry, low quality, etc.)
- **model**: Choose based on your needs (realistic, artistic, etc.)
- **height/width**: 1024x1024 recommended for quality
- **steps**: 30-50 for quality (higher = better but slower)
- **CFGScale**: 7-8.5 for prompt adherence
- **strength**: 0.5-0.7 for image-to-image (lower = more like original)
- **seed**: Set for reproducibility

## Best Practices for Product Advertisement Images

1. **Use high-quality reference images** for your products
2. **Specify professional photography terms** in prompts (studio lighting, commercial quality, etc.)
3. **Use IP-Adapters** to maintain brand consistency across images
4. **Set negative prompts** to avoid common issues (blurry, low quality, distorted)
5. **Use seedImage with low strength** (0.4-0.6) to maintain product features
6. **Combine multiple techniques**: seedImage for product + ipAdapters for brand style
7. **Upscale final images** to 4x for print quality
8. **Remove backgrounds** for versatile use across platforms
