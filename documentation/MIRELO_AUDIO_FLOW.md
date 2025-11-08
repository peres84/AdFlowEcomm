# Mirelo.ai Audio Generation - Complete Integration Guide

**AI-Powered Sound Effects for Videos**

This document explains the step-by-step process for adding AI-generated sound effects to videos using the Mirelo.ai API.

---

## 📋 Overview

### What Mirelo Does

Mirelo.ai generates professional sound effects and background music for videos using AI. It analyzes your video content and creates contextually appropriate audio.

### Workflow

```
1. Create Customer Asset → Get upload URL
2. Upload Video → PUT request to pre-signed URL
3. Generate SFX → AI analyzes video and creates audio
4. Download Audio → Get generated audio files
5. Merge Video + Audio → Create final video with audio ✨
```

### Key Features

- **AI-Powered:** Analyzes video content for context-aware audio
- **Text Prompts:** Guide audio generation with descriptions
- **Multiple Samples:** Generate up to 4 variations
- **Model Versions:** v1.0 and v1.5 available
- **Creativity Control:** Adjust creativity coefficient (1-10)

---

## 🔑 Prerequisites

### API Key

Add to your `.env` file:

```bash
MIRELO_API_KEY=your_api_key_here
```

### Required Packages

```bash
pip install requests python-dotenv
```

### Input Requirements

- **Video Format:** MP4
- **Max Duration:** 10 seconds per generation
- **File Size:** Reasonable size for upload (< 100MB recommended)

---

## 🚀 Complete Workflow

### Step 1: Create Customer Asset

**Purpose:** Get a pre-signed upload URL for your video

**Endpoint:** `POST https://api.mirelo.ai/create-customer-asset`

**Request:**

```python
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "contentType": "video/mp4"
}

response = requests.post(
    "https://api.mirelo.ai/create-customer-asset",
    headers=headers,
    json=payload
)
```

**Response (200):**

```json
{
  "customer_asset_id": "550e8400-e29b-41d4-a716-446655440000",
  "upload_url": "https://presigned-url-for-upload..."
}
```

**What to Save:**
- `customer_asset_id` - Use in Step 3
- `upload_url` - Use in Step 2

---

### Step 2: Upload Video

**Purpose:** Upload your video file to Mirelo's storage

**Method:** `PUT` request to the pre-signed URL

**Request:**

```python
# Read video file
with open(video_path, "rb") as f:
    video_data = f.read()

# Upload using PUT (not POST!)
headers = {
    "Content-Type": "video/mp4"
}

response = requests.put(
    upload_url,  # From Step 1
    data=video_data,
    headers=headers
)
```

**Response:** 200 or 204 (success)

**Important:**
- ✅ Use `PUT` method (not POST)
- ✅ Set `Content-Type: video/mp4`
- ✅ Send raw video data (not JSON)
- ✅ No Authorization header needed (pre-signed URL)

---

### Step 3: Generate Sound Effects

**Purpose:** Generate AI-powered audio for your video

**Endpoint:** `POST https://api.mirelo.ai/video-to-sfx`

**Request:**

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "customer_asset_id": customer_asset_id,  # From Step 1
    "text_prompt": "Cinematic background music with smooth transitions",
    "model_version": "1.5",  # "1.0" or "1.5"
    "num_samples": 1,  # 1-4 variations
    "duration": 10,  # 1-10 seconds
    "creativity_coef": 5,  # 1-10
    "return_audio_only": False
}

response = requests.post(
    "https://api.mirelo.ai/video-to-sfx",
    headers=headers,
    json=payload
)
```

**Response (201):**

```json
{
  "output_paths": [
    "https://mirelo-output.s3.amazonaws.com/audio1.mp3",
    "https://mirelo-output.s3.amazonaws.com/audio2.mp3"
  ]
}
```

**Parameters Explained:**

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `customer_asset_id` | string | - | UUID from Step 1 (required) |
| `text_prompt` | string | - | Description of desired audio |
| `model_version` | string | "1.0", "1.5" | AI model version (default: "1.5") |
| `num_samples` | integer | 1-4 | Number of variations to generate |
| `duration` | number | 1-10 | Audio duration in seconds |
| `creativity_coef` | number | 1-10 | Creativity level (higher = more creative) |
| `return_audio_only` | boolean | - | Return only audio (no video context) |
| `start_offset` | number | 0+ | Start time offset in video |
| `steps` | number | 1-30 | Generation steps (more = higher quality) |
| `seed` | number | - | Random seed for reproducibility |

**Alternative: Use video_url**

Instead of `customer_asset_id`, you can provide a publicly accessible video URL:

```python
payload = {
    "video_url": "https://example.com/video.mp4",
    "text_prompt": "...",
    # ... other parameters
}
```

**Note:** You can use EITHER `customer_asset_id` OR `video_url`, but not both.

---

### Step 4: Download Audio

**Purpose:** Download the generated audio files

**Method:** Simple GET request

```python
def download_audio(url, save_path):
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False

# Download each audio file
for i, audio_url in enumerate(output_paths, 1):
    save_path = f"audio_sample_{i}.mp3"
    download_audio(audio_url, save_path)
```

---

### Step 5: Merge Video and Audio ✨

**Purpose:** Combine video and audio into final video file

**Method:** FFmpeg command to merge streams

**Using the Helper Utility:**

```python
from scripts.utils.video_audio_merger import merge_video_audio

# Merge video and audio
success = merge_video_audio(
    video_path="original_video.mp4",
    audio_path="generated_audio.mp3",
    output_path="final_video_with_audio.mp4"
)
```

**Direct FFmpeg Command:**

```python
import subprocess

def merge_video_audio(video_path, audio_path, output_path):
    cmd = [
        "ffmpeg",
        "-i", video_path,      # Input video
        "-i", audio_path,      # Input audio
        "-c:v", "copy",        # Copy video (no re-encoding)
        "-c:a", "aac",         # Convert audio to AAC
        "-map", "0:v:0",       # Map video from first input
        "-map", "1:a:0",       # Map audio from second input
        "-shortest",           # End when shortest stream ends
        "-y",                  # Overwrite output
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.returncode == 0
```

**Why This Step:**
- Creates a single, ready-to-use video file
- No need to manually combine files later
- Video is not re-encoded (fast, lossless)
- Audio is converted to AAC for universal compatibility

**Output:**
- `original_video_with_audio.mp4` - Complete video ready for use!

---

## 📝 Complete Code Example

```python
"""
Complete Mirelo.ai Audio Generation Example with Video Merging
Automatically finds first video in vid_test/ folder
"""

import requests
import subprocess
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("MIRELO_API_KEY")
API_URL = "https://api.mirelo.ai"

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VID_TEST_DIR = os.path.join(SCRIPT_DIR, "vid_test")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
TEXT_PROMPT = "Cinematic background music with smooth transitions"


def find_first_video():
    """Find first video in vid_test directory."""
    if not os.path.exists(VID_TEST_DIR):
        return None
    
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    files = os.listdir(VID_TEST_DIR)
    
    for file in sorted(files):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            return os.path.join(VID_TEST_DIR, file)
    
    return None


def create_customer_asset(api_key):
    """Step 1: Create customer asset."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # Mirelo uses x-api-key
    }
    
    payload = {"contentType": "video/mp4"}
    
    response = requests.post(
        f"{API_URL}/create-customer-asset",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    
    data = response.json()
    return data["customer_asset_id"], data["upload_url"]


def upload_video(upload_url, video_path):
    """Step 2: Upload video."""
    with open(video_path, "rb") as f:
        video_data = f.read()
    
    headers = {"Content-Type": "video/mp4"}
    
    response = requests.put(upload_url, data=video_data, headers=headers)
    response.raise_for_status()


def generate_sfx(api_key, customer_asset_id, text_prompt):
    """Step 3: Generate sound effects."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # Mirelo uses x-api-key
    }
    
    payload = {
        "customer_asset_id": customer_asset_id,
        "text_prompt": text_prompt,
        "model_version": "1.5",
        "num_samples": 1,
        "duration": 10,
        "creativity_coef": 5
    }
    
    response = requests.post(
        f"{API_URL}/video-to-sfx",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    
    data = response.json()
    return data["output_paths"]


def download_audio(url, save_path):
    """Step 4: Download audio."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def merge_video_audio(video_path, audio_path, output_path):
    """Step 5: Merge video and audio."""
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-y",
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True, text=True, check=True)


def main():
    """Complete workflow with video merging and auto-detection."""
    print("🎵 Starting audio generation...")
    
    # Step 0: Find video
    print("\n📂 Looking for videos in vid_test/...")
    video_path = find_first_video()
    
    if not video_path:
        print("❌ No video found! Add a video to vid_test/")
        return
    
    print(f"📹 Found: {os.path.basename(video_path)}")
    
    # Ensure results folder exists
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Step 1: Create asset
    print("\n1️⃣ Creating customer asset...")
    customer_asset_id, upload_url = create_customer_asset(API_KEY)
    print(f"   Asset ID: {customer_asset_id}")
    
    # Step 2: Upload video
    print("\n2️⃣ Uploading video...")
    upload_video(upload_url, video_path)
    print("   ✅ Upload complete")
    
    # Step 3: Generate audio
    print("\n3️⃣ Generating sound effects...")
    audio_urls = generate_sfx(API_KEY, customer_asset_id, TEXT_PROMPT)
    print(f"   ✅ Generated {len(audio_urls)} audio file(s)")
    
    # Step 4: Download audio
    print("\n4️⃣ Downloading audio...")
    audio_filename = f"audio_{customer_asset_id}_sample1.mp3"
    audio_path = os.path.join(RESULTS_DIR, audio_filename)
    download_audio(audio_urls[0], audio_path)
    print(f"   ✅ Saved: {audio_filename}")
    
    # Step 5: Merge video and audio
    print("\n5️⃣ Merging video and audio...")
    video_basename = os.path.splitext(os.path.basename(video_path))[0]
    output_filename = f"{video_basename}_with_audio.mp4"
    output_path = os.path.join(RESULTS_DIR, output_filename)
    merge_video_audio(video_path, audio_path, output_path)
    print(f"   ✅ Final video: {output_filename}")
    
    print("\n✅ SUCCESS!")
    print(f"\n📁 File Organization:")
    print(f"   Original: vid_test/{os.path.basename(video_path)}")
    print(f"   Audio: results/{audio_filename}")
    print(f"   Final: results/{output_filename}")


if __name__ == "__main__":
    main()
```

### Usage Example

**Step 1: Setup**
```bash
# Create folder structure
mkdir -p scripts/testing_audio/vid_test
mkdir -p scripts/testing_audio/results

# Add your video
cp your_video.mp4 scripts/testing_audio/vid_test/
```

**Step 2: Run**
```bash
cd scripts/testing_audio
python testing_mirelo.py
```

**Step 3: Results**
```
scripts/testing_audio/
├── vid_test/
│   └── your_video.mp4              ← Original (unchanged)
└── results/
    ├── audio_{id}_sample1.mp3      ← Generated audio
    └── your_video_with_audio.mp4   ← Final video ✅
```

---

## 🎯 Text Prompt Examples

Good prompts help guide the AI to generate appropriate audio:

### Product Videos

```python
"Professional product showcase music, modern and clean, upbeat tempo"
"Luxury brand background music, sophisticated and elegant"
"Tech product reveal, futuristic electronic sounds"
```

### Lifestyle Videos

```python
"Casual lifestyle background music, warm and friendly atmosphere"
"Energetic workout music, motivating and powerful"
"Relaxing spa ambiance, calm and peaceful sounds"
```

### Cinematic Videos

```python
"Cinematic trailer music, epic and dramatic"
"Emotional storytelling background, inspiring and uplifting"
"Suspenseful atmosphere, building tension"
```

### Social Media

```python
"Trendy social media background music, catchy and engaging"
"Fun and playful sounds for short-form content"
"Attention-grabbing intro music for reels"
```

---

## ⚠️ Error Handling

### Common Errors

#### 400 - Invalid Request

```json
{
  "detail": "Invalid request body",
  "errors": {
    "duration": ["Must be between 1 and 10"]
  }
}
```

**Solution:** Check parameter values and types

---

#### 401 - Unauthorized

```json
{
  "detail": "Invalid or missing API key"
}
```

**Solution:** Verify `MIRELO_API_KEY` in `.env`

---

#### 403 - Forbidden

```json
{
  "detail": "Insufficient permissions"
}
```

**Solution:** Check API key permissions or account status

---

#### 500 - Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

**Solution:** Retry the request or contact support

---

### Error Handling Pattern

```python
try:
    # Step 1: Create asset
    customer_asset_id, upload_url = create_customer_asset(api_key)
    
    # Step 2: Upload video
    upload_video(upload_url, video_path)
    
    # Step 3: Generate audio
    audio_urls = generate_sfx(api_key, customer_asset_id, prompt)
    
    # Step 4: Download
    for url in audio_urls:
        download_audio(url, save_path)
        
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(f"Details: {e.response.text}")
    
except Exception as e:
    print(f"Error: {str(e)}")
```

---

## 🎛️ Parameter Tuning Guide

### Model Version

- **v1.0:** Original model, faster generation
- **v1.5:** Latest model, better quality (recommended)

### Creativity Coefficient (1-10)

- **1-3:** Conservative, stays close to prompt
- **4-7:** Balanced creativity (recommended)
- **8-10:** Highly creative, more experimental

### Number of Samples (1-4)

- **1:** Single audio file (fastest)
- **2-4:** Multiple variations to choose from

### Duration (1-10 seconds)

- Match your video length
- Max 10 seconds per generation
- For longer videos, use `/long-video-to-sfx` endpoint

### Steps (1-30)

- **1-10:** Fast generation, lower quality
- **11-20:** Balanced (default)
- **21-30:** Slower, highest quality

---

## 🚀 Integration with ProductFlow

### Complete Workflow Integration

```
1. User uploads product image
2. Runware generates 4 video scenes (7s, 7s, 10s, 6s)
3. FFmpeg stitches scenes → 30-second video (no audio)
4. Place stitched video in vid_test/ folder
5. Mirelo auto-detects video and generates audio
6. FFmpeg merges video + audio → Final product with audio ✅
```

### File Organization in ProductFlow

```
scripts/testing_audio/
├── vid_test/
│   └── product_video_30s.mp4       ← From Runware (stitched scenes)
└── results/
    ├── audio_{id}_sample1.mp3      ← Generated by Mirelo
    └── product_video_30s_with_audio.mp4 ← Final product ✅
```

### Output Files

After complete workflow:
- `scene1.mp4`, `scene2.mp4`, `scene3.mp4`, `scene4.mp4` - Individual scenes (Runware)
- `product_video_30s.mp4` - Stitched video in vid_test/ (no audio)
- `audio_{id}_sample1.mp3` - AI-generated audio in results/
- `product_video_30s_with_audio.mp4` - **Complete product in results/** ✅

### Scene-Specific Audio

Generate different audio for each scene:

```python
scenes = [
    {"video": "scene1_hook.mp4", "prompt": "Attention-grabbing intro music"},
    {"video": "scene2_problem.mp4", "prompt": "Tension-building background"},
    {"video": "scene3_solution.mp4", "prompt": "Uplifting, inspiring music"},
    {"video": "scene4_cta.mp4", "prompt": "Confident, professional close"}
]

for scene in scenes:
    audio = generate_audio_for_scene(scene["video"], scene["prompt"])
```

---

## 📊 Best Practices

### 1. Video Preparation

✅ **DO:**
- Use high-quality video input
- Keep videos under 10 seconds per generation
- Use clear, stable footage

❌ **DON'T:**
- Upload corrupted or incomplete videos
- Exceed duration limits
- Use extremely low-quality footage

### 2. Text Prompts

✅ **DO:**
- Be specific about mood and style
- Mention tempo and energy level
- Reference genre or context

❌ **DON'T:**
- Use vague prompts like "good music"
- Include unrelated instructions
- Make prompts too long

### 3. API Usage

✅ **DO:**
- Reuse customer_asset_id for same video
- Handle errors gracefully
- Download audio immediately

❌ **DON'T:**
- Create new assets for same video
- Ignore error responses
- Assume URLs are permanent

---

## 📁 File Organization

### Testing Script Structure

```
scripts/testing_audio/
├── vid_test/                    ← Place input videos here
│   └── your_video.mp4          ← Original videos (stay here)
├── results/                     ← Generated files (auto-created)
│   ├── audio_{id}_sample1.mp3  ← Generated audio
│   └── your_video_with_audio.mp4 ← Final video with audio
└── testing_mirelo.py            ← Testing script
```

### How It Works

1. **Add video to `vid_test/`** - Place any video file in this folder
2. **Run script** - It automatically finds the first video
3. **Get results in `results/`** - Audio and final video saved here
4. **Original stays in `vid_test/`** - Unchanged

### Supported Video Formats

- MP4, AVI, MOV, MKV, WEBM, FLV
- Script automatically detects first video (alphabetically)

---

## 📚 Additional Resources

- **Testing Script:** `../scripts/testing_audio/testing_mirelo.py` (complete workflow with auto-detection)
- **Video-Audio Merger:** `../scripts/utils/video_audio_merger.py`
- **Runware Integration:** `VIDEO_RW_API_FLOW.md`
- **Helper Functions:** `../scripts/utils/README.md`

---

## 🎬 FFmpeg Requirements

The video-audio merging feature requires FFmpeg to be installed:

**Installation:**
- **Windows:** `choco install ffmpeg`
- **Mac:** `brew install ffmpeg`
- **Linux:** `apt-get install ffmpeg`

**Verify Installation:**
```bash
ffmpeg -version
```

**What FFmpeg Does:**
- Merges video and audio streams
- No video re-encoding (fast, lossless)
- Converts audio to AAC for compatibility
- Handles duration mismatches automatically

---

**Last Updated:** Based on Mirelo.ai API documentation + FFmpeg video merging
