# ProductFlow - AI-Powered Product Video Generator

<div align="center">
  
  **Transform your product images into professional 30-second advertisement videos with AI**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![React 19+](https://img.shields.io/badge/react-19+-blue.svg)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-blue.svg)](https://www.typescriptlang.org/)
</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Workflow](#workflow)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview Project

**ProductFlow** is an end-to-end AI-powered platform that automatically generates professional product advertisement videos. Simply upload your product image, provide some basic information, and let AI create a compelling 30-second video with four distinct scenes: Hook, Problem, Solution, and Call-to-Action.

### What Makes ProductFlow Special?

- 🤖 **Fully Automated**: From image upload to final video, everything is AI-powered
- 🎨 **Customizable**: Control brand colors, tone, and visual style
- ⚡ **Fast**: Parallel video generation for all scenes simultaneously
- 🎬 **Professional**: Cinema-quality scene descriptions with detailed audio/visual elements
- 🔄 **Iterative**: Regenerate any scene or image until it's perfect
- 📱 **Responsive**: Modern, mobile-friendly interface

---

## ✨ Features

### Core Features

- **🖼️ Image Generation**: AI-generated product images for each video scene using Runware API
- **📝 Scene Description**: Detailed scene descriptions with camera work, lighting, and audio design
- **🎥 Video Generation**: Parallel video generation for all four scenes using Luma AI
- **🎞️ Video Merging**: Automatic merging of scenes into a final 30-second video
- **🔄 Regeneration**: Regenerate individual images, scenes, or videos with custom feedback
- **💾 Session Management**: Persistent sessions to save progress across the workflow

### User Experience

- **Intuitive Onboarding**: Step-by-step form to capture product details
- **Drag & Drop Upload**: Easy product and logo image uploads with compression
- **Real-time Progress**: Live progress tracking for image and video generation
- **Interactive Review**: Approve or regenerate content at each stage
- **Responsive Design**: Beautiful UI built with React and Tailwind CSS

---

## 🏗️ Architecture

ProductFlow follows a modern full-stack architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Onboarding│  │  Upload  │  │  Images  │  │  Videos  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Form   │  │  Upload  │  │  Images  │  │  Videos  │   │
│  │   API    │  │   API    │  │   API    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Service Layer                            │  │
│  │  • Session Manager  • OpenAI Service                 │  │
│  │  • Runware Service  • Luma Service                   │  │
│  │  • FFmpeg Service   • Error Handling                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  OpenAI  │  │ Runware  │  │ Luma AI  │  │  FFmpeg  │   │
│  │  Vision  │  │   API    │  │   API    │  │  Local   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Frontend**: React SPA with TypeScript, React Router, and Tailwind CSS
2. **Backend**: FastAPI server with async support and Pydantic validation
3. **Session Management**: In-memory session storage with file-based persistence
4. **AI Services**: Integration with OpenAI, Runware, and Luma AI APIs
5. **Video Processing**: FFmpeg for video merging and processing

---

## 🛠️ Tech Stack

### Frontend
- **React 19** - UI framework
- **TypeScript 5.9** - Type safety
- **Vite 7** - Build tool and dev server
- **React Router 7** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS 4** - Utility-first CSS
- **React Dropzone** - File upload

### Backend
- **Python 3.10+** - Programming language
- **FastAPI 0.104+** - Web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Pillow** - Image processing
- **FFmpeg-python** - Video processing
- **Python-dotenv** - Environment management

### AI Services
- **OpenAI GPT-4 Vision** - Image analysis and prompt generation
- **Runware API** - Image generation
- **Luma AI** - Video generation from images

### DevOps
- **Git** - Version control
- **npm** - Frontend package manager
- **pip** - Python package manager
- **FFmpeg** - Video processing binary

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18+** and npm
- **Python 3.10+** and pip
- **FFmpeg** (for video processing)
- **Git**

### API Keys Required

You'll need API keys for the following services:

1. **OpenAI API** - For GPT-4 Vision (image analysis and prompts)
2. **Runware API** - For image generation
3. **Luma AI API** - For video generation

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/productflow.git
cd productflow
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_openai_key
# RUNWARE_API_KEY=your_runware_key
# LUMA_API_KEY=your_luma_key
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file (optional, for custom API URL)
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

#### 4. Install FFmpeg

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### Running the Application

#### Start Backend Server

```bash
cd backend
# Activate venv if not already activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 📁 Project Structure

```
productflow/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   │   ├── form.py        # Form submission
│   │   │   ├── upload.py      # File uploads
│   │   │   ├── images.py      # Image generation
│   │   │   ├── scenes.py      # Scene descriptions
│   │   │   ├── videos.py      # Video generation
│   │   │   └── session.py     # Session management
│   │   ├── core/              # Core utilities
│   │   │   ├── errors.py      # Error handling
│   │   │   └── config.py      # Configuration
│   │   ├── models/            # Pydantic models
│   │   │   ├── form.py
│   │   │   ├── scene.py
│   │   │   ├── video.py
│   │   │   └── session.py
│   │   ├── services/          # Business logic
│   │   │   ├── session_manager.py
│   │   │   ├── openai_service.py
│   │   │   ├── runware_service.py
│   │   │   ├── luma_service.py
│   │   │   ├── video_service.py
│   │   │   └── ffmpeg_service.py
│   │   ├── prompts/           # AI prompts
│   │   └── main.py            # FastAPI app
│   ├── uploads/               # Uploaded files
│   ├── outputs/               # Generated videos
│   ├── requirements.txt
│   └── .env
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   │   ├── LandingPage.tsx
│   │   │   ├── OnboardingForm.tsx
│   │   │   ├── UploadPage.tsx
│   │   │   ├── ImageGenerationLoading.tsx
│   │   │   ├── ImageGallery.tsx
│   │   │   ├── SceneDescriptionReview.tsx
│   │   │   └── VideoGenerationLoading.tsx
│   │   ├── services/          # API services
│   │   │   └── api.ts
│   │   ├── types/             # TypeScript types
│   │   │   └── index.ts
│   │   ├── utils/             # Utilities
│   │   │   └── session.ts
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── package.json
│   └── vite.config.ts
├── .kiro/                      # Kiro IDE specs
│   └── specs/
│       └── productflow-fullstack/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── README.md
├── LICENSE
└── .gitignore
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Session Management
- `POST /api/session/create` - Create new session
- `GET /api/session/{session_id}` - Get session data

#### Form Submission
- `POST /api/form/submit` - Submit product information

#### File Upload
- `POST /api/upload/product` - Upload product image
- `POST /api/upload/logo` - Upload logo image (optional)

#### Image Generation
- `POST /api/images/generate` - Generate images for all scenarios
- `POST /api/images/regenerate` - Regenerate specific image

#### Scene Descriptions
- `POST /api/scenes/generate-descriptions` - Generate scene descriptions
- `POST /api/scenes/regenerate-description` - Regenerate specific scene

#### Video Generation
- `POST /api/videos/generate-scenes` - Start parallel video generation
- `GET /api/videos/status/{job_id}` - Get video generation status
- `POST /api/videos/regenerate-scene` - Regenerate specific video
- `POST /api/videos/merge` - Merge scenes into final video

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

---

## 🔄 Workflow

ProductFlow follows a structured workflow with 8 main steps:

### 1. Landing Page
- Welcome screen with product overview
- "Get Started" button to begin

### 2. Onboarding Form
- Product name and category
- Target audience and main benefit
- Brand colors and tone
- Target platform
- Scene description preferences

### 3. Image Upload
- Upload product image (required)
- Upload logo image (optional)
- Automatic image compression

### 4. Image Generation
- AI analyzes product image
- Generates 4+ images for each scenario:
  - **Hook**: Attention-grabbing opening
  - **Problem**: Highlight the problem
  - **Solution**: Show your product solving it
  - **CTA**: Call-to-action

### 5. Image Selection
- Review generated images
- Select one image per scenario
- Regenerate any image with custom prompts

### 6. Scene Description Review
- AI generates detailed scene descriptions
- Includes visual, audio, and camera details
- Approve or regenerate with feedback

### 7. Video Generation
- Parallel generation of all 4 scenes
- Real-time progress tracking
- Individual scene retry on failure

### 8. Final Video
- Review individual scene videos
- Merge into final 30-second video
- Download or share

---

## ⚙️ Configuration

### Backend Configuration (.env)

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
RUNWARE_API_KEY=your_runware_api_key
LUMA_API_KEY=your_luma_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

# Image Processing
MAX_IMAGE_DIMENSION=1024
IMAGE_QUALITY=85

# Video Processing
VIDEO_FPS=30
VIDEO_CODEC=libx264
AUDIO_CODEC=aac

# Session
SESSION_TIMEOUT=3600  # 1 hour
```

### Frontend Configuration (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_video_api.py

# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

### Manual Testing

See `TESTING_SESSION_ID.md` for testing mode configuration that bypasses session validation.

---

## 🚢 Deployment

### Backend Deployment

#### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Using Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# Deploy dist/ folder to your hosting service
# (Vercel, Netlify, AWS S3, etc.)
```

### Environment Variables

Make sure to set all required environment variables in your deployment platform.

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** - For GPT-4 Vision API
- **Runware** - For image generation API
- **Luma AI** - For video generation API
- **FastAPI** - For the amazing web framework
- **React Team** - For the UI library
- **Tailwind CSS** - For the utility-first CSS framework

---

## 📞 Support

For support, please:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs`

---

## 🗺️ Roadmap

- [ ] Add more video templates
- [ ] Support for multiple languages
- [ ] Batch processing for multiple products
- [ ] Advanced video editing features
- [ ] Integration with social media platforms
- [ ] Analytics and performance tracking
- [ ] Team collaboration features
- [ ] Custom branding options

---

<div align="center">
  Made with ❤️ by the AdFlowEcomm Team
  
  ⭐ Star us on GitHub if you find this project useful!
</div>



