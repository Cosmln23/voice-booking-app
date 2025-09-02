"""
CORS Configuration and Domain Validation
Enhanced CORS handling for production deployment
"""

import re
from typing import List
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_allowed_origins() -> List[str]:
    """Get list of allowed CORS origins with environment-based configuration"""
    
    # Base origins from settings
    origins = settings.cors_origins.copy()
    
    # Add environment-specific origins
    if settings.debug:
        # Development origins
        additional_dev_origins = [
            "http://localhost:3001",  # Alternative Next.js port
            "http://localhost:8080",  # Alternative dev server
            "http://127.0.0.1:3001",
            "http://127.0.0.1:8080",
        ]
        origins.extend(additional_dev_origins)
    else:
        # Production origins
        additional_prod_origins = [
            "https://voice-booking-app-staging.vercel.app",  # Staging frontend
            "https://voice-booking-app-git-*.vercel.app",   # Git branch deployments
        ]
        origins.extend(additional_prod_origins)
    
    # Remove duplicates and return
    return list(set(origins))


def is_allowed_origin(origin: str) -> bool:
    """
    Check if an origin is allowed based on patterns and exact matches
    Handles wildcard patterns like *.vercel.app
    """
    if not origin:
        return False
    
    allowed_origins = get_allowed_origins()
    
    # Check exact matches first
    if origin in allowed_origins:
        return True
    
    # Check wildcard patterns
    for allowed in allowed_origins:
        if '*' in allowed:
            # Convert wildcard pattern to regex
            pattern = allowed.replace('*', '[a-zA-Z0-9-]+')
            escaped_pattern = re.escape(pattern)
            final_pattern = escaped_pattern.replace(r'\[a-zA-Z0-9-\]\+', '[a-zA-Z0-9-]+')
            pattern = f"^{final_pattern}$"
            
            if re.match(pattern, origin):
                logger.info(f"Origin {origin} matched wildcard pattern {allowed}")
                return True
    
    logger.warning(f"Origin {origin} not allowed. Allowed origins: {allowed_origins}")
    return False


def get_cors_config() -> dict:
    """Get CORS middleware configuration with regex support for Vercel domains"""
    
    # Static origins for localhost development
    static_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
    ]
    
    return {
        "allow_origins": static_origins,
        "allow_origin_regex": r"^https:\/\/.*\.vercel\.app$",  # All Vercel domains
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Client-Version",
            "User-Agent"
        ],
        "expose_headers": [
            "X-Total-Count",
            "X-Page-Count", 
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset"
        ],
        "max_age": 3600  # 1 hour preflight cache
    }


def log_cors_config():
    """Log current CORS configuration for debugging"""
    config = get_cors_config()
    logger.info(
        "CORS configuration loaded with regex support",
        extra={
            "static_origins": config["allow_origins"],
            "vercel_regex": config["allow_origin_regex"],
            "allow_credentials": config["allow_credentials"],
            "allow_methods": config["allow_methods"],
            "debug_mode": settings.debug
        }
    )