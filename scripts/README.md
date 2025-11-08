# Video Generation Helper Scripts

Professional utilities for Runware video generation workflows.

## 📁 Files

### `video_helpers.py`
Core video generation utilities.

**Classes:**
- `RunwareVideoHelper` - Main helper class for Runware API operations

**Functions:**
- `resize_for_model()` - Resize images to model-specific dimensions
- `stitch_videos_ffmpeg()` - Stitch multiple videos using FFmpeg
- `get_video_info()` - Get video metadata using FFprobe

**Constants:**
- `MODEL_CONFIGS` - Pre-configured settings for different video models

### `scene_generator.py`
Multi-scene video generation for ProductFlow workflow.

**Classes:**
- `SceneConfig` - Configuration for a single video scene
- `MultiSceneGenerator` - Generate and stitch multiple scenes

**Functions:**
- `create_standard_scenes()` - Create standard 4-scene product video configuration

### `resizer_img.py`
Professional image resizing for API dimension requirements.

**Functions:**
- `resize_image()` - Resize with quality control and aspect ratio options
- `get_image_dimensions()` - Get image dimensions without full load
- `validate_dimensions()` - Check if image meets requirements

### `extension_changer_img.py`
Image format conversion for API compatibility.

**Functions:**
- `convert_image_format()` - Convert between formats (JPEG, PNG, WEBP, etc.)
- `get_image_format()` - Check current image format
- `is_format_supported()` - Validate format compatibility
- `convert_for_api()` - Auto-convert for specific APIs
- `batch_convert()` - Convert multiple images at once

---

## 🚀 Quick Start

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

## 📖 Examples

See the `testing/` directory for complete examples:

- `testing_runware.py` - Basic single video generation
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
