# ProductFlow - Final Tech Stack & Architecture
## Updated with OpenAI + Runware Only

---

## TECHNOLOGY STACK

### Language Models & Analysis
- **OpenAI API** - ALL text analysis, prompt generation, and optimization
  - Analyzes product images
  - Analyzes onboarding data
  - Analyzes logos
  - Generates image prompts for Runware
  - Generates video scene descriptions for Runware
  - Analyzes dialog for caption extraction

### Image Generation
- **Runware.ai** - Professional product image generation
  - Input: OpenAI-optimized image prompts
  - Output: 4-6 professional 1024x1024 images
  - Features: Logo integration, brand color matching

### Video Generation
- **Runware.ai** - Professional video scene generation
  - Input: OpenAI scene descriptions with audio/music/dialog guidance
  - Output: 4 separate MP4 scenes (7s, 7s, 10s, 6s)
  - Features: Professional quality, engagement-focused audio
  - Stitched into: Final 30-second vertical video

### Video Processing
- **FFmpeg** - Lossless video concatenation
  - Stitches 4 scene videos in sequence
  - Output: Final 30-second sequence.mp4
  - No re-encoding = no quality loss

### Audio/Caption Processing
- **Speech-to-Text API** (OpenAI Whisper or similar)
  - Extracts dialog/narration from generated video
  - Generates captions with timing
  - Output: SRT files or hardcoded captions

---

## DATA FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER UPLOADS                                  │
│                      Product Image + Logo                               │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        OPENAI ANALYSIS                                  │
│  Analyzes: Product image, onboarding, logo, brand characteristics      │
│  Output: Optimized prompts for Runware                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
        ┌─────────────────────────┴─────────────────────────┐
        ↓                                                   ↓
    ┌──────────────────┐                      ┌──────────────────┐
    │  IMAGE BRANCH    │                      │  VIDEO BRANCH    │
    │  RUNWARE.AI      │                      │  OPENAI ANALYSIS │
    │                  │                      │                  │
    │ 4 Image Prompts  │                      │ 4 Scene Desc w/  │
    │     ↓            │                      │ Audio/Music/     │
    │ 4-6 Images       │                      │ Dialog Guidance  │
    │ 1024x1024        │                      │      ↓           │
    │ With Logo        │                      │  RUNWARE.AI      │
    │                  │                      │  Video Generation│
    │                  │                      │      ↓           │
    │                  │                      │  4 MP4 Scenes    │
    │                  │                      │ (7s,7s,10s,6s)   │
    └──────────────────┘                      └──────────────────┘
        ↓                                              ↓
        │                                    ┌────────────────┐
        │                                    │  FFMPEG        │
        │                                    │  Stitch 4      │
        │                                    │  Scenes        │
        │                                    │      ↓         │
        └────────────────────┬───────────────┤ 30sec Video    │
                             ↓               └────────────────┘
                    ┌─────────────────┐              ↓
                    │ USER DOWNLOADS: │      ┌──────────────┐
                    │ - Images        │      │ SPEECH-TO-   │
                    │ - Video         │      │ TEXT API     │
                    │ - Optional:     │      │ (Optional)   │
                    │   Captions      │      │      ↓       │
                    │   Transcript    │      │ Captions/    │
                    └─────────────────┘      │ SRT/Trans    │
                                             └──────────────┘
```

---

## STEP-BY-STEP PROCESS

### STEP 1: Onboarding Form
- User enters: Product name, category, audience, benefit, brand color, tone, platform, website, logo (optional)
- Data stored in session memory

### STEP 2: Product Image & Logo Upload
- User uploads product image (required)
- User optionally uploads logo (PNG/JPG/SVG)
- Images stored temporarily in session

### STEP 3: Image Generation
1. **OpenAI analyzes:**
   - Product image characteristics
   - Onboarding data requirements
   - Logo placement strategy
   
2. **OpenAI generates:** 4 detailed image prompts optimized for Runware
   
3. **Runware generates:** 4-6 professional images (1024x1024)
   - With logo naturally integrated (if provided)
   - Matching brand color and tone
   - Ready for social media use

### STEP 4: Image Preview
- User sees gallery of original + generated images
- Can download individual images
- Reviews logo integration

### STEP 5: Video Scene Generation
1. **OpenAI analyzes:**
   - All product images
   - Onboarding data
   - Brand requirements
   
2. **OpenAI generates:** 4 detailed scene descriptions including:
   - Visual description
   - Camera movements
   - Lighting and mood
   - **Background music style** (e.g., "energetic electronic, upbeat tempo")
   - **Sound effects** (e.g., "attention-grabbing audio cues")
   - **Dialog/Narration** (e.g., "Meet the future of coffee making...")
   - **Audio balance** (e.g., "Music 60%, narration 40%")
   - **Benefits emphasized** (Scene 3 only)
   
3. **Runware generates:** 4 separate video scenes
   - Scene 1: HOOK (7 seconds) - with engaging music
   - Scene 2: PROBLEM (7 seconds) - with tension-building audio
   - Scene 3: SOLUTION (10 seconds) - with inspiring music + benefits
   - Scene 4: CTA (6 seconds) - with professional music + call-to-action
   - Each optimized for audio engagement

### STEP 6: Video Stitching
1. **FFmpeg concatenates** all 4 scenes
2. **Output:** Final 30-second video (sequence.mp4)
3. Video ready for preview and download

### STEP 7: Optional Caption Generation
1. **Speech-to-Text API extracts** audio dialog/narration
2. **Generates captions** with timing
3. **User downloads** one or more:
   - Video with hardcoded captions (burned-in)
   - Video + SRT subtitle file
   - Text transcript file

### STEP 8: Final Download
- User downloads complete marketing package
- All generated assets available:
  - Final video (with or without captions)
  - 4-6 product images
  - Optional captions/transcript
  - Ready for all social media platforms

---

## ENGAGEMENT AUDIO STRATEGY

### Every Scene Has Professional Audio

**Scene 1: HOOK (7s)**
- Music: Energetic, fast-paced, attention-grabbing
- SFX: Compelling audio elements
- Narration: Hook line ("Meet the future of...")
- Goal: Stop the scroll

**Scene 2: PROBLEM (7s)**
- Music: Tension-building, minor key, thoughtful
- SFX: Frustration sounds that relate to problem
- Narration: Empathetic problem statement
- Goal: Create relatability

**Scene 3: SOLUTION (10s)**
- Music: Inspiring, uplifting, builds momentum
- SFX: Satisfying positive audio cues
- Narration: **Clear benefit statements**
  - Benefit 1: Solved
  - Benefit 2: Additional value
  - Benefit 3: Lifestyle improvement
- Visuals: Multiple use-case scenarios
- Goal: Build excitement

**Scene 4: CTA (6s)**
- Music: Professional, confident, memorable
- SFX: Success/affirmation sounds
- Narration: Final compelling call-to-action
- Visuals: Product hero shot, brand logo
- Goal: Drive action

---

## OPENAI ROLE BREAKDOWN

### Image Generation Prompt
- **Input to OpenAI:**
  - Product image (analyzed for features, colors, materials)
  - Onboarding data (benefit, audience, tone, brand color)
  - Logo description (if provided)

- **OpenAI generates:** 4 image prompts optimized for Runware
  - Specific lighting recommendations
  - Exact composition guidance
  - Logo placement instructions
  - Brand color integration
  - Professional photography language

- **Output to Runware:** Image prompts ready for generation

### Video Scene Generation
- **Input to OpenAI:**
  - Product analysis
  - All 4-6 generated product images
  - Onboarding data (benefit, audience, tone, website)
  - Logo info (if provided)
  - Scene requirements (Hook, Problem, Solution, CTA)

- **OpenAI generates:** 4 detailed scene descriptions including:
  - Complete visual descriptions
  - Camera movement specifications
  - Lighting and mood details
  - **Audio design:**
    - Music style and tempo
    - Sound effects descriptions
    - Dialog/narration content
    - Audio mixing guidance
  - **For Scene 3 only:** Specific benefits to emphasize

- **Output to Runware:** Scene descriptions ready for video generation

### Dialog/Caption Analysis
- **Input to OpenAI Whisper:** Generated video audio
- **OpenAI extracts:** All spoken dialog and narration
- **Output:** Text captions with precise timing

---

## KEY ADVANTAGES OF THIS ARCHITECTURE

✅ **Simple, focused tech stack** - Only OpenAI + Runware
✅ **Professional quality** - Runware handles both images and videos
✅ **Engagement-first** - Audio/music/dialog in every scene
✅ **Fast generation** - Parallel processing possible
✅ **Flexible output** - Multiple format options for captions
✅ **Logo integration** - Seamless branding throughout
✅ **No authentication needed** - Session-based only
✅ **No database** - Temporary storage only
✅ **Complete in 3-5 minutes** - Fast user experience

---

## FILE OUTPUTS

**User receives:**
1. Final 30-second video (MP4)
2. Optional: Captions (hardcoded or SRT)
3. Optional: Transcript text
4. 4-6 professional product images (1024x1024)
5. All formats optimized for social media

**User can immediately:**
- Post video to Instagram Reels, TikTok, YouTube Shorts
- Download images for additional marketing use
- Use captions for accessibility and engagement
- Share complete branded marketing asset

---

## SUMMARY

**ProductFlow** is a streamlined, AI-powered product video generator using:
- **OpenAI** for all analysis and intelligent prompt generation
- **Runware.ai** for professional image and video generation
- **FFmpeg** for lossless video stitching
- **Speech-to-Text** for optional caption generation

Every scene includes professional engagement audio (music + dialog), benefits are explicitly showcased in Scene 3, and optional captions make the final product accessible and optimized for social media success.

Complete workflow: **Form → Upload → Generate (OpenAI) → Create (Runware) → Stitch (FFmpeg) → Caption (optional) → Download**
