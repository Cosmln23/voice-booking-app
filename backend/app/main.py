from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.cors import get_cors_config, log_cors_config
from app.database import database
from app.api import appointments, clients, services, statistics, agent, business_settings
from app.api.endpoints import voice
from app.websockets.endpoints import router as websocket_router

# Setup logging
setup_logging(debug=settings.debug)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("Starting Voice Booking App API...")
    
    # Skip everything that might hang - just start the server
    print("Skipping database and other connections for fast startup")
    
    yield
    
    # Shutdown
    print("Shutting down Voice Booking App API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Voice Booking App API for salon appointment management",
    lifespan=lifespan,
)

# Add CORS middleware with enhanced configuration
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    **cors_config
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Enhanced HTTP exception handler with logging"""
    logger.error(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": str(request.url),
            "method": request.method,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": logger.handlers[0].formatter.formatTime(
                    logger.makeRecord(
                        logger.name, 0, "", 0, "", (), None
                    )
                ) if logger.handlers else None
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler for unexpected errors"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error"
            }
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Voice Booking App API",
        "version": "1.0.0",
        "database": "mock_mode"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(appointments.router, prefix="/api", tags=["appointments"])
app.include_router(clients.router, prefix="/api", tags=["clients"])
app.include_router(services.router, prefix="/api", tags=["services"])
app.include_router(statistics.router, prefix="/api", tags=["statistics"])
app.include_router(agent.router, prefix="/api", tags=["agent"])
app.include_router(business_settings.router, prefix="/api", tags=["settings"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])

# Include WebSocket router
app.include_router(websocket_router, prefix="", tags=["websockets"])


if __name__ == "__main__":
    import os
    # Use PORT environment variable if available (Railway sets this)
    port = int(os.getenv("PORT", settings.port))
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=port,
        reload=settings.debug,
        log_config=None  # Disable uvicorn logging, use our custom logging
    )