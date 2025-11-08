# ProductFlow - Setup Guide

ProductFlow is an AI-powered product video generator that transforms product images into professional 30-second advertisement videos.

## Project Structure

```
productflow/
├── frontend/          # React + Vite + TypeScript frontend
├── backend/           # FastAPI Python backend
├── images/            # Project assets (logo)
├── scripts/           # Utility scripts
└── documentation/     # Project documentation
```

## Backend Setup

### Prerequisites
- Python 3.10+
- FFmpeg installed and available in PATH

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file from the example:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

6. Add your API keys to the `.env` file:
```
OPENAI_API_KEY=your-openai-api-key
RUNWARE_API_KEY=your-runware-api-key
MIRELO_API_KEY=your-mirelo-api-key
```

### Running the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Frontend Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies (already done during setup):
```bash
npm install
```

3. Create a `.env` file from the example:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

4. Update the `.env` file if needed (default points to localhost:8000)

### Running the Frontend

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Brand Assets

- Logo: `images/logo.png` (copied to `frontend/src/assets/logo.png`)
- Brand Colors:
  - Primary Blue: `#2596be`
  - Secondary Green: `#a0d053`

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY`: Your OpenAI API key
- `RUNWARE_API_KEY`: Your Runware API key
- `SESSION_TTL_MINUTES`: Session timeout (default: 30)
- `UPLOAD_DIR`: Upload directory (default: ./uploads)
- `OUTPUT_DIR`: Output directory (default: ./outputs)
- `MAX_FILE_SIZE_MB`: Max file upload size (default: 10)

### Frontend (.env)
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Development

### Backend Structure
```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic services
│   ├── prompts/      # AI prompt templates
│   └── main.py       # FastAPI application
├── uploads/          # Uploaded files
├── outputs/          # Generated videos
└── requirements.txt  # Python dependencies
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/   # React components
│   ├── pages/        # Page components
│   ├── services/     # API services
│   ├── types/        # TypeScript types
│   ├── assets/       # Static assets (logo)
│   └── App.tsx       # Main app component
└── package.json      # Node dependencies
```

## Next Steps

Follow the implementation tasks in `.kiro/specs/productflow-fullstack/tasks.md` to build out the application features.
