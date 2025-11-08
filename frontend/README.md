# ProductFlow Frontend

React + TypeScript + Vite application for ProductFlow - an AI-powered product video generator.

## Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets (logo, images)
│   ├── components/      # Reusable React components
│   ├── pages/           # Page components
│   ├── services/        # API service layer
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main app component with routing
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles with Tailwind
├── public/              # Public static files
└── package.json         # Dependencies and scripts
```

## Features

- **React 19** with TypeScript for type-safe development
- **Vite** for fast development and optimized builds
- **React Router** for client-side routing
- **TailwindCSS** for styling with brand colors
- **Axios** for API communication
- **Session Management** with localStorage

## Brand Colors

- Primary Blue: `#2596be` (accessible via `text-brand-blue` or `bg-brand-blue`)
- Secondary Green: `#a0d053` (accessible via `text-brand-green` or `bg-brand-green`)

## Routes

- `/` - Landing page
- `/onboarding` - Product information form
- `/upload` - Product image and logo upload
- `/images` - Generated image gallery
- `/scenes` - Scene description review
- `/videos` - Video scene review
- `/final` - Final video preview and download

## Session Management

The application uses localStorage to maintain a session ID across the workflow:
- Session ID is automatically generated on first visit
- Persists across page refreshes
- Used for all API requests to maintain state

## API Service

The `services/api.ts` file provides a centralized API layer with:
- Axios instance with base URL configuration
- Request interceptor to add session ID
- Response interceptor for error handling
- Typed API methods for all endpoints

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```
VITE_API_BASE_URL=http://localhost:8000
```

## TypeScript

The project uses TypeScript with strict mode enabled. Type definitions are located in `src/types/index.ts`.

## Next Steps

Future tasks will implement:
- Landing page component
- Onboarding form with validation
- File upload with drag-and-drop
- Image gallery with regeneration
- Scene description review
- Video generation and review
- Final video preview and download
