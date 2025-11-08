# Complete Video Generation Workflow

**End-to-End Guide: From Image to Final Video with Audio**

This guide combines Runware (video generation) and Mirelo (audio generation) to create complete, production-ready videos with AI-generated sound effects.

---

## 📋 Overview

### Complete Workflow

```
Step 1: Runware Video Generation
├─ Upload product image
├─ Generate video (6 seconds)
└─ Download video → Save to vid_test/

Step 2: Mirelo Audio Generation
├─ Auto-detect video in vid_test/
├─ Generate AI audio
├─ Download audio → Save to results/
└─ Merge video + audio → Final video in results/

Output: Complete video with audio ready for use! ✅
```

### Time Estimate

- **Runware Video:** ~4 minutes (6-second video)
- **Mirelo Audio:** ~2-3 minutes (audio generation + merge)
- **Total:** ~6-7 minutes for complete workflow

### Requirements

- **Runware API Key** - For video generation
- **Mirelo API Key** - For audio generation
- **FFmpeg** - For video-audio merging
- **Python 3.8+** - With required packages

---

## 🎬 Part 1: Video Generation (Runware)

### Step 1.1: Prepare Your Image

**Requirements:**
- Format: JPEG or PNG
- Dimensions: Will be resized to 1366x768
- Quality: High resolution recommended

**Location:**
```
scripts/testing_video/imgs_test/your_image.jpg
```

### Step 1.2: Configure Video Generation

**Edit:** `scripts/testing_video/testing_runware_.py`

```python
# Video prompt
SCRIPT = "Your video description here"

# Model configuration (verified working)
MODEL = "minimax:1@1"
MODEL_WIDTH = 1366
MODEL_HEIGHT = 768
MODEL_DURATION = 6  # seconds
```

### Step 1.3: Run Video Generation

```bash
cd scripts/testing_video
python testing_runware_.py
```

**What Happens:**
1. Image uploaded to Runware (base64 encoded)
2. Video generation request submitted
3. Polls every 5 seconds for completion
4. Downloads video to `results/` folder

**Output:**
```
scripts/testing_video/results/
└── {task_uuid}.mp4  ← Generated video (no audio)
```

### Step 1.4: Move Video for Audio Processing

**Copy video to Mirelo input folder:**
```bash
# Windows
copy scripts\testing_video\results\*.mp4 scripts\testing_audio\vid_test\

# Mac/Linux
cp scripts/testing_video/results/*.mp4 scripts/testing_audio/vid_test/
```

---

## 🎵 Part 2: Audio Generation (Mirelo)

### Step 2.1: Configure Audio Generation

**Edit:** `scripts/testing_audio/testing_mirelo.py`

```python
# Audio prompt (describe desired audio)
TEXT_PROMPT = "Cinematic background music with smooth transitions"

# Audio parameters
MODEL_VERSION = "1.5"      # Latest model
NUM_SAMPLES = 1            # Number of variations
DURATION = 10              # Max 10 seconds
CREATIVITY_COEF = 5        # 1-10 (higher = more creative)
```

### Step 2.2: Run Audio Generation

```bash
cd scripts/testing_audio
python testing_mirelo.py
```

**What Happens:**
1. Auto-detects first video in `vid_test/`
2. Uploads video to Mirelo
3. Generates AI audio based on prompt
4. Downloads audio to `results/`
5. Merges video + audio using FFmpeg
6. Saves final video to `results/`

**Output:**
```
scripts/testing_audio/
├── vid_test/
│   └── your_video.mp4              ← Original (unchanged)
└── results/
    ├── audio_{id}_sample1.mp3      ← Generated audio
    └── your_video_with_audio.mp4   ← Final video ✅
```

---

## 📊 Detailed API Workflows

### Runware API Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RUNWARE VIDEO GENERATION                 │
└─────────────────────────────────────────────────────────────┘

1. PREPARE IMAGE
   ├─ Resize to 1366x768
   ├─ Convert to JPEG
   └─ Encode to base64

2. UPLOAD IMAGE
   ├─ POST /v1
   ├─ taskType: "imageUpload"
   ├─ Headers: Authorization: Bearer {api_key}
   └─ Response: imageUUID

3. SUBMIT VIDEO REQUEST
   ├─ POST /v1
   ├─ taskType: "videoInference"
   ├─ model: "minimax:1@1"
   ├─ deliveryMethod: "async"
   ├─ frameImages: [imageUUID]
   └─ Response: taskUUID (acknowledgment)

4. POLL FOR COMPLETION
   ├─ POST /v1 (every 5 seconds)
   ├─ taskType: "getResponse"
   ├─ Check response.data[] for status
   ├─ Status: "processing" → continue polling
   ├─ Status: "success" → video ready
   └─ Status: "error" → check errors[]

5. DOWNLOAD VIDEO
   ├─ GET videoURL from response
   ├─ Save as MP4
   └─ Total time: ~244 seconds (4 minutes)
```

### Mirelo API Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MIRELO AUDIO GENERATION                  │
└─────────────────────────────────────────────────────────────┘

1. FIND VIDEO
   ├─ Auto-detect in vid_test/
   ├─ Supported: MP4, AVI, MOV, MKV, WEBM, FLV
   └─ Takes first file (alphabetically)

2. CREATE CUSTOMER ASSET
   ├─ POST /create-customer-asset
   ├─ Headers: x-api-key: {api_key}
   ├─ contentType: "video/mp4"
   └─ Response: customer_asset_id, upload_url

3. UPLOAD VIDEO
   ├─ PUT to upload_url (pre-signed)
   ├─ Headers: Content-Type: video/mp4
   ├─ Send raw video data
   └─ Response: 200/204 success

4. GENERATE AUDIO
   ├─ POST /video-to-sfx
   ├─ Headers: x-api-key: {api_key}
   ├─ customer_asset_id from step 2
   ├─ text_prompt: audio description
   ├─ model_version: "1.5"
   └─ Response: output_paths[] (audio URLs)

5. DOWNLOAD AUDIO
   ├─ GET audio URL
   ├─ Save as MP3 to results/
   └─ Note: Mirelo returns MP4 with video+audio

6. MERGE VIDEO + AUDIO
   ├─ FFmpeg command
   ├─ -i original_video.mp4
   ├─ -i generated_audio.mp3
   ├─ -c:v copy (no re-encoding)
   ├─ -c:a aac (convert to AAC)
   ├─ -map 0:v:0 (video from input 0)
   ├─ -map 1:a:0 (audio from input 1)
   └─ Output: final_video_with_audio.mp4
```

---

## 🔑 API Authentication

### Runware

**Header Format:**
```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {RUNWARE_API_KEY}"
}
```

**Environment Variable:**
```bash
RUNWARE_API_KEY=your_runware_api_key
```

### Mirelo

**Header Format:**
```python
headers = {
    "Content-Type": "application/json",
    "x-api-key": MIRELO_API_KEY
}
```

**Environment Variable:**
```bash
MIRELO_API_KEY=your_mirelo_api_key
```

---

## 📁 File Organization

### Project Structure

```
AdFlowEcomm/
├── .env                          ← API keys
│
├── scripts/
│   ├── testing_video/
│   │   ├── imgs_test/
│   │   │   └── product.jpg      ← Input image
│   │   ├── results/
│   │   │   └── video.mp4        ← Generated video (no audio)
│   │   └── testing_runware_.py
│   │
│   ├── testing_audio/
│   │   ├── vid_test/
│   │   │   └── video.mp4        ← Copy from testing_video/results/
│   │   ├── results/
│   │   │   ├── audio.mp3        ← Generated audio
│   │   │   └── video_with_audio.mp4 ← Final output ✅
│   │   └── testing_mirelo.py
│   │
│   └── utils/
│       ├── file_helpers.py
│       ├── api_helpers.py
│       ├── video_audio_merger.py
│       └── README.md
│
└── documentation/
    ├── VIDEO_RW_API_FLOW.md      ← Detailed Runware guide
    ├── MIRELO_AUDIO_FLOW.md      ← Detailed Mirelo guide
    └── COMPLETE_VIDEO_WORKFLOW.md ← This file
```

---

## 🎯 Quick Start Guide

### Prerequisites

**1. Install Dependencies:**
```bash
pip install requests pillow python-dotenv
```

**2. Install FFmpeg:**
```bash
# Windows
choco install ffmpeg

# Mac
brew install ffmpeg

# Linux
apt-get install ffmpeg
```

**3. Configure API Keys:**

Create `.env` in project root:
```bash
RUNWARE_API_KEY=your_runware_key
MIRELO_API_KEY=your_mirelo_key
```

### Complete Workflow

**Step 1: Generate Video**
```bash
# Add image to imgs_test/
cp your_product.jpg scripts/testing_video/imgs_test/

# Run video generation
cd scripts/testing_video
python testing_runware_.py

# Wait ~4 minutes
# Output: results/{uuid}.mp4
```

**Step 2: Generate Audio & Merge**
```bash
# Copy video to audio input folder
cp results/*.mp4 ../testing_audio/vid_test/

# Run audio generation + merge
cd ../testing_audio
python testing_mirelo.py

# Wait ~2-3 minutes
# Output: results/{video}_with_audio.mp4 ✅
```

**Step 3: Get Your Video**
```bash
# Final video location:
scripts/testing_audio/results/{video}_with_audio.mp4
```

---

## 🎨 Customization Options

### Video Generation (Runware)

**Prompt Engineering:**
```python
# Product showcase
SCRIPT = "Professional product photography with cinematic lighting"

# Lifestyle scene
SCRIPT = "Person using product in modern home, natural lighting"

# Action shot
SCRIPT = "Dynamic product demonstration with motion and energy"
```

**Model Options:**
```python
# MiniMax 01 Base (6s) - Fastest ✅
MODEL = "minimax:1@1"
MODEL_DURATION = 6

# MiniMax Hailuo 02 (10s)
MODEL = "minimax:hailuo@2"
MODEL_DURATION = 10
```

### Audio Generation (Mirelo)

**Prompt Examples:**
```python
# Cinematic
TEXT_PROMPT = "Epic cinematic music with orchestral elements"

# Upbeat
TEXT_PROMPT = "Energetic upbeat music with positive vibes"

# Ambient
TEXT_PROMPT = "Calm ambient background music, subtle and professional"

# Product-specific
TEXT_PROMPT = "Tech product reveal music, modern and innovative"
```

**Creativity Control:**
```python
# Conservative (stays close to prompt)
CREATIVITY_COEF = 3

# Balanced (recommended)
CREATIVITY_COEF = 5

# Creative (more experimental)
CREATIVITY_COEF = 8
```

---

## 🔧 Troubleshooting

### Runware Issues

**Problem:** "Invalid frame image width"
- **Solution:** Image automatically resized to 1366x768

**Problem:** "Task timeout"
- **Solution:** Video generation takes ~4 minutes, be patient

**Problem:** "API key invalid"
- **Solution:** Check `RUNWARE_API_KEY` in `.env`

### Mirelo Issues

**Problem:** "No video found in vid_test/"
- **Solution:** Copy video from `testing_video/results/` to `testing_audio/vid_test/`

**Problem:** "FFmpeg AAC encoder error"
- **Solution:** Script automatically tries alternative method (audio copy)

**Problem:** "Merge failed"
- **Solution:** Update FFmpeg: `choco upgrade ffmpeg`

### FFmpeg Issues

**Problem:** "FFmpeg not found"
- **Solution:** Install FFmpeg (see installation instructions above)

**Problem:** "Experimental codec error"
- **Solution:** Script uses `-strict -2` flag automatically

---

## 💡 Best Practices

### Video Generation

✅ **DO:**
- Use high-quality source images
- Write clear, descriptive prompts
- Wait for completion (don't interrupt)
- Save generated videos with meaningful names

❌ **DON'T:**
- Use very low resolution images
- Make prompts too vague
- Poll faster than 5 seconds
- Delete videos before audio generation

### Audio Generation

✅ **DO:**
- Match audio style to video content
- Use descriptive audio prompts
- Keep creativity coefficient balanced (5)
- Test different prompts for best results

❌ **DON'T:**
- Use generic prompts like "good music"
- Set creativity too high (unpredictable)
- Delete original video after merge
- Skip FFmpeg installation

### File Management

✅ **DO:**
- Organize videos by project/date
- Keep originals separate from outputs
- Use descriptive filenames
- Back up important videos

❌ **DON'T:**
- Mix input and output folders
- Overwrite original videos
- Delete intermediate files immediately
- Use special characters in filenames

---

## 📊 Cost Estimation

### Runware

- **Video Generation:** ~$0.18 per 6-second video
- **Image Upload:** Included
- **Polling:** Free

### Mirelo

- **Audio Generation:** Varies by duration and model
- **Video Upload:** Included
- **Processing:** Per-request pricing

**Total Estimate:** ~$0.20-0.30 per complete video with audio

---

## 🚀 Advanced Usage

### Batch Processing

**Generate multiple videos:**
```python
# Loop through images
for image in image_list:
    image_id = upload_image(API_KEY, image)
    task_uuid = generate_video(API_KEY, prompt, image_id)
    # Poll and download...
```

### Custom Audio Mixing

**Use helper utilities:**
```python
from scripts.utils.video_audio_merger import add_background_music

# Add background music at 30% volume
add_background_music(
    video_path="video.mp4",
    music_path="music.mp3",
    output_path="output.mp4",
    music_volume=0.3
)
```

### Automated Workflow

**Combine both steps:**
```python
# 1. Generate video with Runware
video_path = generate_runware_video(image_path, prompt)

# 2. Move to Mirelo input
shutil.copy(video_path, "scripts/testing_audio/vid_test/")

# 3. Generate audio and merge
final_video = generate_mirelo_audio(video_path, audio_prompt)

# 4. Done!
print(f"Final video: {final_video}")
```

---

## 📚 Additional Resources

### Documentation

- **Runware Details:** [VIDEO_RW_API_FLOW.md](VIDEO_RW_API_FLOW.md)
- **Mirelo Details:** [MIRELO_AUDIO_FLOW.md](MIRELO_AUDIO_FLOW.md)
- **Helper Functions:** [../scripts/utils/README.md](../scripts/utils/README.md)
- **Video Models:** [video_models.md](video_models.md)

### Testing Scripts

- **Video Generation:** `scripts/testing_video/testing_runware_.py`
- **Audio Generation:** `scripts/testing_audio/testing_mirelo.py`

### Helper Utilities

- **File Operations:** `scripts/utils/file_helpers.py`
- **API Helpers:** `scripts/utils/api_helpers.py`
- **Video-Audio Merger:** `scripts/utils/video_audio_merger.py`

---

## ✅ Success Checklist

### Before Starting

- [ ] API keys configured in `.env`
- [ ] FFmpeg installed and in PATH
- [ ] Python packages installed
- [ ] Product image ready

### After Video Generation

- [ ] Video downloaded to `testing_video/results/`
- [ ] Video quality checked
- [ ] Video copied to `testing_audio/vid_test/`

### After Audio Generation

- [ ] Audio generated successfully
- [ ] Video and audio merged
- [ ] Final video plays correctly
- [ ] Audio syncs with video

### Final Delivery

- [ ] Video quality approved
- [ ] Audio quality approved
- [ ] File size acceptable
- [ ] Ready for platform upload

---

## 🎉 Summary

**Complete Workflow:**
1. **Runware** generates video from image (~4 min)
2. **Mirelo** generates audio from video (~2 min)
3. **FFmpeg** merges video + audio (instant)
4. **Result:** Production-ready video with audio! ✅

**Total Time:** ~6-7 minutes from image to final video

**Output Quality:**
- Video: 1366x768, 6 seconds, MP4
- Audio: AI-generated, synced, AAC
- Final: Professional, ready for social media

**Next Steps:**
- Upload to Instagram Reels, TikTok, YouTube Shorts
- Use in marketing campaigns
- Share on social media
- Integrate into ProductFlow application

---

**Last Updated:** Complete workflow guide with Runware + Mirelo integration
