from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.cors import get_cors_config, log_cors_config
from app.core.bootstrap import make_supabase_clients, test_supabase_connection
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
    logger.info("Starting Voice Booking App API...")
    
    # Initialize app state
    app.state.ready = False
    app.state.sb_anon = None
    app.state.sb_service = None
    app.state.db_connected = False
    
    try:
        # Initialize Supabase clients
        logger.info("Initializing Supabase clients...")
        app.state.sb_anon, app.state.sb_service = make_supabase_clients()
        
        # Test database connection
        app.state.db_connected = test_supabase_connection(
            app.state.sb_anon, 
            app.state.sb_service
        )
        
        if app.state.db_connected:
            logger.info("✅ Database connected successfully")
        else:
            logger.warning("⚠️ Database connection failed")
        
        # Log CORS configuration
        log_cors_config()
        logger.info("✅ CORS configuration loaded")
        
        # Verify OpenAI configuration
        if settings.openai_api_key:
            logger.info("✅ OpenAI API key configured")
        else:
            logger.warning("⚠️ OpenAI API key not configured - voice features disabled")
        
        app.state.ready = True
        logger.info("🚀 Voice Booking App API ready for production!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        # Don't raise - let health check handle the status
    
    yield
    
    # Shutdown
    logger.info("Shutting down Voice Booking App API...")
    try:
        app.state.sb_anon = None
        app.state.sb_service = None
        app.state.db_connected = False
        logger.info("✅ Database disconnected cleanly")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


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
    """Health check endpoint with database status"""
    try:
        # Check app readiness
        if not getattr(app.state, "ready", False):
            return {
                "status": "starting",
                "service": "Voice Booking App API",
                "version": settings.version,
                "database": "initializing"
            }
        
        # Test database connection using RPC or fallback
        db_status = "disconnected"
        test_client = getattr(app.state, "sb_service", None) or getattr(app.state, "sb_anon", None)
        
        if test_client:
            try:
                # Try RPC health check first
                response = test_client.rpc("health_check").execute()
                db_status = "connected" if response.data else "disconnected"
            except Exception:
                # Fallback to simple query
                try:
                    response = test_client.table("services").select("id").limit(1).execute()
                    db_status = "connected"
                except Exception:
                    db_status = "disconnected"
        
        # Check OpenAI configuration
        openai_status = "configured" if settings.openai_api_key else "not_configured"
        
        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "service": "Voice Booking App API",
            "version": settings.version,
            "database": db_status,
            "openai": openai_status,
            "environment": "production" if not settings.debug else "development"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "service": "Voice Booking App API",
            "version": settings.version,
            "error": str(e)
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