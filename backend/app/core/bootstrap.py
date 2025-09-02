"""
Bootstrap utilities for single-point Supabase initialization
"""
import os
from typing import Optional, Tuple
from supabase import create_client, Client
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def _env_clean(name: str) -> str:
    """Get and clean environment variable"""
    value = os.getenv(name, "")
    return value.strip() if isinstance(value, str) else ""


def _is_valid_supabase_key(key: str) -> bool:
    """Validate Supabase key format (JWT starts with eyJ)"""
    return key and key.startswith("eyJ")


def make_supabase_clients() -> Tuple[Optional[Client], Optional[Client]]:
    """
    Create Supabase clients with proper error handling
    Returns: (sb_anon, sb_service)
    """
    url = settings.supabase_url
    anon_key = settings.supabase_anon_key
    service_key = settings.supabase_service_key
    
    if not url:
        logger.warning("SUPABASE_URL not configured")
        return None, None
    
    sb_anon = None
    sb_service = None
    
    # Create anon client
    if _is_valid_supabase_key(anon_key):
        try:
            sb_anon = create_client(url, anon_key)
            logger.info("✅ Supabase anon client created")
        except Exception as e:
            logger.error(f"Failed to create anon client: {e}")
    else:
        logger.warning("SUPABASE_ANON_KEY invalid or missing")
    
    # Create service client
    if _is_valid_supabase_key(service_key):
        try:
            sb_service = create_client(url, service_key)
            logger.info("✅ Supabase service client created")
        except Exception as e:
            logger.error(f"Failed to create service client: {e}")
    else:
        logger.warning("SUPABASE_SERVICE_KEY invalid or missing")
    
    if not (sb_anon or sb_service):
        raise RuntimeError("No valid Supabase keys configured")
    
    return sb_anon, sb_service


def test_supabase_connection(sb_anon: Optional[Client], sb_service: Optional[Client]) -> bool:
    """Test Supabase connection with fallback clients"""
    test_client = sb_service or sb_anon
    if not test_client:
        return False
    
    try:
        # Use RPC health check if available, fallback to simple query
        try:
            response = test_client.rpc("health_check").execute()
            return bool(response.data)
        except Exception:
            # Fallback to simple table query
            response = test_client.table("services").select("id").limit(1).execute()
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False