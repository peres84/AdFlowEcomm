# Helper Functions - Complete Reference

Professional utilities for Runware video generation workflows. All helper functions are tested and verified working.

---

## 📁 Available Helper Modules

### 1. Image Resizing (`resizer_img.py`)

**Purpose:** Resize images to meet API dimension requirements

**Main Function:**
```python
from scripts.resizer_img import resize_image

resized_path = resize_image(
    image_path="product.jpg",
    target_width=1366,
    target_height=768,
    quality=95
)
```

**All Functions:**
- `resize_image()` - Resize with quality control and aspect ratio options
- `get_image_dimensions()` - Get image dimensions without full load
- `validate_dimensions()` - Check if image meets requirements

**Features:**
- Professional quality resizing (LANCZOS algorithm)
- RGBA to RGB conversion for JPEG
- Aspect ratio preservation option
- Validation and error handling

**Use Case:** When Runware API rejects images due to `invalidFrameImageWidth` errors

---

### 2. Format Conversion (`extension_changer_img.py`)

**Purpose:** Convert images between formats for API compatibility

**Main Function:**
```python
from scripts.extension_changer_img import convert_image_format

converted_path = convert_image_format(
    image_path="product.png",
    target_format="JPEG"
)
```

**All Functions:**
- `convert_image_format()` - Convert between formats (JPEG, PNG, WEBP, etc.)
- `get_image_format()` - Check current image format
- `is_format_supported()` - Validate format compatibility
- `convert_for_api()` - Auto-convert for specific APIs
- `batch_convert()` - Convert multiple images at once

**Features:**
- Supports JPEG, PNG, WEBP, BMP, TIFF, GIF
- Transparency handling
- API-specific conversion helpers
- Batch conversion support

**Use Case:** When API requires specific image formats

---

### 3. Video Generation (`video_helpers.py`)

**Purpose:** Core Runware API operations

**Main Class:**
```python
from scripts.video_helpers import RunwareVideoHelper

helper = RunwareVideoHelper(api_key="your_key")

# Upload image
image_id = helper.upload_image("product.jpg")

# Generate video
task_uuid, _ = helper.generate_video(
    prompt="Product video description",
    image_id=image_id,
    model="minimax:1@1",
    duration=6
)

# Poll until complete
result = helper.poll_until_complete(task_uuid)

# Download
helper.download_video(result["videoURL"], "output.mp4")
```

**Classes:**
- `RunwareVideoHelper` - Main helper class for Runware API operations

**Functions:**
- `resize_for_model()` - Resize images to model-specific dimensions
- `stitch_videos_ffmpeg()` - Stitch multiple videos using FFmpeg
- `get_video_info()` - Get video metadata using FFprobe

**Constants:**
- `MODEL_CONFIGS` - Pre-configured settings for different video models

**Features:**
- Complete Runware API wrapper
- Automatic polling with timeout
- Error handling
- Model configurations

---

### 4. Multi-Scene Generation (`scene_generator.py`)

**Purpose:** Generate and stitch 4-scene product videos

---

### 5. Video-Audio Merging (`video_audio_merger.py`)

**Purpose:** Merge video and audio files using FFmpeg

**Main Class:**
```python
from scripts.scene_generator import MultiSceneGenerator, create_standard_scenes

# Create scene configs
scenes = create_standard_scenes(
    product_name="Coffee Maker",
    benefit="Perfect coffee in 30 seconds",
    image_id=image_id,
    scene_vibe="Modern minimalist kitchen"
)

# Generate complete video
generator = MultiSceneGenerator(api_key="your_key")
final_video = generator.generate_complete_video(
    scenes=scenes,
    output_filename="product_video.mp4"
)
```

**Classes:**
- `SceneConfig` - Configuration for a single video scene
- `MultiSceneGenerator` - Generate and stitch multiple scenes

**Functions:**
- `create_standard_scenes()` - Create standard 4-scene product video configuration

**Features:**
- 4-scene workflow (Hook, Problem, Solution, CTA)
- Automatic FFmpeg stitching
- Progress tracking
- Error recovery

---

### 5. Video-Audio Merging (`video_audio_merger.py`)

**Purpose:** Merge video and audio files using FFmpeg

**Main Function:**
```python
from scripts.utils.video_audio_merger import merge_video_audio

success = merge_video_audio(
    video_path="video.mp4",
    audio_path="audio.mp3",
    output_path="final_video.mp4"
)
```

**All Functions:**
- `merge_video_audio()` - Merge video and audio with full control
- `replace_audio()` - Replace existing audio track
- `add_background_music()` - Mix background music with original audio
- `extract_audio()` - Extract audio from video
- `get_video_info()` - Get video metadata
- `check_ffmpeg_installed()` - Verify FFmpeg availability
- `quick_merge()` - Quick merge with defaults

**Features:**
- No video re-encoding (fast, lossless)
- Customizable audio codec and bitrate
- Background music mixing
- Audio extraction
- FFmpeg validation

**Use Case:** Adding AI-generated audio (Mirelo) to generated videos (Runware)

---

## 🎯 Quick Decision Guide

**Need to resize an image?**
→ Use `resizer_img.py`

**Need to convert image format?**
→ Use `extension_changer_img.py`

**Need to generate a single video?**
→ Use `video_helpers.py`

**Need to generate 4-scene product video?**
→ Use `scene_generator.py`

---

## 🚀 Quick Start Examples

### Single Video Generation

```python
from scripts.video_helpers import RunwareVideoHelper, resize_for_model

# Initialize
helper = RunwareVideoHelper(api_key="your_api_key")

# Prepare image
resized_path = resize_for_model("image.jpg", 1366, 768)

# Upload
image_id = helper.upload_image(resized_path)

# Generate video
task_uuid, _ = helper.generate_video(
    prompt="A smooth rotating product video",
    image_id=image_id,
    model="minimax:1@1",
    duration=6
)

# Poll until complete
result = helper.poll_until_complete(task_uuid)

# Download
if result.get("status") == "success":
    helper.download_video(result["videoURL"], "output.mp4")
```

### 4-Scene Product Video

```python
from scripts.scene_generator import MultiSceneGenerator, create_standard_scenes
from scripts.video_helpers import RunwareVideoHelper, resize_for_model

# Setup
helper = RunwareVideoHelper(api_key="your_api_key")
resized_path = resize_for_model("product.jpg", 1366, 768)
image_id = helper.upload_image(resized_path)

# Create scenes
scenes = create_standard_scenes(
    product_name="Premium Coffee Maker",
    benefit="Perfect coffee in 30 seconds",
    image_id=image_id,
    scene_vibe="Modern minimalist kitchen, soft natural lighting"
)

# Generate complete video
generator = MultiSceneGenerator(api_key="your_api_key")
final_video = generator.generate_complete_video(
    scenes=scenes,
    output_filename="product_video.mp4"
)
```

---

## 📋 Model Configurations

### Verified Working Models

**MiniMax 01 Base** ✅ (Recommended)
```python
{
    "model": "minimax:1@1",
    "duration": 6,
    "width": 1366,
    "height": 768,
    "generation_time": "~244s (4 minutes)"
}
```

**MiniMax Hailuo 02**
```python
{
    "model": "minimax:hailuo@2",
    "duration": 10,
    "width": 1366,
    "height": 768
}
```

**KlingAI Standard**
```python
{
    "model": "klingai:3@2",
    "duration": 10,
    "width": 1280,
    "height": 720
}
```

**PixVerse V3.5**
```python
{
    "model": "pixverse:3.5@1",
    "duration": 5,
    "width": 1080,
    "height": 1080
}
```

---

## 🎬 Scene Structure

Standard 4-scene product video (30 seconds total):

### Scene 1: HOOK (7s)
- **Goal:** Capture attention, stop the scroll
- **Content:** Opening shot, dynamic camera, attention-grabbing
- **Audio:** Energetic music, hook line

### Scene 2: PROBLEM (7s)
- **Goal:** Identify pain point, create connection
- **Content:** Problem scenario, relatable struggle
- **Audio:** Tension-building music, empathetic narration

### Scene 3: SOLUTION (10s)
- **Goal:** Demonstrate benefits, show transformation
- **Content:** Product in action, multiple use cases, benefits visible
- **Audio:** Inspiring music, benefit statements

### Scene 4: CTA (6s)
- **Goal:** Drive action, memorable close
- **Content:** Hero shot, brand elements, call-to-action
- **Audio:** Professional music, compelling CTA

---

## 🛠️ Requirements

### Python Packages
```bash
pip install requests pillow python-dotenv
```

### System Requirements
- **FFmpeg** - For video stitching
  - Windows: `choco install ffmpeg` or download from ffmpeg.org
  - Mac: `brew install ffmpeg`
  - Linux: `apt-get install ffmpeg`

### Environment Variables
```bash
RUNWARE_API_KEY=your_api_key_here
```

---

## ✅ Verification Status

All helper functions have been tested and verified:

- ✅ `resizer_img.py` - Correctly implements image resizing
- ✅ `extension_changer_img.py` - Format conversion working
- ✅ `video_helpers.py` - Runware API integration verified
- ✅ `scene_generator.py` - Multi-scene workflow ready

**Test Results:**
- MiniMax model: ✅ Working (244s generation time)
- Image upload: ✅ Working
- Status polling: ✅ Working
- Video download: ✅ Working

---

## 📖 Complete Examples

See the `testing/` directory for working examples:

- `testing_runware.py` - Basic single video generation (verified working)
- `example_using_helpers.py` - Using helper functions
- `example_4_scenes.py` - Complete 4-scene workflow
- `test_fastest_models.py` - Model comparison testing

---

## 🔧 Helper Function Reference

### RunwareVideoHelper

```python
helper = RunwareVideoHelper(api_key, api_url="https://api.runware.ai/v1")

# Upload image
image_id = helper.upload_image(image_path)

# Generate video
task_uuid, response = helper.generate_video(
    prompt="description",
    image_id="uuid",
    model="minimax:1@1",
    duration=6,
    width=1366,
    height=768
)

# Check status
status = helper.check_status(task_uuid)

# Poll until complete
result = helper.poll_until_complete(
    task_uuid,
    poll_interval=5,
    timeout=600,
    verbose=True
)

# Download video
success = helper.download_video(url, save_path)
```

### MultiSceneGenerator

```python
generator = MultiSceneGenerator(
    api_key="key",
    model="minimax:1@1",
    output_dir="results"
)

# Generate single scene
video_path = generator.generate_scene(scene_config)

# Generate all scenes
video_paths = generator.generate_all_scenes(scenes)

# Stitch scenes
final_video = generator.stitch_scenes(video_paths, "output.mp4")

# Complete workflow
final_video = generator.generate_complete_video(
    scenes,
    output_filename="final.mp4"
)
```

---

## ⚡ Performance Notes

- **Single video (6s):** ~4 minutes generation time
- **4-scene video (30s):** ~16-20 minutes total
- **Polling interval:** 5 seconds recommended
- **Timeout:** 10 minutes per scene recommended

---

## 🐛 Troubleshooting

### Image Upload Fails
- Check image format (JPEG, PNG supported)
- Verify file size (< 10MB recommended)
- Use `resize_for_model()` to ensure correct dimensions

### Video Generation Fails
- Verify model name is correct
- Check dimensions match model requirements
- Ensure duration is within model limits
- Use `MODEL_CONFIGS` for verified settings

### FFmpeg Stitching Fails
- Ensure FFmpeg is installed and in PATH
- Check all video files exist and are valid
- Verify videos have same codec/resolution
- Use absolute paths for video files

---

## 📝 Best Practices

1. **Always resize images** to model-specific dimensions before upload
2. **Use async delivery method** for video generation (required)
3. **Poll with reasonable intervals** (5s recommended, not faster)
4. **Handle errors gracefully** - video generation can fail
5. **Set appropriate timeouts** (10 minutes per scene)
6. **Clean up temporary files** after stitching
7. **Use MODEL_CONFIGS** for verified working configurations

---

## 🎯 ProductFlow Integration

These helpers are designed for the ProductFlow application workflow:

1. User uploads product image + fills form
2. OpenAI analyzes and generates scene descriptions
3. `MultiSceneGenerator` creates 4 videos from descriptions
4. FFmpeg stitches scenes into final 30-second video
5. User downloads complete marketing package

See `product-guidelines/` for complete ProductFlow specifications.

---

## 🚀 Next Steps for Fullstack Integration

### Backend API Routes

```python
# Suggested API endpoints using these helpers

POST /api/upload-image
→ Use helper.upload_image()
→ Return imageUUID

POST /api/generate-video
→ Use helper.generate_video()
→ Return taskUUID

GET /api/video-status/:taskId
→ Use helper.check_status()
→ Return current status

GET /api/download-video/:taskId
→ Use helper.download_video()
→ Return video file
```

### Frontend Integration

- Image upload component with dimension validation
- Progress polling UI (updates every 5 seconds)
- Video preview player
- Download button
- Error handling with user-friendly messages

### Database (Optional)

- Store task UUIDs for tracking
- Track generation status and progress
- Save video URLs and metadata
- Log costs per generation

### Error Handling

- Dimension validation before upload (use `validate_dimensions()`)
- Format conversion if needed (use `convert_image_format()`)
- Retry logic for failed generations
- User-friendly error messages

---

## 📚 Additional Documentation

- **API Flow Guide:** `../documentation/VIDEO_RW_API_FLOW.md` - Complete step-by-step Runware API integration
- **Model Reference:** `../documentation/video_models.md` - Available models and configurations
- **Product Specs:** `../product-guidelines/` - Complete ProductFlow specifications
