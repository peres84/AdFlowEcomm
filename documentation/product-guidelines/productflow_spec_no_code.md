# ProductFlow - Product Video Generator
## Simplified Specification (No Code)

---

## 1. APP OVERVIEW

**Core Value:**
Transform product images into professional 30-second advertisement videos

**User Journey:**
Form → Upload Image → Generate Use-Case Images → Generate Video Scenes → Stitch Scenes → Download Video

**No authentication, no database, session-based only**

---

## 2. 6-STEP USER FLOW

### STEP 1: ONBOARDING FORM
**User provides product and brand information**

Form Fields:
- Product Name
- Product Category (dropdown)
- Target Audience (selection)
- Main Problem/Benefit (text)
- Brand Color (color picker)
- Brand Tone (selection: Professional / Casual / Energetic / Luxury)
- Target Platform (dropdown: Instagram Reels / TikTok / YouTube Shorts / Facebook)
- Website URL
- **Scene Description / Desired Vibe** (textarea) ⭐ IMPORTANT
  - How the user wants ALL scenes to look, feel, and be styled
  - Visual style preferences: (e.g., minimalist, lifestyle, cinematic, product-focused, bright, moody, premium, casual, authentic)
  - Lighting preferences: (e.g., natural light, studio lighting, golden hour, bright and clean, soft diffused, dramatic)
  - Environment/Setting: (e.g., modern office, home environment, outdoor/nature, professional studio, real-world location, lifestyle moment)
  - Mood/Atmosphere: (e.g., energetic and fun, luxurious and premium, real and authentic, professional and trustworthy, intimate and personal)
  - Specific visual inspirations or references
  - What to avoid
  - Examples:
    - "Modern minimalist aesthetic with clean whites and teal accents. Bright natural light through windows. Professional office setting, real people, authentic moments, premium quality."
    - "Sunny outdoor lifestyle moments. Real people, genuine emotions, energetic and relatable. Golden hour lighting. Colorful, vibrant, joyful atmosphere."
    - "Luxury unboxing experience. Sophisticated, premium aesthetic. Professional studio lighting. High-end product presentation. Clean, elegant, exclusive feeling."
    - "Authentic real-world usage. Home environment. Casual but polished. Natural lighting. People genuinely using the product. Relatable and trustworthy."

**Output:** Session data saved (in-memory) including complete scene vibe description

---

### STEP 2: UPLOAD PRODUCT IMAGE & LOGO
**User uploads primary product image (required) and optional logo**

Product Image:
- Drag-and-drop upload
- Image preview
- Compression before processing
- Single image required

Logo Upload (Optional):
- Secondary upload field (optional)
- Logo preview
- Recommended: PNG with transparent background
- Used for image mockup generation if provided
- If not provided, only product image is used

**Output:** Product image + optional logo stored in session

---

### STEP 3: GENERATE USE-CASE IMAGES
**AI generates 4-6 professional product mockup images using Runware.ai**

Process:
1. OpenAI analyzes onboarding data + product image + optional logo
2. OpenAI generates 4-6 detailed image prompts for Runware with logo integration instructions (if logo provided)
3. Runware generates high-quality mockup images (1024x1024) with logo naturally integrated
4. Images returned to frontend for preview

**Logo Handling:**
- If user provided logo: OpenAI includes logo placement instructions in prompts
- If no logo provided: OpenAI focuses on product and brand color only
- Runware generates images with logo integrated (if provided in prompt)
- User sees final images with or without logo depending on what they uploaded

**Output:** Gallery of generated images with descriptions (logo integrated where applicable)

---

### STEP 4: PREVIEW IMAGES
**User sees all generated images**

Display:
- Original product image
- 4-6 generated use-case images
- Each with use-case label
- Download button per image (user can save for social media)

**User Action:** Proceed to video generation

---

### STEP 5: GENERATE VIDEO (SCENE BY SCENE)
**AI generates 4 separate video scenes that will be stitched together**

Process:
1. OpenAI creates 4 scene descriptions (Hook, Problem, Solution, CTA)
2. Each scene is generated separately as individual video file
3. Scenes are stitched together into final 30-second video

**Output:** 4 individual video files + 1 final stitched video

---

### STEP 6: DOWNLOAD VIDEO
**User downloads final stitched video**

Features:
- Preview player
- Download button
- Option to create another video
- Video format optimized for platform

**Output:** MP4 file ready to post

---

## 3. SYSTEM ARCHITECTURE

### INPUT: ONBOARDING DATA & ASSETS
```
{
  "product_name": string,
  "category": string,
  "audience": string,
  "benefit": string,
  "brand_color": string,
  "tone": string,
  "platform": string,
  "website": string,
  "scene_description": string (NEW - visual style and atmosphere),
  "product_image": file (required),
  "logo_image": file (optional, PNG with transparency preferred)
}
```

### PROCESSING FLOW

**Stage 1: Image Generation**
- Input: Onboarding data + Product image
- Process: OpenAI → Runware.ai
- Output: 4-6 use-case images

**Stage 2: Scene Generation**
- Input: Onboarding data + All images (original + generated)
- Process: OpenAI generates 4 scene descriptions
- Output: 4 individual scene prompt descriptions (text, not videos yet)

**Stage 3: Video Scene Generation**
- Input: Each scene description
- Process: Video generation tool (professional video creator) generates 1 video per scene
- Output: 4 separate MP4 files (shot_1.mp4, shot_2.mp4, shot_3.mp4, shot_4.mp4)

**Stage 4: Video Stitching**
- Input: 4 video files in sequence
- Process: FFmpeg concat demuxer stitches videos
- Output: Final 30-second video (sequence.mp4)

---

## 4. IMAGE GENERATION (RUNWARE.AI)

### OPENAI ANALYSIS: Generate Runware Image Prompts

**Process:**
1. OpenAI analyzes the uploaded product image
2. OpenAI analyzes onboarding data (product name, benefit, audience, tone)
3. OpenAI analyzes logo (if provided)
4. OpenAI generates 4 detailed, specific prompts optimized for Runware.ai image generation

```markdown
You are a professional product photographer and visual strategist analyzing images and data for AI image generation.

Your task: Analyze the provided product image and generate 4 detailed image generation prompts for Runware.ai.

**PRODUCT INFORMATION:**
- Product Name: [product_name]
- Category: [category]
- Main Benefit: [benefit]
- Target Audience: [audience]
- Brand Tone: [tone]
- Brand Color: [brand_color]

**VISUAL STYLE & SCENE DESCRIPTION:** ⭐ NEW
- User-provided description: [scene_description]
- This describes how the user wants scenes to look and feel
- Visual atmosphere, environment, mood, aesthetic
- Examples: "Modern minimalist office", "Luxury lifestyle", "Outdoor adventure", etc.

**PRODUCT IMAGE ANALYSIS:**
- Analyze the uploaded product image provided
- Describe: colors, materials, style, size, key features, design elements
- Identify what makes this product unique or attractive
- Note any existing branding or logos visible

**LOGO ANALYSIS (if provided):**
- Logo Provided: [YES/NO]
- Logo Description: [color, style, shape, design elements if provided]
- Logo Integration Strategy: [natural placement suggestions for mockup scenes]

**TASK:**
Generate exactly 4 image prompts specifically optimized for Runware.ai. Each prompt should:

1. Create a realistic, professional product showcase scene
2. Show the product in an authentic use-case scenario
3. Integrate logo naturally if provided (on packaging, signage, branded display)
4. Use vivid visual language perfectly suited for AI image generation
5. Include specific lighting, textures, materials, and colors
6. Reference brand color subtly in composition
7. Match brand tone exactly
8. Produce professional, social-media-ready quality

**OUTPUT FORMAT:**

Use-Case 1: [Use-Case Name]
Runware Prompt: [Detailed, vivid prompt - 3-5 sentences with specific visual direction for Runware]
Logo Integration: [How/where logo appears if provided]

Use-Case 2: [Use-Case Name]
Runware Prompt: [Detailed prompt...]
Logo Integration: [Details if applicable]

Use-Case 3: [Use-Case Name]
Runware Prompt: [Detailed prompt...]
Logo Integration: [Details if applicable]

Use-Case 4: [Use-Case Name]
Runware Prompt: [Detailed prompt...]
Logo Integration: [Details if applicable]

---

**GUIDANCE FOR RUNWARE.AI PROMPTS:**
- Use concrete, descriptive language (Runware excels with specific visual details)
- **Incorporate scene description:** Each image should match the user-provided visual style
- Lighting: Always specify lighting type (studio, golden hour, bright daylight, soft diffused, etc.)
- Composition: Mention specific framing (close-up, mid-shot, wide angle, rule of thirds, etc.)
- Materials/Textures: Reference specific textures visible in the product image
- Background: Describe realistic, professional backgrounds suitable for the product **AND matching scene description**
- Style: Commercial photography, professional quality, polished
- Brand Color: Subtle integration of brand color in the scene
- Logo Placement (if provided): Natural, professional, enhances rather than distracts
- **Scene Atmosphere:** Match the feeling described in scene_description (modern/luxury/casual/outdoor/etc.)
- Target Quality: All prompts should generate minimum 1024x1024 high-quality images
```

### RUNWARE IMAGE OUTPUT

Each image should be:
- 1024x1024 resolution
- Professional quality
- Ready for social media
- High contrast and visually appealing

---

## 5. VIDEO SCENE GENERATION (RUNWARE.AI)

### OPENAI ANALYSIS: Generate Video Scene Descriptions

**Process:**
1. OpenAI analyzes onboarding data, all generated images, and logo
2. OpenAI generates 4 detailed scene descriptions optimized for Runware.ai video generation
3. Each scene includes engagement elements: music direction, sound design, and optional dialog/narration

```markdown
You are a professional video director and copywriter specializing in high-converting product advertisements.

Your task: Create 4 detailed scene descriptions for a 30-second product video.

These descriptions will be used to generate individual video scenes using Runware.ai video generation.

**PRODUCT INFORMATION:**
- Product Name: [product_name]
- Main Benefit: [benefit]
- Target Audience: [audience]
- Brand Tone: [tone]
- Brand Color: [brand_color]
- Website: [website]

**VISUAL STYLE & SCENE ATMOSPHERE:** ⭐ NEW
- Scene Description from User: [scene_description]
- All video scenes should follow this visual style and atmosphere
- Environment, mood, aesthetic consistency throughout video
- Example: If "luxury minimalist office", all scenes should maintain this aesthetic

**AVAILABLE VISUAL ASSETS:**
- Original Product Image: [detailed description of uploaded product image]
- Generated Use-Case Image 1: [use-case name and visual description]
- Generated Use-Case Image 2: [use-case name and visual description]
- Generated Use-Case Image 3: [use-case name and visual description]
- Generated Use-Case Image 4: [use-case name and visual description]
- Logo Provided: [YES/NO - if yes, description and branding strategy]

**TASK:** Generate 4 complete scene descriptions optimized for Runware.ai video generation.

Each scene must include:
1. Vivid visual sequence description
2. Camera work and transitions
3. Lighting and mood
4. Audio direction: Background music style
5. Sound effects descriptions
6. Dialog/Narration (REQUIRED): Clear, compelling spoken narrative that matches the scene
7. Music + Dialog balance specifications
8. Engagement elements for viewer retention

**CRITICAL: ENGAGEMENT AUDIO**
- Every scene must have either background music OR dialog/narration (or both)
- Dialog/Narration should be natural, conversational, not robotic
- Music should match emotional tone of scene
- Sound should create emotional engagement throughout video

**TIMING:**
- Scene 1 (Hook): 7 seconds
- Scene 2 (Problem): 7 seconds
- Scene 3 (Solution): 10 seconds
- Scene 4 (CTA): 6 seconds
- Total: 30 seconds

---

**SCENE 1: HOOK (7 seconds)**
Goal: Capture attention, create curiosity, stop the scroll

Visual Description: [Vivid description of opening shot - what viewer sees first, camera movement, lighting, composition]

Camera/Movement: [Specific techniques - zoom, pan, tracking, dynamic cuts]

Lighting & Mood: [Professional lighting that creates visual impact and emotional pull]

Image Integration: [Which visual asset featured]

Audio Design:
- Background Music: [Specific style and tempo - e.g., "upbeat modern electronic, fast-paced, energetic"]
- Sound Effects: [Attention-grabbing audio elements that match visuals]
- Dialog/Narration: [Opening statement - compelling hook line, max 2 sentences]
  - Example: "Meet the future of [product category]. Here's why everyone is switching."
- Audio Balance: [How dialog and music mix - e.g., "Music at 60%, narration clear at 40%"]

Engagement Target: [What hooks the viewer? Curiosity? Visual wow factor? Problem recognition?]

---

**SCENE 2: PROBLEM (7 seconds)**
Goal: Identify pain point, show struggle, create emotional connection

Visual Description: [Show realistic problem scenario - struggle or unmet need viewer experiences]

Camera/Movement: [Camera work conveying tension - handheld, quick cuts, deliberate pacing]

Lighting & Mood: [Lighting showing contrast with Hook - subtly different emotional tone]

Image Integration: [Which visual asset shows problem context]

Audio Design:
- Background Music: [Style reflecting tension/frustration - e.g., "minor key, building concern, thoughtful tempo"]
- Sound Effects: [Realistic problem sounds - frustration audio cues that reinforce struggle]
- Dialog/Narration: [Problem statement - empathetic, relatable, max 3 sentences]
  - Example: "Every single day, the same frustration. Wasted time. Wasted money. There has to be a better way."
- Audio Balance: [Dialog prominent as viewer should feel heard, music supports emotion]

Emotional Tone: Frustration, recognition, validation of struggle

---

**SCENE 3: SOLUTION (10 seconds)**
Goal: Demonstrate benefits, show transformation, build excitement, create satisfaction

Visual Description: [Product introduction and demonstration - solution in action. Show 2-3 specific benefits being solved]

Benefits Showcased:
- Benefit 1: [What primary problem does it solve? How is this shown visually?]
- Benefit 2: [What additional value/feature improves experience?]
- Benefit 3: [How does this improve lifestyle or create aspirational moment?]

Camera/Movement: [Fast, dynamic cuts showing product in multiple scenarios, building momentum, satisfying transitions]

Lighting & Mood: [Warm, bright, positive lighting - clear visual contrast from Scene 2. Professional, aspirational aesthetic]

Image Integration: [Multiple visual assets showing different benefits, use-cases, and lifestyle scenarios]

Audio Design:
- Background Music: [Uplifting, energetic, building - e.g., "inspiring modern soundtrack, builds momentum to peak, celebratory"]
- Sound Effects: [Satisfying, positive audio cues - smooth operation sounds, success elements, encouraging audio feedback]
- Dialog/Narration: [Benefit statements - clear value proposition, max 4 sentences]
  - Example: "[Product] delivers [benefit 1] in just [timeframe]. Plus [benefit 2] and [benefit 3]. The solution you've been waiting for."
- Audio Balance: [Narration clear over uplifting music, SFX enhance positive moments]

Pacing: Fast but not overwhelming, clearly showing multiple benefits

Emotional Tone: Relief, excitement, satisfaction, aspiration, confidence

Engagement Element: [Is viewer excited and ready to take action?]

---

**SCENE 4: CALL-TO-ACTION (6 seconds)**
Goal: Drive immediate action, create urgency, memorable brand close

Visual Description: [Professional, premium final moment - product hero shot with strong branding and aspirational moment]

Camera/Movement: [Confident, steady shot - product 360 reveal, slow zoom into hero, or product + brand reveal]

Lighting & Mood: [Professional, clean, premium lighting - product/brand is the star. Trust-building aesthetic]

Logo Integration: [Logo prominently featured if provided - final brand imprint]

On-Screen Text Elements:
- Headline CTA: [Bold, compelling action - max 5 words, e.g., "GET YOURS TODAY"]
- Secondary CTA: [Action instruction - max 5 words, e.g., "CLICK LINK BELOW"]
- Tertiary: [Website URL or promo code]
- Urgency Element: [If applicable - "Limited Time", "First 100 Only", "Exclusive Access"]

Audio Design:
- Background Music: [Confident, professional, memorable - e.g., "branded sonic signature, bold, inspiring, professional"]
- Sound Effects: [Success/affirmation audio - brand sonic signature if available, positive completion sounds]
- Dialog/Narration: [Final compelling statement - call-to-action, max 3 sentences]
  - Example: "Don't settle for ordinary. Join thousands of happy customers. Visit [website] today and transform your [product category]."
- Audio Balance: [Narration clear and prominent so CTA is unmissable, music supports brand moment]

Visual Ending: [Final memorable frame - product, logo, brand, or aspirational customer moment]

Engagement Element: [Would viewer take action? Does CTA feel urgent and trustworthy?]

---

**OVERALL AUDIO GUIDELINES:**

- Emotional Arc: Curiosity → Recognition → Excitement → Confidence (reflected in music progression)
- **Scene Consistency:** Music and audio should match the scene description aesthetic
- Dialog Quality: Natural, conversational, not corporate or robotic
- Music Selection: Professional, matches brand tone (Professional/Casual/Energetic/Luxury) AND scene description
- Sound Design: Premium quality, enhances without distracting
- Narration Authenticity: Speaker should sound genuine, passionate about product
- Engagement Continuity: Audio keeps viewer engaged across all 4 scenes
- Music Transitions: Smooth progression between scenes
- Volume Clarity: Dialog always clear and audible over music/SFX
- **Visual Audio Match:** Audio design supports the visual atmosphere (e.g., minimalist aesthetic = clean, spacious audio; luxury = premium, rich audio)
```

### VIDEO SCENE DESCRIPTION OUTPUT STRUCTURE

Each scene description should include:

**Scene 1: HOOK**
- Duration: 7 seconds
- Visual Description: [2-3 sentences describing opening shot, camera work, lighting]
- Key Elements: [Specific visuals, colors, movements]
- Image Use: [Which image from gallery, if any]
- Emotional Target: [Primary feeling viewer should experience]

**Scene 2: PROBLEM**
- Duration: 7 seconds
- Visual Description: [2-3 sentences showing problem scenario]
- Key Elements: [Problem visualization, emotional cues]
- Image Use: [Context image]
- Emotional Target: Frustration, recognition

**Scene 3: SOLUTION**
- Duration: 10 seconds
- Visual Description: [2-3 sentences showing product benefits and transformation]
- Key Elements: [Product introduction, benefits shown, satisfaction visible]
- Image Use: [Multiple use-case images showing lifestyle benefits]
- Emotional Target: Satisfaction, aspiration, confidence

**Scene 4: CTA**
- Duration: 6 seconds
- Visual Description: [2-3 sentences of professional final shot]
- Key Elements: [Product hero shot, brand elements visible]
- On-Screen Text:
  - Headline: [Main CTA]
  - Secondary: [Action instruction]
  - Tertiary: [Website]
- Image Use: [Original product image prominent]
- Emotional Target: Confidence, urgency, trust

---

## 6. VIDEO GENERATION WORKFLOW

### Process Flow

**Step 1: Scene 1 Description Generated**
- Video generation tool receives: Scene 1 detailed description
- Generates: shot_1.mp4 (7 seconds)
- Output: Individual MP4 file

**Step 2: Scene 2 Description Generated**
- Video generation tool receives: Scene 2 detailed description
- Generates: shot_2.mp4 (7 seconds)
- Output: Individual MP4 file

**Step 3: Scene 3 Description Generated**
- Video generation tool receives: Scene 3 detailed description
- Generates: shot_3.mp4 (10 seconds)
- Output: Individual MP4 file

**Step 4: Scene 4 Description Generated**
- Video generation tool receives: Scene 4 detailed description
- Generates: shot_4.mp4 (6 seconds)
- Output: Individual MP4 file

**Step 5: Video Stitching**
- Input: shot_1.mp4, shot_2.mp4, shot_3.mp4, shot_4.mp4 (in sequence)
- Process: FFmpeg concatenates videos in order
- Output: sequence.mp4 (30 seconds total)

---

## 7. VIDEO STITCHING APPROACH

### FFmpeg Concat Method (Recommended)

**Process:**
1. Save 4 generated video files in sequence folder
2. Name them: shot_1.mp4, shot_2.mp4, shot_3.mp4, shot_4.mp4
3. Use FFmpeg concat demuxer to combine them
4. Output final video: sequence.mp4

**Benefits:**
- Lossless stitching (no re-encoding)
- Fast processing
- No quality loss
- Clean transitions between scenes
- Professional results

**Implementation:**
- Create temporary concat file listing all shots
- Use FFmpeg to join videos
- Output single MP4 file

---

## 8. CAPTION GENERATION (OPTIONAL FINAL STEP)

### Speech-to-Text Captions from Dialog/Narration

**Purpose:**
Generate captions from video dialog/narration to make content accessible and increase social media engagement.

**When Captions Are Generated:**
- After video is fully generated and stitched
- User sees prompt: "Add Captions? (Optional but recommended)"
- User can choose to add or skip

**Caption Generation Process:**

1. **Extract Audio:** Audio track from final video extracted
2. **Speech-to-Text:** Dialog and narration converted to text
3. **Timing Sync:** Captions timed to match spoken words
4. **Formatting:** Professional caption styling applied
5. **User Review:** (Optional) User can edit caption text before finalizing

**Why Captions Matter:**
- ✅ Many social media users watch without sound
- ✅ Accessibility for deaf/hard of hearing users
- ✅ Increases watch time and engagement on social media
- ✅ Improves SEO and content discoverability
- ✅ Professional, complete marketing asset

**Caption Output Options:**

**Option 1: Video with Hardcoded Captions**
- Captions burned directly into video file
- No separate files needed
- Perfect for platforms like TikTok, Instagram Reels
- Cannot be edited by user after download
- File format: MP4 with burned-in captions

**Option 2: Video + SRT Subtitle File**
- Main video file (no captions)
- Separate SRT file with timing and text
- Allows flexibility on different platforms
- User can customize captions on their platform
- Downloads: video.mp4 + video.srt

**Option 3: Transcript Only**
- Just the text of all dialog/narration
- Useful for blog posts, social media descriptions
- Plain text or formatted document
- Download: transcript.txt

**Caption Customization (Optional):**
- Edit caption text if desired
- Change caption styling:
  - Font type (sans-serif, serif, modern, etc.)
  - Font size (scaled to video)
  - Color (white, yellow, or custom)
  - Position (bottom, center, top)
  - Background (transparent, semi-opaque, solid)
- Preview captions with video before downloading
- Add brand watermark or logo to caption area

**Download Options:**
User can download one or all:
- [ ] Video with hardcoded captions
- [ ] Video + SRT file
- [ ] Transcript text file

**Example Caption Output:**

```
Scene 1 (0-7s): "Meet the future of coffee making. Here's why everyone is switching."
Scene 2 (7-14s): "Every morning, the same frustration. Wasted time. Wasted money."
Scene 3 (14-24s): "[Product] delivers perfect brewing in 30 seconds. Plus zero waste and 100% satisfaction."
Scene 4 (24-30s): "Don't settle for ordinary. Visit [website] today."
```

---

## 9. USER INTERFACE FLOW

### DISPLAY STRUCTURE

**STEP 1: FORM PAGE**
- Single page with all form fields
- Clear labels and helpful hints
- **New field: Scene Description / Visual Style textarea**
  - Label: "How would you like your scenes to look and feel?"
  - Placeholder examples: "Modern minimalist office with soft lighting" or "Outdoor luxury lifestyle" or "Clean, bright, professional environment"
  - Helpful hint: "Describe the visual atmosphere, environment, and mood. This will guide the look and feel of your images and video."
- Next button at bottom

**STEP 2: UPLOAD PAGE (Product Image + Logo)**
- Primary upload area: Product Image (required)
  - Drag-and-drop zone
  - Clear label: "Upload Your Product Image (Required)"
  - File preview with dimensions
  
- Secondary upload area: Logo (optional)
  - Drag-and-drop zone below product image
  - Clear label: "Upload Your Logo (Optional)"
  - Helpful text: "PNG with transparent background recommended"
  - File preview showing logo
  - Option to remove uploaded logo
  
- Proceed button only active after product image uploaded
- Back and Next buttons

**STEP 3: GENERATING IMAGES (Loading State)**
- Progress indicator
- Message: "Creating professional use-case images..."
- Estimated time display

**STEP 4: IMAGE GALLERY**
- Grid view of all images (original + 4 generated)
- Each image labeled with use-case name
- Visual indicator if logo is integrated in image (small badge or text)
- Download button per image
- Visual indication of image source (original vs generated)
- Note showing: "Logo integrated" or "No logo" for transparency
- [← BACK]     [GENERATE VIDEO →]

**STEP 5: GENERATING VIDEO (Loading State)**
- Scene-by-scene progress tracker
- Message: "Scene 1 of 4: Creating hook with engaging audio... (7 seconds)"
- Visual progress bar per scene
- Estimated time remaining
- Information about audio/music being added

**STEP 6: VIDEO PREVIEW & DOWNLOAD**
- Video preview player
- One-click download button (video file)
- Video details (duration: 30 seconds, format, file size)
- Display of dialog/narration used
- [NEXT: ADD CAPTIONS (Optional)]
- [DOWNLOAD & FINISH]
- [CREATE ANOTHER]

**STEP 7: CAPTIONS (OPTIONAL)**
- Prompt: "Add Captions to Your Video?"
- Explanation: "Captions increase engagement and accessibility"
- Options to choose:
  - [ ] Video with burned-in captions
  - [ ] Video + SRT subtitle file
  - [ ] Transcript text file
- Caption preview:
  - Display sample captions from video
  - Allow editing if desired
  - Caption styling options (preview)
- [SKIP CAPTIONS]
- [ADD & DOWNLOAD]
- Completion page showing all available downloads

**STEP 8: FINAL DOWNLOAD**
- All files ready for download
- Display what's included:
  - Final video (with captions if chosen)
  - Optional: SRT file, transcript
  - Original generated images (optional link to re-download)
- [DOWNLOAD ALL FILES]
- [CREATE ANOTHER PRODUCT]
- Share social media tips or instructions

**STEP 3: GENERATING IMAGES (Loading State)**
- Progress indicator
- Message: "Creating professional use-case images..."
- Estimated time display

**STEP 4: IMAGE GALLERY**
- Grid view of all images (original + 4 generated)
- Each image labeled with use-case name
- Visual indicator if logo is integrated in image (small badge or text)
- Download button per image
- Visual indication of image source (original vs generated)
- Note showing: "Logo integrated" or "No logo" for transparency

**STEP 5: GENERATING VIDEO (Loading State)**
- Scene-by-scene progress tracker
- Message: "Scene 1 of 4: Creating hook... (7 seconds)"
- Visual progress bar
- Estimated time remaining

**STEP 6: VIDEO READY**
- Video preview player
- Download button
- Video details (duration, format, size)
- "Create Another" button

---

## 10. DATA FLOW DIAGRAM

```
[User Form Input]
        ↓
[Session Data Stored]
        ↓
[Product Image + Logo Uploaded]
        ↓
[OpenAI Analyzes Product & Generates Image Prompts]
        ↓
[Runware Generates 4-6 Professional Images]
        ↓
[Images Displayed in Gallery]
        ↓
[User Approves, Continues]
        ↓
[OpenAI Generates 4 Scene Descriptions with Audio/Dialog Guidance]
        ↓
[Scene 1 → Runware → shot_1.mp4 (7 seconds)]
        ↓
[Scene 2 → Runware → shot_2.mp4 (7 seconds)]
        ↓
[Scene 3 → Runware → shot_3.mp4 (10 seconds)]
        ↓
[Scene 4 → Runware → shot_4.mp4 (6 seconds)]
        ↓
[FFmpeg Stitches All 4 Shots]
        ↓
[Final Video: sequence.mp4 (30 seconds)]
        ↓
[User Views Video Preview]
        ↓
[Optional: User Generates Captions from Dialog/Narration]
        ↓
[Speech-to-Text Extracts Dialog → Creates Captions]
        ↓
[User Reviews/Edits Captions (Optional)]
        ↓
[Captions Applied to Video]
        ↓
[User Downloads Final Package]
  - Video (with or without captions)
  - SRT subtitle file (optional)
  - Transcript text (optional)
  - Original generated images (optional)
```

---

## 11. KEY FEATURES

✅ **Simple workflow** - Form → Upload → Generate Images → Generate Video → Add Captions (optional) → Download  
✅ **No authentication** - No login required  
✅ **Professional images** - Runware.ai image generation with logo integration  
✅ **Scene-by-scene videos** - Runware.ai video generation with engagement audio/music  
✅ **Dialog/Narration** - Every scene includes spoken narrative for clarity and engagement  
✅ **Engagement music** - Professional background music matched to emotional tone  
✅ **Optional captions** - Generate captions from dialog for accessibility and social media optimization  
✅ **Caption flexibility** - Choose between hardcoded, SRT file, or transcript  
✅ **Independent image downloads** - Users can repurpose generated images for own use  
✅ **Logo integration** - Optional branding throughout images and video  
✅ **Mobile-responsive UI**  
✅ **No database** - Session-based only  
✅ **Fast generation** - Complete workflow in 3-5 minutes

---

## 11. TIMING & PERFORMANCE

**Image Generation:** 30-60 seconds (4 images)
**Scene 1 Generation:** 20-30 seconds (7 seconds of video)
**Scene 2 Generation:** 20-30 seconds (7 seconds of video)
**Scene 3 Generation:** 30-45 seconds (10 seconds of video)
**Scene 4 Generation:** 15-20 seconds (6 seconds of video)
**Video Stitching:** 5-10 seconds (FFmpeg)
**Total Time:** ~3-4 minutes for complete workflow

---

## 16. ADVANTAGES OF SCENE-BY-SCENE APPROACH

✅ **Parallel Processing:** Can generate scenes simultaneously if API allows
✅ **Smaller Files:** Individual scene videos are smaller, faster to generate
✅ **Error Recovery:** If one scene fails, can regenerate just that scene
✅ **Better Quality Control:** Can review each scene individually before stitching
✅ **Flexibility:** Easy to reorder scenes or regenerate specific scenes
✅ **Professional Results:** Scene descriptions can be highly specific and detailed
✅ **API Friendly:** Smaller requests may be more reliable than one large video generation

---

---

## 12. SCENE DESCRIPTION IMPACT

### How Scene Description Influences Output

**Scene Description** is a user-provided input that shapes:
1. **Image generation** - Visual atmosphere and environment
2. **Video scene generation** - Visual consistency across all scenes
3. **Audio design** - Music and sound matching the aesthetic

### Example Outputs with Different Scene Descriptions

**Example 1: "Modern Minimalist Office"**

Scene Description Input:
```
"Modern minimalist office with soft natural window lighting, 
clean aesthetic, professional yet welcoming atmosphere"
```

Impact on Generation:
- Images: Clean, uncluttered backgrounds, soft natural lighting, modern minimalist desk
- Video: All scenes maintain minimalist aesthetic, soft spacious audio design
- Result: Cohesive, professional, calm campaign

---

**Example 2: "Outdoor Luxury Lifestyle"**

Scene Description Input:
```
"Outdoor luxury lifestyle moments, golden hour lighting, 
scenic natural backgrounds, premium aesthetics"
```

Impact on Generation:
- Images: Outdoor settings, golden hour lighting, luxury product placement
- Video: All scenes set outdoors with premium aesthetic, rich audio design
- Result: Aspirational, exclusive, high-end campaign

---

**Example 3: "Bright, Fun, Casual Home"**

Scene Description Input:
```
"Bright, fun home environment, casual and friendly atmosphere, 
relatable everyday moments"
```

Impact on Generation:
- Images: Bright home environments, warm lighting, casual relatable settings
- Video: All scenes in bright homes, upbeat audio, friendly narration
- Result: Approachable, relatable, fun campaign

---

### Why Scene Description Matters

✅ **Visual Consistency** - All images and video match a cohesive aesthetic
✅ **Brand Alignment** - User vision translates to final output
✅ **Emotional Coherence** - Mood consistent throughout campaign
✅ **Professional Quality** - Deliberate aesthetic choices vs. generic output
✅ **Engagement** - Viewers experience complete, immersive brand world
✅ **Differentiation** - Same product has radically different presentations based on scene description

---

## 13. QUALITY ASSURANCE CHECKLIST

**Image Generation:**
- [ ] 4 professional images generated
- [ ] Images show different use-cases
- [ ] Brand color visible in images
- [ ] Logo integrated naturally (if provided)
- [ ] Images are high resolution (1024x1024)
- [ ] **Scene description aesthetic applied** ⭐
- [ ] Visual consistency with scene description
- [ ] Images ready for social media use

**Video Scene Generation:**
- [ ] Scene 1: Hook captures attention
- [ ] Scene 2: Problem clearly identified
- [ ] Scene 3: Solution demonstrated with product and benefits
- [ ] Scene 4: CTA is clear and actionable
- [ ] Scenes flow naturally together
- [ ] Total duration is exactly 30 seconds
- [ ] **Scene description aesthetic maintained throughout** ⭐
- [ ] Audio/music matches scene atmosphere
- [ ] Dialog/narration quality professional

**Video Stitching:**
- [ ] All 4 scenes present
- [ ] Scenes in correct order
- [ ] Transitions are seamless
- [ ] Audio/music consistent
- [ ] Final video is 30 seconds
- [ ] File is ready to upload to social media

---

## 14. LOGO INTEGRATION STRATEGY

### Logo Upload (Step 2)

**User Flow:**
1. Upload product image (required)
2. Optionally upload logo file
3. Both stored in session

**Logo File Requirements:**
- Format: PNG, JPG, or SVG
- Recommended: PNG with transparent background
- Size: Any size (will be processed/resized as needed)
- Aspect ratio: Any (will be adapted to fit scenes)

**Logo Detection:**
- If user provides logo, system stores it as separate asset
- If user doesn't provide logo, system notes this and instructs OpenAI accordingly

---

### Logo Integration in Image Generation

**OpenAI's Role:**
- When logo is provided, OpenAI includes specific placement instructions in image prompts
- Example placements:
  - On product packaging/box
  - On a branded storefront or display
  - On branded signage in the background
  - On a branded shopping bag or container
  - Watermark corner (professional style, not obtrusive)
  - On branded display shelf or counter

**Runware Integration:**
- Receives image prompt with specific logo placement instructions
- Generates image with logo naturally incorporated
- Logo should be recognizable but not overpowering
- Professional integration (looks like real branded environment)

**Quality Assurance:**
- Logo is visible and recognizable
- Logo placement feels natural to the scene
- Logo doesn't distract from product
- Consistent logo appearance across all generated images

---

### Logo in Video Scenes

**Scene Generation:**
- OpenAI notes logo availability in scene descriptions
- Can reference logo in scenes (e.g., "branded signage visible", "product packaging shows logo")
- Runware generates video scenes with logo integration where mentioned

**Scene Types:**
- Scene 1 (Hook): Logo could appear subtly in background
- Scene 2 (Problem): Logo typically not prominent
- Scene 3 (Solution): Logo visible on product/packaging
- Scene 4 (CTA): Logo prominently featured on final brand reveal

---

### User Experience Around Logo

**Transparency:**
- User sees that logo was uploaded
- In image gallery, user can see which images have logo integrated
- Before video generation, system confirms: "Using uploaded logo in video"

**Flexibility:**
- Logo is optional (not required for success)
- If logo already on product image, user doesn't need to upload separately
- User can see before/after comparison in gallery

**Output:**
- Final video can feature logo prominently or subtly
- Downloaded images show logo (if integrated)
- User can use generated images with logo for social media

---

### Technical Handling

**Logo Processing:**
1. User uploads logo file
2. System stores file in session (temporary)
3. System creates text description of logo for OpenAI (color, style, shape)
4. OpenAI includes logo description in image generation prompts
5. Runware receives prompt with logo integration instructions
6. Generated images include logo (natural integration)
7. Video scenes reference logo where applicable

**No Logo Case:**
1. User skips logo upload
2. System notes: "No logo provided"
3. OpenAI focuses on product image and brand color only
4. Runware generates images without logo
5. Images and video highlight product without brand logo

---

### Example Logo Integration Scenarios

**Scenario 1: Coffee Maker with Logo**
- Product Image: Coffee maker (no logo visible)
- Logo Upload: Brand logo (circular, teal color)
- Generated Image Use-Case "Morning Routine":
  - OpenAI prompt: "Coffee maker on desk with branded packaging/box showing logo in corner"
  - Runware generates: Image with product, packaging displays logo naturally
  - Video integration: Logo visible on packaging in Scene 3

**Scenario 2: Skincare Product with Logo**
- Product Image: Skincare bottle (logo already on label)
- Logo Upload: Skipped (logo already on product)
- Generated Images: Focus on product benefits, existing logo visible on bottle
- Video: Logo highlighted on product packaging throughout

**Scenario 3: Tech Accessory with Logo**
- Product Image: Tech device (minimal branding)
- Logo Upload: Brand logo provided
- Generated Images: Logo integrated on product packaging/presentation
- Video: Logo featured in CTA scene with brand reveal

---

## 15. NEXT STEPS

**For MVP (Hackathon):**
1. Build form interface (Step 1)
2. Build upload interface (Step 2)
3. Integrate OpenAI image prompt generation (Step 3)
4. Display image gallery (Step 4)
5. Integrate OpenAI video scene generation (Step 5)
6. Send scene descriptions to Runware for video generation
7. Implement FFmpeg video stitching (Step 6)
8. Display video download (Step 6)
9. Deploy and test end-to-end

**For Future Enhancement:**
- Batch generation (multiple products at once)
- Scene customization UI
- A/B testing different scenes
- User accounts and history
- Analytics on video performance
- API for external integrations

---

## SUMMARY

**ProductFlow** is a streamlined, AI-powered product video generator that:

1. **Collects** product, brand, and **scene vision** information via simple form
2. **Analyzes** product image, onboarding data, **and scene description** with OpenAI
3. **Generates** professional use-case images with Runware.ai (with optional logo integration)
   - **Shaped by scene description for cohesive aesthetic**
4. **Creates** 4 distinct video scenes with OpenAI (including engaging audio/music/dialog)
   - **Maintains scene description aesthetic throughout**
5. **Generates** each scene separately with Runware.ai for quality and flexibility
6. **Stitches** scenes together with FFmpeg for final 30-second video
7. **Extracts** dialog and optionally generates captions
8. **Delivers** complete marketing package with unified visual language

**Key Differentiators:**
- Scene-by-scene generation for quality + flexibility
- **Scene description input for custom visual aesthetic**
- Professional engagement audio/music/dialog in every scene
- Optional captions for accessibility and social media optimization
- Logo integration throughout
- **Unified visual language across all assets**
- OpenAI analysis + Runware generation + FFmpeg stitching

**Output:**
- 30-second vertical videos (9:16 format)
- Professional product images (1024x1024)
- **Cohesive aesthetic matching scene description**
- Professional audio, music, and dialog
- Optional captions (hardcoded or SRT)
- Ready-to-post social media content
