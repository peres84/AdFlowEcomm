# Documentation Index

Complete documentation for the AdFlowEcomm video generation system.

---

## 📚 Main Documentation

### [VIDEO_RW_API_FLOW.md](VIDEO_RW_API_FLOW.md)
**Complete Runware API Integration Guide**

Step-by-step guide for implementing video generation with Runware API:
- ✅ Verified working configuration (MiniMax, 244s generation)
- Complete workflow (upload → generate → poll → download)
- Request/response structures
- Error handling patterns
- Full working code examples

**Use this when:** Implementing video generation in your fullstack application

---

### [video_models.md](video_models.md)
**Video Model Reference**

Complete reference for available video models on Runware:
- Model providers (MiniMax, KlingAI, PixVerse, etc.)
- Duration limits and dimensions
- Payload parameters
- Model-specific requirements

**Use this when:** Choosing which video model to use or troubleshooting model errors

---

## 🛠️ Helper Functions

### [../scripts/README.md](../scripts/README.md)
**Helper Functions - Complete Reference**

All helper utilities for video generation:
- Image resizing (`resizer_img.py`)
- Format conversion (`extension_changer_img.py`)
- Video generation (`video_helpers.py`)
- Multi-scene generation (`scene_generator.py`)

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

### [../testing/](../testing/)
**Working Code Examples**

Verified working examples:
- `testing_runware.py` - ✅ Basic single video generation (verified)
- `example_using_helpers.py` - Using helper functions
- `example_4_scenes.py` - Complete 4-scene workflow
- `test_fastest_models.py` - Model comparison testing

**Use this when:** Looking for working code to test or reference

---

## 🚀 Quick Navigation

**I want to...**

- **Understand the API flow** → [VIDEO_RW_API_FLOW.md](VIDEO_RW_API_FLOW.md)
- **Use helper functions** → [../scripts/README.md](../scripts/README.md)
- **Choose a video model** → [video_models.md](video_models.md)
- **See working examples** → [../testing/](../testing/)
- **Understand ProductFlow** → [../product-guidelines/](../product-guidelines/)

---

## ✅ Verification Status

All documentation is based on tested and verified code:

- ✅ MiniMax model working (244s generation time)
- ✅ Complete API flow documented
- ✅ Helper functions tested
- ✅ Examples verified

**Last Updated:** Based on successful test runs with Runware API
