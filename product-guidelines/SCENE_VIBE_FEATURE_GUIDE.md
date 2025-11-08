# Scene Description / Visual Vibe Feature
## Complete Implementation Guide

---

## OVERVIEW

The **Scene Description / Visual Vibe** field allows users to define exactly how they want their product video and images to look and feel. This single input shapes both the generated images AND the video scenes, ensuring visual consistency and brand alignment throughout the entire campaign.

---

## STEP 1: ONBOARDING FORM - Scene Description Input

### Form Field Details

**Field Name:** "How would you like your scenes to look and feel?"  
**Type:** Textarea (open-ended text input)  
**Required:** Recommended (but technically optional)  
**Character Limit:** 500-1000 characters recommended

### User Guidance

**Placeholder Examples:**
```
"Modern minimalist office with soft natural window lighting, 
clean aesthetic, professional yet welcoming"

"Outdoor luxury lifestyle moments, golden hour lighting, 
scenic natural backgrounds, premium feel"

"Bright, fun home environment, casual and friendly, 
everyday relatable moments"
```

**Helpful Hint Text:**
```
"Describe the visual atmosphere, environment, and mood of your scenes. 
Include details about lighting, setting, color palette, and overall aesthetic. 
This will guide how your images and video look and feel throughout."
```

### What Users Should Input

**Visual Style:**
- Minimalist, lifestyle, cinematic, product-focused, dramatic, clean, artistic
- Example: "Minimalist and clean"

**Lighting:**
- Natural light, studio lighting, golden hour, bright and clean, soft diffused, dramatic
- Example: "Soft natural window light, morning ambiance"

**Environment/Setting:**
- Modern office, home environment, outdoor/nature, professional studio, real-world location
- Example: "Modern office, contemporary desk setup"

**Mood/Atmosphere:**
- Energetic and fun, luxurious and premium, real and authentic, professional, intimate
- Example: "Professional yet welcoming, trustworthy"

**Color Palette & Aesthetic:**
- Reference brand colors, overall feel
- Example: "Clean whites, soft grays, touches of brand teal"

**What to Avoid:**
- Example: "Avoid corporate stock photos, overly staged scenes"

### Complete Example Inputs

```
INPUT 1: Coffee Maker Brand
"Modern, minimalist kitchen counter. Clean whites and stainless steel. 
Natural morning light streaming through windows. Professional but relatable. 
Real people, genuine moments, not staged. Premium quality feel."

INPUT 2: Skincare Brand
"Luxury spa aesthetic. Soft, warm lighting. Minimalist staging with natural elements 
(plants, water, stones). Premium packaging prominent. Calming, sophisticated mood. 
High-end product presentation."

INPUT 3: Tech Product
"Sleek, contemporary tech environment. Professional studio lighting. 
Clean backgrounds, product-focused. Modern aesthetic, cutting-edge feeling. 
Bright, clean, sophisticated. Real users, professional context."

INPUT 4: Fitness Product
"Energetic outdoor environments. Golden hour or bright daylight. Real people working out. 
Authentic, motivating atmosphere. Dynamic, action-oriented. Natural, gym, or park settings. 
Vibrant, energetic mood."
```

---

## HOW SCENE DESCRIPTION FLOWS THROUGH THE APP

### FLOW DIAGRAM

```
┌─────────────────────────────────────────┐
│  USER INPUTS SCENE DESCRIPTION          │
│  "Modern minimalist office, soft light" │
└──────────────┬──────────────────────────┘
               ↓
        ┌──────────────────┐
        │  STORED IN       │
        │  SESSION DATA    │
        └──────────────────┘
               ↓
        ┌──────────────────────────────────┐
        │  PASSED TO OPENAI PROMPTS        │
        ├──────────────────────────────────┤
        │ 1. Image Generation Prompt       │
        │ 2. Video Scene Generation Prompt │
        └──────────────┬───────────────────┘
               ↓                    ↓
        ┌──────────────┐    ┌──────────────┐
        │  RUNWARE     │    │  RUNWARE     │
        │  Generates   │    │  Generates   │
        │  4-6 Images  │    │  4 Scenes    │
        │  With Vibe   │    │  With Vibe   │
        └──────────────┘    └──────────────┘
               ↓                    ↓
        ┌──────────────┐    ┌──────────────┐
        │ Professional │    │ Professional │
        │ Images That  │    │ Videos That  │
        │ Match Vibe   │    │ Match Vibe   │
        └──────────────┘    └──────────────┘
```

---

## DATA STRUCTURE

### Onboarding Data Includes:

```json
{
  "product_name": "Premium Coffee Maker",
  "category": "Appliance",
  "audience": "Millennials",
  "benefit": "Perfect coffee in 30 seconds, zero waste",
  "brand_color": "#008B8B",
  "tone": "Professional",
  "platform": "Instagram Reels",
  "website": "https://coffeebrand.com",
  
  "scene_vibe_description": "Modern minimalist kitchen. Clean whites and stainless steel. 
  Soft natural light through windows. Professional yet welcoming. Real people, genuine 
  morning moments, not staged. Premium quality aesthetic.",
  
  "product_image": "file_reference",
  "logo_image": "file_reference"
}
```

---

## OPENAI PROMPTS - SCENE DESCRIPTION INTEGRATION

### Image Generation Prompt Section

**In the OpenAI prompt, scene description is included as:**

```markdown
**VISUAL STYLE & SCENE DESCRIPTION:** ⭐ CRITICAL
- User-provided description: [scene_vibe_description]
- This describes exactly how the user wants scenes to look and feel
- Apply this aesthetic to all generated images
- Maintain consistency with user's visual vision
- Examples provided: [parsed from scene_description]
- Lighting preference: [extract from scene_description]
- Environment: [extract from scene_description]
- Mood: [extract from scene_description]
```

**Impact on OpenAI Output:**
- OpenAI uses scene description to craft 4 image prompts
- Each image prompt explicitly references the scene vibe
- Runware receives prompts with consistent visual direction

### Video Scene Generation Prompt Section

**In the OpenAI prompt, scene description is included as:**

```markdown
**VISUAL STYLE & SCENE ATMOSPHERE:** ⭐ CRITICAL FOR VIDEO CONSISTENCY
- Scene Description from User: [scene_vibe_description]
- ALL 4 VIDEO SCENES must maintain this visual style and atmosphere
- Consistency is KEY: Hook, Problem, Solution, CTA all match this aesthetic
- Environment: [parsed from scene_description]
- Lighting: [parsed from scene_description]
- Mood: [parsed from scene_description]
- Aesthetic: [parsed from scene_description]
- Example: If "luxury minimalist office", all scenes should maintain this throughout

**APPLICATION TO EACH SCENE:**

SCENE 1 (Hook): Apply scene vibe - opening should establish the aesthetic
SCENE 2 (Problem): Maintain scene vibe - problem shown within this environment/mood
SCENE 3 (Solution): Preserve scene vibe - solution presented in consistent aesthetic
SCENE 4 (CTA): Reinforce scene vibe - final call-to-action in brand aesthetic
```

---

## RUNWARE RECEIVES OPTIMIZED PROMPTS

### Example: How Scene Description Becomes Image Prompts

**User Input:**
```
"Modern minimalist kitchen counter with soft morning light, 
clean whites and stainless steel, professional yet welcoming"
```

**OpenAI Generates 4 Image Prompts:**

```
Prompt 1 (Morning Routine):
"Modern minimalist kitchen counter with premium coffee maker at center. 
Clean white cabinetry, stainless steel accents. Soft golden morning light 
streaming through window, casting gentle shadows. Professional photography. 
Minimalist aesthetic, welcoming atmosphere."

Prompt 2 (Office Environment):
"Contemporary office desk with coffee maker. Clean workspace, minimalist design. 
Soft natural light from office window. White walls, stainless steel desk accessories. 
Professional, welcoming, productive atmosphere. High-end aesthetic."

Prompt 3 (Lifestyle Moment):
"Person enjoying coffee in modern kitchen. Clean, bright minimalist space. 
Golden morning light. Stainless steel coffee maker visible. Genuine moment, 
professional photography. Welcoming, peaceful morning atmosphere."

Prompt 4 (Detailed Product Shot):
"Close-up of premium coffee maker in minimalist kitchen. Soft directional lighting. 
Clean surfaces, stainless steel and white. Professional product photography. 
Modern, premium, welcoming aesthetic."
```

**Runware generates 4 images** all matching the minimalist, well-lit, welcoming vibe

---

## IMPACT ON FINAL OUTPUT

### Images Generated

All 4-6 images reflect the scene vibe:
- Consistent lighting approach
- Matching environment/setting
- Aligned mood and atmosphere
- Professional aesthetic throughout
- User's exact vision realized

### Videos Generated

All 4 scenes maintain visual consistency:
- **Scene 1 (Hook):** Establishes the aesthetic with opener
- **Scene 2 (Problem):** Shows problem within the scene vibe aesthetic
- **Scene 3 (Solution):** Demonstrates product in consistent environment
- **Scene 4 (CTA):** Closes with reinforced brand aesthetic

### Audio Design

Background music and sounds also match the vibe:
- "Luxury minimalist office" → Sophisticated, calm music
- "Energetic outdoor lifestyle" → Upbeat, adventurous audio
- "Casual home environment" → Warm, friendly sounds

---

## EXAMPLES: SAME PRODUCT, DIFFERENT SCENES

### Product: Premium Water Bottle

**Version 1 - Luxury Minimalist**
```
Scene Description: "Luxury minimalist aesthetic, clean whites and blacks, 
professional studio lighting, premium product focus, sophisticated mood"

Result:
- Images: Clean studio settings, sleek backgrounds, product-centric
- Video: Sophisticated, premium feel, professional audio design
- Captions: Refined, elegant language
- Overall: High-end, exclusive brand position
```

**Version 2 - Outdoor Adventure**
```
Scene Description: "Outdoor adventure moments, golden hour lighting, 
mountains and nature, active lifestyle, energetic atmosphere"

Result:
- Images: Mountain peaks, golden sunset, hikers, nature settings
- Video: Dynamic, action-oriented, adventure audio
- Captions: Motivational, energetic language
- Overall: Active, aspirational brand position
```

**Version 3 - Casual Home**
```
Scene Description: "Bright home environment, casual and friendly, 
relatable everyday moments, natural lighting, approachable"

Result:
- Images: Home environments, families, everyday use, warm lighting
- Video: Friendly, accessible, warm audio design
- Captions: Relatable, conversational language
- Overall: Accessible, trustworthy brand position
```

**SAME PRODUCT. THREE COMPLETELY DIFFERENT CAMPAIGNS.**

---

## QUALITY ASSURANCE

### Verify Scene Vibe Consistency

**For Images:**
- [ ] All images match the described scene vibe
- [ ] Lighting consistent with user's description
- [ ] Environment/setting aligns with scene vibe
- [ ] Mood and atmosphere preserved across images
- [ ] Color palette matches scene vibe and brand color

**For Video:**
- [ ] All 4 scenes maintain the scene vibe throughout
- [ ] Scene 1 establishes aesthetic
- [ ] Scene 2 problem shown within aesthetic
- [ ] Scene 3 solution presented consistently
- [ ] Scene 4 CTA reinforces aesthetic
- [ ] Lighting consistency across scenes
- [ ] Audio design matches scene vibe

**For Captions & Narration:**
- [ ] Language tone matches scene vibe (luxury vs. casual, etc.)
- [ ] Narration feels authentic to aesthetic

---

## USER EXPERIENCE

### Form Field (Step 1)

```
┌─────────────────────────────────────────────────┐
│ How would you like your scenes to look and feel?│
├─────────────────────────────────────────────────┤
│                                                 │
│ [Textarea with placeholder examples visible]   │
│                                                 │
│ "Modern minimalist office with soft..."        │
│                                                 │
│ [?] Hint: "Describe the visual atmosphere..."  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Benefits to User

✅ **Complete Control** - Define exact aesthetic
✅ **Visual Consistency** - All assets match one vision
✅ **Brand Alignment** - Output reflects brand identity
✅ **Differentiation** - Same product looks different based on vibe
✅ **Professional Quality** - Deliberate choices vs. generic output
✅ **Time Saving** - OpenAI optimizes based on description instead of trial/error

---

## IMPLEMENTATION CHECKLIST

**Frontend:**
- [ ] Add textarea field to Step 1 form
- [ ] Include placeholder examples
- [ ] Add helpful hint text
- [ ] Optional field (but recommended)
- [ ] Display character count

**Backend:**
- [ ] Store scene_vibe_description in session data
- [ ] Pass to OpenAI image generation prompt
- [ ] Pass to OpenAI video scene generation prompt
- [ ] Include in data structure

**OpenAI Integration:**
- [ ] Include scene_vibe_description in image prompt (CRITICAL)
- [ ] Include scene_vibe_description in video prompt (CRITICAL)
- [ ] Instruct OpenAI to maintain consistency
- [ ] Extract specific details (lighting, environment, mood)

**Runware Integration:**
- [ ] Receive optimized prompts (no changes needed)
- [ ] Generate images matching scene vibe
- [ ] Generate videos maintaining scene vibe

**Testing:**
- [ ] Test with different scene descriptions
- [ ] Verify consistency across images
- [ ] Verify consistency across video scenes
- [ ] Verify audio design matches vibe
- [ ] Test edge cases (vague descriptions, etc.)

---

## SUMMARY

The **Scene Description/Visual Vibe** field is a powerful feature that:

1. **Captures** exactly how the user wants their campaign to look and feel
2. **Guides** both image and video generation through consistent aesthetic
3. **Ensures** visual and audio coherence throughout all generated assets
4. **Enables** different brand positioning for the same product
5. **Delivers** professional, intentional output vs. generic results

It's a single user input that shapes the entire visual outcome of the campaign.
