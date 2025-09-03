"""
Supabase User-specific Client Helper
Creates Supabase client with user JWT for RLS enforcement
"""

from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_supabase_for_user(jwt_token: str) -> Client:
    """
    Create Supabase client with user JWT for RLS enforcement
    
    Args:
        jwt_token: User's JWT access token from Supabase auth
        
    Returns:
        Supabase client configured with user context
        
    Raises:
        ValueError: If Supabase credentials not configured
    """
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise ValueError("Supabase credentials not configured")
    
    # Create client with anon key
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    
    # Set user JWT - this enables RLS policies to work with auth.uid()
    client.postgrest.auth(jwt_token)
    
    logger.debug("Created Supabase client with user JWT for RLS")
    return client


def create_admin_supabase_client() -> Optional[Client]:
    """
    Create Supabase client with service role (bypasses RLS)
    Use ONLY for admin operations, statistics, system maintenance
    
    Returns:
        Service role client or None if service key not configured
    """
    if not settings.supabase_url or not settings.supabase_service_key:
        logger.warning("Supabase service key not configured")
        return None
    
    client = create_client(settings.supabase_url, settings.supabase_service_key)
    logger.debug("Created Supabase admin client (bypasses RLS)")
    return client


class UserSupabaseManager:
    """
    Context manager for user-specific Supabase operations
    Ensures proper JWT context for RLS enforcement
    """
    
    def __init__(self, jwt_token: str):
        self.jwt_token = jwt_token
        self.client: Optional[Client] = None
    
    def __enter__(self) -> Client:
        """Enter context with user Supabase client"""
        self.client = create_supabase_for_user(self.jwt_token)
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - cleanup if needed"""
        self.client = None
        
        if exc_type:
            logger.error(f"Error in user Supabase context: {exc_val}")
        return False  # Don't suppress exceptions


# Helper function for FastAPI dependency injection
def get_user_supabase_client(user_info: Dict[str, Any], jwt_token: str) -> Client:
    """
    FastAPI dependency helper for user-specific Supabase client
    
    Args:
        user_info: User info from require_user dependency
        jwt_token: JWT token from Authorization header
        
    Returns:
        Supabase client with user context
    """
    client = create_supabase_for_user(jwt_token)
    
    # Log user context for debugging
    logger.debug(
        f"Created user Supabase client",
        extra={
            "user_id": user_info.get("user_id"),
            "email": user_info.get("email")
        }
    )
    
    return client


# Utility functions for common patterns
def extract_user_id_from_jwt(user_info: Dict[str, Any]) -> str:
    """
    Extract user_id from JWT payload for created_by field
    
    Args:
        user_info: User info from require_user dependency
        
    Returns:
        User UUID string
        
    Raises:
        ValueError: If user_id not found in JWT
    """
    user_id = user_info.get("user_id")
    if not user_id:
        raise ValueError("User ID not found in JWT payload")
    
    return user_id


def ensure_created_by(data: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure data has created_by field set to current user
    
    Args:
        data: Data dictionary for create/update operations
        user_info: User info from require_user dependency
        
    Returns:
        Data with created_by field set
    """
    if "created_by" not in data or not data["created_by"]:
        data["created_by"] = extract_user_id_from_jwt(user_info)
    
    return data