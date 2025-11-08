# Helper Functions Summary

Quick reference for all video generation helper utilities.

---

## 📁 Available Helpers

### 1. Image Resizing (`scripts/resizer_img.py`)

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

**Features:**
- Professional quality resizing (LANCZOS algorithm)
- RGBA to RGB conversion for JPEG
- Aspect ratio preservation option
- Validation and error handling

**Use Case:** When Runware API rejects images due to `invalidFrameImageWidth` errors

---

### 2. Format Conversion (`scripts/extension_changer_img.py`)

**Purpose:** Convert images between formats for API compatibility

**Main Function:**
```python
from scripts.extension_changer_img import convert_image_format

converted_path = convert_image_format(
    image_path="product.png",
    target_format="JPEG"
)
```

**Features:**
- Supports JPEG, PNG, WEBP, BMP, TIFF, GIF
- Transparency handling
- API-specific conversion helpers
- Batch conversion support

**Use Case:** When API requires specific image formats

---

### 3. Video Generation (`scripts/video_helpers.py`)

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

**Features:**
- Complete Runware API wrapper
- Automatic polling with timeout
- Error handling
- Model configurations

---

### 4. Multi-Scene Generation (`scripts/scene_generator.py`)

**Purpose:** Generate and stitch 4-scene product videos

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

**Features:**
- 4-scene workflow (Hook, Problem, Solution, CTA)
- Automatic FFmpeg stitching
- Progress tracking
- Error recovery

---

## 🎯 Quick Decision Guide

**Need to resize an image?**
→ Use `scripts/resizer_img.py`

**Need to convert image format?**
→ Use `scripts/extension_changer_img.py`

**Need to generate a single video?**
→ Use `scripts/video_helpers.py`

**Need to generate 4-scene product video?**
→ Use `scripts/scene_generator.py`

---

## 📖 Complete Documentation

- **API Flow:** `documentation/VIDEO_RW_API_FLOW.md`
- **Helper Details:** `scripts/README.md`
- **Model Info:** `documentation/video_models.md`
- **Product Specs:** `product-guidelines/`

---

## ✅ Verification

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

## 🚀 Next Steps for Fullstack Integration

1. **Backend API Routes:**
   - POST `/api/upload-image` → Use `upload_image()`
   - POST `/api/generate-video` → Use `generate_video()`
   - GET `/api/video-status/:taskId` → Use `check_status()`
   - GET `/api/download-video/:taskId` → Use `download_video()`

2. **Frontend Integration:**
   - Image upload component
   - Progress polling UI
   - Video preview player
   - Download button

3. **Database (Optional):**
   - Store task UUIDs
   - Track generation status
   - Save video URLs
   - Log costs

4. **Error Handling:**
   - Dimension validation before upload
   - Format conversion if needed
   - Retry logic for failed generations
   - User-friendly error messages

See `documentation/VIDEO_RW_API_FLOW.md` for complete implementation details.
