# Runware Python SDK Documentation

## Overview
This document provides comprehensive information about using the Runware Python SDK for image and video generation in your applications.

## Installation

```bash
pip install runware
```

**Requirements:**
- Python ≥ 3.10
- API key from https://my.runware.ai/

## Setup and Configuration

### Environment Variables

```bash
# Set your API key
export RUNWARE_API_KEY="your_api_key_here"

# Optional: Configure timeouts (in milliseconds)
export IMAGE_INFERENCE_TIMEOUT="120000"  # 2 minutes
export VIDEO_POLLING_TIMEOUT="1440000"   # 24 minutes
export AUDIO_POLLING_TIMEOUT="240000"    # 4 minutes
```

### Python Code Setup

```python
import os
from runware import Runware

# Initialize Runware client
runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
await runware.connect()

# ... perform operations ...

# Always close connection when done
await runware.close()
```

## Core Concepts

### Async/Await Pattern

All Runware SDK operations are asynchronous:

```python
import asyncio

async def main():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Your code here

    await runware.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Image UUIDs

Images are referenced by UUID v4 strings:
- Uploaded images return a UUID
- Generated images have a UUID
- Use these UUIDs in subsequent operations

```python
# Upload an image
uploaded = await runware.uploadImage("path/to/image.jpg")
image_uuid = uploaded.imageUUID

# Use UUID in another operation
request = IImageInference(
    seedImage=image_uuid,
    # ...
)
```

## Available Classes and Methods

### Main Client Class: `Runware`

```python
from runware import Runware

runware = Runware(api_key="your_key")
await runware.connect()  # Must call before operations
await runware.close()    # Call when done
```

### Image Generation Classes

#### IImageInference

Main class for text-to-image and image-to-image:

```python
from runware import IImageInference

request = IImageInference(
    # Required
    positivePrompt="a beautiful sunset",
    model="civitai:36520@76907",

    # Optional common parameters
    negativePrompt="blurry, low quality",
    height=512,
    width=512,
    numberResults=1,
    steps=30,
    CFGScale=7.5,
    seed=42,

    # Image-to-image parameters
    seedImage="uuid-of-uploaded-image",
    strength=0.7,

    # IP-Adapter for style guidance
    ipAdapters=[{
        "model": "runware:55@3",
        "guideImages": ["uuid1", "uuid2"],
        "weight": 0.75
    }],

    # Inpainting/outpainting
    maskImage="uuid-of-mask",

    # ACE++ for character consistency
    acePlusPlus=IAcePlusPlus(
        inputImages=["uuid"],
        repaintingScale=0.3
    ),

    # ControlNet
    controlNet=[{
        "model": "controlnet-model-id",
        "guideImage": "uuid",
        "weight": 0.8,
        "startStep": 0,
        "endStep": 1000
    }],

    # Performance optimization
    acceleratorOptions=IAcceleratorOptions(
        teaCache=True,
        teaCacheDistance=0.6
    ),

    # Output options
    outputFormat="PNG",  # PNG, JPG, WEBP
    outputType="base64",  # "base64" or "dataURI"

    # Async processing
    webhookURL="https://your-server.com/webhook",
    includeCost=True
)

images = await runware.imageInference(requestImage=request)
```

#### IImageBackgroundRemoval

```python
from runware import IImageBackgroundRemoval

payload = IImageBackgroundRemoval(
    inputImage="uuid-or-url",
    outputFormat="PNG",
    rgba=(255, 255, 255, 0)  # Background color (transparent)
)

images = await runware.imageBackgroundRemoval(
    removeImageBackgroundPayload=payload
)
```

#### IImageUpscale

```python
from runware import IImageUpscale

payload = IImageUpscale(
    inputImage="uuid-or-url",
    upscaleFactor=4,  # 2 or 4
    outputFormat="PNG"
)

upscaled = await runware.imageUpscale(upscaleGanPayload=payload)
```

#### IImageCaption

```python
from runware import IImageCaption

caption_payload = IImageCaption(
    inputImage="uuid-or-url"
)

result = await runware.imageCaption(requestImageToText=caption_payload)
print(result.text)  # Caption text
```

#### IPhotoMaker

```python
from runware import IPhotoMaker
import uuid

request = IPhotoMaker(
    model="civitai:139562@344487",
    positivePrompt="img of a person in a forest",
    steps=35,
    numberResults=1,
    height=512,
    width=512,
    style="No style",  # PhotoMaker style preset
    strength=40,  # 0-100
    outputFormat="WEBP",
    taskUUID=str(uuid.uuid4()),
    inputImages=[
        "https://example.com/face1.jpg",
        "https://example.com/face2.jpg"
    ]
)

photos = await runware.photoMaker(requestPhotoMaker=request)
```

### Video Generation Classes

#### IVideoInference

```python
from runware import IVideoInference, IFrameImage, IGoogleProviderSettings

request = IVideoInference(
    # Required
    positivePrompt="cinematic video of sunset",
    model="google:3@0",

    # Optional parameters
    width=1280,
    height=720,
    numberResults=1,
    seed=42,

    # Image-to-video
    frameImages=[
        IFrameImage(
            inputImage="uuid-or-url",
            position=0  # 0.0 to 1.0 (timeline position)
        ),
    ],

    # Reference images (style guidance)
    referenceImages=["uuid1", "uuid2"],

    # Provider-specific settings
    providerSettings=IGoogleProviderSettings(
        generateAudio=True,
        enhancePrompt=True
    ),

    # Async processing
    skipResponse=True,  # Get taskUUID immediately
    webhookURL="https://your-server.com/webhook",
    deliveryMethod="async",

    # Output
    outputFormat="MP4",  # MP4, WEBM, MOV
    includeCost=True
)

videos = await runware.videoInference(requestVideo=request)
```

#### IVideoBackgroundRemoval

```python
from runware import IVideoBackgroundRemoval, IVideoBackgroundRemovalInputs

request = IVideoBackgroundRemoval(
    model="bria:51@1",
    inputs=IVideoBackgroundRemovalInputs(
        video="uuid-or-url"
    ),
    outputFormat="WEBM",
    deliveryMethod="async"
)

videos = await runware.videoBackgroundRemoval(
    requestVideoBackgroundRemoval=request
)
```

#### IVideoCaption

```python
from runware import IVideoCaption, IVideoCaptionInputs

request = IVideoCaption(
    model="memories:1@1",
    inputs=IVideoCaptionInputs(
        video="https://example.com/video.mp4"
    ),
    deliveryMethod="async"
)

result = await runware.videoCaption(requestVideoCaption=request)
print(result.text)
```

### Utility Classes

#### IPromptEnhance

```python
from runware import IPromptEnhance

enhancer = IPromptEnhance(
    prompt="A beautiful sunset",
    promptVersions=3,      # Number of variations
    promptMaxLength=64     # Max length
)

enhanced = await runware.promptEnhance(promptEnhancer=enhancer)
for prompt in enhanced:
    print(prompt.text)
```

#### IAcePlusPlus

For character-consistent generation:

```python
from runware import IAcePlusPlus

ace = IAcePlusPlus(
    inputImages=["uuid1"],
    repaintingScale=0.3,  # 0.0-0.5, lower preserves identity more
    maskImage="uuid-of-mask"  # Optional selective editing
)
```

#### IAcceleratorOptions

Optimize inference speed:

```python
from runware import IAcceleratorOptions

# For Flux/SD3/transformer models
accelerator = IAcceleratorOptions(
    teaCache=True,
    teaCacheDistance=0.6  # 0.1 (conservative) to 1.0 (aggressive)
)

# For UNet models (Stable Diffusion 1.x/2.x)
accelerator = IAcceleratorOptions(
    deepCacheInterval=3,  # Steps between cache operations
    deepCacheBranchId=0
)

# For first-block caching
accelerator = IAcceleratorOptions(
    fbcache=True,
    cacheStartStep=0,
    cacheStopStep=8
)
```

### Helper Methods

#### Upload Image

```python
# From file path
uploaded = await runware.uploadImage("path/to/image.jpg")
print(uploaded.imageUUID)

# From URL (no upload needed, just use URL directly in requests)
```

#### Get Response (for async tasks)

```python
# When using skipResponse=True
response = await runware.videoInference(
    requestVideo=IVideoInference(
        positivePrompt="video",
        model="google:3@0",
        skipResponse=True
    )
)

task_uuid = response.taskUUID

# Poll for completion
results = await runware.getResponse(taskUUID=task_uuid)
```

#### Model Upload (Custom Models)

```python
from runware import IModelUpload

upload = IModelUpload(
    modelURL="https://example.com/model.safetensors",
    modelName="my-custom-model",
    modelType="checkpoint"  # checkpoint, lora, etc.
)

result = await runware.modelUpload(requestModelUpload=upload)
```

## Response Objects

### Image Response

```python
images = await runware.imageInference(...)

for image in images:
    print(image.imageURL)       # URL to generated image
    print(image.imageUUID)      # UUID for future reference
    print(image.seed)           # Seed used
    if hasattr(image, 'cost'):
        print(image.cost)       # Cost in USD
    if hasattr(image, 'taskUUID'):
        print(image.taskUUID)   # Task identifier
```

### Video Response

```python
videos = await runware.videoInference(...)

for video in videos:
    print(video.videoURL)       # URL to generated video
    print(video.seed)           # Seed used
    print(video.status)         # "success" or other status
    if hasattr(video, 'cost'):
        print(video.cost)       # Cost in USD
    if hasattr(video, 'taskUUID'):
        print(video.taskUUID)   # Task identifier
```

## Common Patterns

### Error Handling

```python
import asyncio

async def generate_image_safe():
    runware = None
    try:
        runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
        await runware.connect()

        request = IImageInference(
            positivePrompt="test",
            model="runware:101@1",
            height=512,
            width=512
        )

        images = await runware.imageInference(requestImage=request)
        return images

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        if runware:
            await runware.close()

if __name__ == "__main__":
    result = asyncio.run(generate_image_safe())
```

### Batch Processing

```python
async def batch_generate():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    prompts = [
        "a red apple",
        "a blue car",
        "a green tree"
    ]

    all_images = []

    for prompt in prompts:
        request = IImageInference(
            positivePrompt=prompt,
            model="runware:101@1",
            height=512,
            width=512,
            numberResults=2
        )

        images = await runware.imageInference(requestImage=request)
        all_images.extend(images)

    await runware.close()
    return all_images
```

### Concurrent Requests

```python
async def concurrent_generation():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Create multiple requests
    requests = [
        IImageInference(positivePrompt="sunset", model="runware:101@1", height=512, width=512),
        IImageInference(positivePrompt="ocean", model="runware:101@1", height=512, width=512),
        IImageInference(positivePrompt="mountain", model="runware:101@1", height=512, width=512),
    ]

    # Execute concurrently
    tasks = [runware.imageInference(requestImage=req) for req in requests]
    results = await asyncio.gather(*tasks)

    await runware.close()

    # Flatten results
    all_images = [img for result in results for img in result]
    return all_images
```

### Using Context Manager (if supported)

```python
async def with_context_manager():
    async with Runware(api_key=os.getenv("RUNWARE_API_KEY")) as runware:
        await runware.connect()

        request = IImageInference(
            positivePrompt="test",
            model="runware:101@1",
            height=512,
            width=512
        )

        images = await runware.imageInference(requestImage=request)
        return images
    # Automatically closed
```

## Advanced Features

### Webhook Integration

Set up a webhook server to receive results:

```python
# Flask example
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/runware', methods=['POST'])
def runware_webhook():
    data = request.json

    # Process the result
    if 'imageURL' in data:
        print(f"Image ready: {data['imageURL']}")
    elif 'videoURL' in data:
        print(f"Video ready: {data['videoURL']}")

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=5000)
```

```python
# In Runware code
request = IImageInference(
    positivePrompt="test",
    model="runware:101@1",
    height=512,
    width=512,
    webhookURL="https://your-domain.com/webhook/runware"
)

response = await runware.imageInference(requestImage=request)
print(f"Task submitted: {response.taskUUID}")
# Result will be posted to webhook
```

### Saving Images Locally

```python
import aiohttp
import aiofiles

async def save_image(image_url: str, filename: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                async with aiofiles.open(filename, 'wb') as f:
                    await f.write(await response.read())
                print(f"Saved: {filename}")

# Usage
async def generate_and_save():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    request = IImageInference(
        positivePrompt="beautiful landscape",
        model="runware:101@1",
        height=512,
        width=512
    )

    images = await runware.imageInference(requestImage=request)

    for i, image in enumerate(images):
        await save_image(image.imageURL, f"output_{i}.png")

    await runware.close()

if __name__ == "__main__":
    asyncio.run(generate_and_save())
```

### Progress Tracking for Long Tasks

```python
import time

async def track_video_progress():
    runware = Runware(api_key=os.getenv("RUNWARE_API_KEY"))
    await runware.connect()

    # Submit video generation
    request = IVideoInference(
        positivePrompt="cinematic video",
        model="google:3@0",
        width=1280,
        height=720,
        skipResponse=True
    )

    response = await runware.videoInference(requestVideo=request)
    task_uuid = response.taskUUID

    print(f"Task submitted: {task_uuid}")
    print("Waiting for completion...")

    # Poll for completion
    max_attempts = 120  # 10 minutes with 5-second intervals
    for attempt in range(max_attempts):
        try:
            result = await runware.getResponse(taskUUID=task_uuid)
            if result:
                print(f"Video ready: {result[0].videoURL}")
                break
        except:
            pass

        print(f"Still processing... ({attempt + 1}/{max_attempts})")
        await asyncio.sleep(5)

    await runware.close()
```

## Best Practices

1. **Always close connections**: Use `await runware.close()` when done
2. **Handle errors gracefully**: Wrap operations in try/except blocks
3. **Use async for long tasks**: Set `skipResponse=True` or use webhooks
4. **Reuse connections**: Create one Runware instance and reuse it
5. **Set seeds for reproducibility**: Use consistent seeds for A/B testing
6. **Enable cost tracking**: Use `includeCost=True` to monitor spending
7. **Optimize with accelerators**: Use teaCache/deepCache for faster generation
8. **Use appropriate timeouts**: Configure environment variables for long tasks
9. **Validate inputs**: Check image UUIDs exist before using them
10. **Save important UUIDs**: Store imageUUID for generated images you want to reuse

## Troubleshooting

### Connection Issues

```python
# Increase timeout
import os
os.environ["IMAGE_INFERENCE_TIMEOUT"] = "300000"  # 5 minutes
```

### Invalid Model ID

```python
# Check model format
# CivitAI: "civitai:MODEL_ID@VERSION_ID"
# Runware: "runware:MODEL_ID@VERSION"
# OpenAI: "openai:MODEL_ID@VERSION"
# Google: "google:MODEL_ID@VERSION"
```

### Image Upload Fails

```python
# Ensure file exists and is valid format
import os
if os.path.exists("path/to/image.jpg"):
    uploaded = await runware.uploadImage("path/to/image.jpg")
else:
    print("File not found")
```

### Video Takes Too Long

```python
# Use async delivery
request = IVideoInference(
    # ... params ...
    deliveryMethod="async",
    skipResponse=True
)
```

## Additional Resources

- **Official Documentation**: https://docs.runware.ai/
- **GitHub Repository**: https://github.com/Runware/sdk-python
- **PyPI Package**: https://pypi.org/project/runware/
- **API Reference**: https://runware.ai/docs/en/image-inference/api-reference
- **Get API Key**: https://my.runware.ai/
