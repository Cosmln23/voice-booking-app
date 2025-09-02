"""
Authentication middleware pentru Supabase JWT verification
Implements require_user() dependency function pentru API protection
"""

import jwt
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.logging import get_logger
from functools import lru_cache

logger = get_logger(__name__)
security = HTTPBearer()

# Cache pentru JWKS keys
_jwks_cache: Optional[Dict[str, Any]] = None


@lru_cache(maxsize=1)
def get_jwks_url() -> str:
    """Generate JWKS URL pentru Supabase project"""
    if not settings.supabase_url:
        raise HTTPException(status_code=500, detail="Supabase URL not configured")
    
    # Extract project ref din URL
    # Format: https://projectref.supabase.co
    project_ref = settings.supabase_url.split('//')[1].split('.')[0]
    jwks_url = f"https://{project_ref}.supabase.co/rest/v1/auth/jwks"
    
    logger.debug(f"JWKS URL: {jwks_url}")
    return jwks_url


def fetch_jwks() -> Dict[str, Any]:
    """Fetch și cache JWKS from Supabase"""
    global _jwks_cache
    
    try:
        jwks_url = get_jwks_url()
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        
        _jwks_cache = response.json()
        logger.info("JWKS fetched și cached successfully")
        return _jwks_cache
        
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        if _jwks_cache:
            logger.warning("Using cached JWKS")
            return _jwks_cache
        raise HTTPException(status_code=500, detail="JWT verification unavailable")


def get_signing_key(token_header: Dict[str, Any]) -> Optional[str]:
    """Extract signing key din JWKS based on token header"""
    try:
        kid = token_header.get('kid')
        if not kid:
            return None
        
        jwks = fetch_jwks()
        
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                # Convert JWK to PEM format pentru jwt library
                from jwt.algorithms import RSAAlgorithm
                return RSAAlgorithm.from_jwk(key)
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get signing key: {e}")
        return None


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify și decode Supabase JWT token"""
    try:
        # Decode header fără verification pentru a obține kid
        unverified_header = jwt.get_unverified_header(token)
        
        # Get signing key
        signing_key = get_signing_key(unverified_header)
        if not signing_key:
            raise HTTPException(status_code=401, detail="Invalid token signature")
        
        # Verify și decode token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=['RS256'],
            audience='authenticated',  # Supabase audience
            options={'verify_exp': True, 'verify_aud': True}
        )
        
        logger.debug(f"JWT verified for user: {payload.get('sub')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency function pentru user authentication
    Returns: User info din JWT claims
    Raises: HTTPException cu 401 dacă authentication fails
    """
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = credentials.credentials
        
        # Verify JWT token
        payload = verify_jwt_token(token)
        
        # Extract user info
        user_info = {
            'user_id': payload.get('sub'),
            'email': payload.get('email'),
            'role': payload.get('role', 'authenticated'),
            'aud': payload.get('aud'),
            'exp': payload.get('exp')
        }
        
        if not user_info['user_id']:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        logger.debug(f"User authenticated: {user_info['email']}")
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Optional: Function pentru checking specific roles
def require_admin(user_info: Dict[str, Any] = Depends(require_user)) -> Dict[str, Any]:
    """
    Advanced dependency pentru admin-only endpoints
    Usage: user = Depends(require_admin)
    """
    if user_info.get('role') != 'admin':
        logger.warning(f"Unauthorized admin access attempt: {user_info.get('email')}")
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_info


# Health check pentru auth system
async def auth_health_check() -> Dict[str, Any]:
    """Test auth system health"""
    try:
        jwks_url = get_jwks_url()
        
        # Test JWKS availability
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        
        return {
            "status": "healthy",
            "jwks_url": jwks_url,
            "supabase_configured": bool(settings.supabase_url and settings.supabase_anon_key)
        }
        
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "supabase_configured": bool(settings.supabase_url and settings.supabase_anon_key)
        }