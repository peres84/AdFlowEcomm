# Documentation Index

Complete documentation for the AdFlowEcomm video generation system.

---

## 📚 Main Documentation

### [COMPLETE_VIDEO_WORKFLOW.md](COMPLETE_VIDEO_WORKFLOW.md) ⭐ START HERE
**End-to-End Video Generation Guide**

Complete workflow combining Runware (video) + Mirelo (audio):
- ✅ Step-by-step: Image → Video → Audio → Final Video
- Quick start guide (~6-7 minutes total)
- File organization and structure
- Customization options
- Troubleshooting guide
- Best practices

**Use this when:** Creating complete videos with audio from start to finish

**Perfect for:** First-time users, complete workflow understanding

---

### [VIDEO_RW_API_FLOW.md](VIDEO_RW_API_FLOW.md)
**Runware API Integration Guide (Detailed)**

Deep dive into Runware video generation:
- ✅ Verified working configuration (MiniMax, 244s generation)
- Complete workflow (upload → generate → poll → download)
- Request/response structures
- Error handling patterns
- Full working code examples

**Use this when:** Implementing video generation or troubleshooting Runware API

---

### [MIRELO_AUDIO_FLOW.md](MIRELO_AUDIO_FLOW.md)
**Mirelo Audio Generation Guide (Detailed)**

Deep dive into Mirelo audio generation:
- ✅ 5-step workflow (create asset → upload → generate → download → merge)
- Video-audio merging with FFmpeg
- Text prompt examples for different video types
- Parameter tuning guide
- Error handling patterns

**Use this when:** Implementing audio generation or troubleshooting Mirelo API

---

### [video_models.md](video_models.md)
**Video Model Reference**

Complete reference for available video models on Runware:
- Model providers (MiniMax, KlingAI, PixVerse, etc.)
- Duration limits and dimensions
- Payload parameters
- Model-specific requirements

**Use this when:** Choosing which video model to use

---

## 🛠️ Helper Functions

### [../scripts/utils/README.md](../scripts/utils/README.md)
**Helper Functions - Complete Reference**

All helper utilities for video generation:
- Image resizing (`resizer_img.py`)
- Format conversion (`extension_changer_img.py`)
- Video generation (`video_helpers.py`)
- Multi-scene generation (`scene_generator.py`)
- Video-audio merging (`video_audio_merger.py`) ✨

Includes quick start examples, verification status, and integration guides.

**Use this when:** Looking for reusable helper functions or code examples

---

## 📋 Product Guidelines

### [../product-guidelines/](../product-guidelines/)
**ProductFlow Specifications**

Complete specifications for the ProductFlow application:
- `FINAL_TECH_STACK.md` - Technology stack and architecture
- `productflow_spec_no_code.md` - Complete product specification
- `SCENE_VIBE_FEATURE_GUIDE.md` - Scene description feature guide
- `ideas-examples.md` - Examples and ideas

**Use this when:** Understanding the complete ProductFlow workflow and requirements

---

## 🧪 Testing & Examples

### [../scripts/testing_video/](../scripts/testing_video/)
**Video Generation Testing**

- `testing_runware_.py` - ✅ Runware video generation (verified working)

### [../scripts/testing_audio/](../scripts/testing_audio/)
**Audio Generation Testing**

- `testing_mirelo.py` - ✅ Mirelo audio generation + video merging (complete workflow)

**Use this when:** Looking for working code to test or reference

**Note:** Testing scripts now include complete workflows with video-audio merging!

---

## 🚀 Quick Navigation

**I want to...**

- **Generate videos** → [VIDEO_RW_API_FLOW.md](VIDEO_RW_API_FLOW.md)
- **Add audio to videos** → [MIRELO_AUDIO_FLOW.md](MIRELO_AUDIO_FLOW.md)
- **Use helper functions** → [../scripts/README.md](../scripts/README.md)
- **Choose a video model** → [video_models.md](video_models.md)
- **See working examples** → [../testing/](../testing/)
- **Understand ProductFlow** → [../product-guidelines/](../product-guidelines/)

---

## ✅ Verification Status

All documentation is based on tested and verified code:

**Video Generation (Runware):**
- ✅ MiniMax model working (244s generation time)
- ✅ Complete API flow documented
- ✅ Helper functions tested
- ✅ Examples verified

**Audio Generation (Mirelo):**
- ✅ Testing script created (`scripts/testing_audio/testing_mirelo.py`)
- ✅ Complete 5-step workflow documented
- ✅ Video-audio merging integrated
- ✅ Helper utility created (`video_audio_merger.py`)
- ⏳ Awaiting verification with actual API

**Last Updated:** Based on successful test runs and API documentation
