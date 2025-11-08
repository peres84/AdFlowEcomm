from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio
import logging
from app.api import session, form, upload, images, scenes, videos
from app.services import session_manager
from app.core import (
    ProductFlowError,
    log_error,
    create_error_response,
    setup_logging
)

# Load environment variables
load_dotenv()

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)

logger = logging.getLogger(__name__)


async def cleanup_task():
    """Background task to cleanup expired sessions every 5 minutes"""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        session_manager.cleanup_expired_sessions()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Start the cleanup task
    cleanup_task_handle = asyncio.create_task(cleanup_task())
    yield
    # Shutdown: Cancel the cleanup task
    cleanup_task_handle.cancel()
    try:
        await cleanup_task_handle
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="ProductFlow API",
    description="AI-powered product video generator API",
    version="1.0.0",
    lifespan=lifespan
)


# Global exception handlers
@app.exception_handler(ProductFlowError)
async def productflow_error_handler(request: Request, exc: ProductFlowError):
    """Handle custom ProductFlow errors"""
    log_error(
        error=exc,
        context={"path": request.url.path, "method": request.method}
    )
    
    response = create_error_response(exc, include_details=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=response
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "retry_allowed": exc.status_code >= 500,
            "timestamp": None
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "retry_allowed": False,
            "details": exc.errors(),
            "timestamp": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unexpected exceptions"""
    log_error(
        error=exc,
        context={"path": request.url.path, "method": request.method}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again.",
            "retry_allowed": True,
            "timestamp": None
        }
    )


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories for serving uploaded files and outputs
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Include routers
app.include_router(session.router)
app.include_router(form.router)
app.include_router(upload.router)
app.include_router(images.router)
app.include_router(scenes.router)
app.include_router(videos.router)

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "ProductFlow API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/stats")
async def get_stats():
    """Get API statistics including active session count"""
    try:
        active_sessions = session_manager.get_session_count()
        logger.info(f"Stats requested - Active sessions: {active_sessions}")
        return {
            "active_sessions": active_sessions
        }
    except Exception as e:
        log_error(e, context={"endpoint": "/stats"})
        raise
