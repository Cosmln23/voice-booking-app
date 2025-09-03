"""
Production-ready Authentication middleware pentru Supabase JWT verification
Uses PyJWKClient for automatic JWKS caching - SCALABLE & FAST
Recommended by ChatGPT for production environments
"""

import jwt
from jwt import PyJWKClient
from typing import Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
security = HTTPBearer()

# Production-ready JWKS configuration
def get_jwks_config():
    """Get correct Supabase JWKS URL and issuer"""
    if not settings.supabase_url:
        raise HTTPException(status_code=500, detail="Supabase URL not configured")
    
    # CORRECT Supabase Auth endpoints (not REST API)
    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    issuer = f"{settings.supabase_url}/auth/v1"
    
    logger.debug(f"JWKS URL: {jwks_url}")
    logger.debug(f"Issuer: {issuer}")
    
    return jwks_url, issuer

# Initialize PyJWKClient with automatic caching
JWKS_URL, ISSUER = get_jwks_config()
jwks_client = PyJWKClient(JWKS_URL)

logger.info(f"✅ PyJWKClient initialized with JWKS: {JWKS_URL}")


async def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    HYBRID Production-ready JWT verification
    1. Try PyJWKClient local validation (FAST)
    2. Fallback to Supabase introspection if JWKS empty (RELIABLE)
    """
    try:
        # FIRST: Try local JWKS validation (preferred)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        
        # Decode and verify JWT locally
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={
                "verify_exp": True,
                "verify_iss": True, 
                "verify_aud": False,  # Supabase poate avea aud diferit
            }
        )
        
        logger.debug(f"JWT verified locally for user: {payload.get('sub')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidIssuerError:
        logger.warning(f"Invalid issuer in JWT token, expected: {ISSUER}")
        raise HTTPException(status_code=401, detail="Invalid token issuer")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as jwks_error:
        # FALLBACK: If JWKS fails (no keys, network, etc), try introspection
        logger.warning(f"JWKS validation failed ({jwks_error}), trying fallback introspection")
        
        try:
            user_info = await fallback_user_introspection(token)
            logger.info("Successfully used fallback introspection")
            
            # Convert to JWT-like payload format
            return {
                'sub': user_info['user_id'],
                'email': user_info['email'],
                'role': user_info['role'],
                'aud': 'authenticated',
                'iss': ISSUER
            }
        except Exception as fallback_error:
            logger.error(f"Both JWKS and introspection failed: JWKS={jwks_error}, Introspection={fallback_error}")
            raise HTTPException(status_code=401, detail="Authentication failed")


async def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency pentru user authentication
    Production-ready with local JWT validation
    
    Returns: User info din JWT claims
    Raises: HTTPException 401 dacă authentication fails
    """
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = credentials.credentials.strip()
        
        if not token:
            raise HTTPException(status_code=401, detail="Empty token")
        
        # Verify JWT token (hybrid approach)
        payload = await verify_supabase_jwt(token)
        
        # Extract user info
        user_info = {
            'user_id': payload.get('sub'),
            'email': payload.get('email'),
            'role': payload.get('role', 'authenticated'),
            'aud': payload.get('aud'),
            'exp': payload.get('exp'),
            'iss': payload.get('iss')
        }
        
        if not user_info['user_id']:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        logger.debug(f"User authenticated: {user_info['email']} (ID: {user_info['user_id']})")
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Optional: Admin role check
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
    """Test auth system health - production ready"""
    try:
        # Test JWKS availability
        jwks_url, issuer = get_jwks_config()
        
        # Test if PyJWKClient can fetch keys
        keys = jwks_client.get_jwk_set()
        key_count = len(keys.get('keys', []))
        
        return {
            "status": "healthy",
            "jwks_url": jwks_url,
            "issuer": issuer,
            "jwks_keys_available": key_count,
            "supabase_configured": bool(settings.supabase_url and settings.supabase_anon_key),
            "auth_type": "PyJWKClient (Production)"
        }
        
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "jwks_url": JWKS_URL,
            "issuer": ISSUER,
            "supabase_configured": bool(settings.supabase_url and settings.supabase_anon_key),
            "auth_type": "PyJWKClient (Production)"
        }


# Fallback introspection (DOAR pentru debugging/emergency)
async def fallback_user_introspection(token: str) -> Dict[str, Any]:
    """
    Fallback method - DOAR pentru debugging
    NU folosești în producție normal
    """
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_anon_key
                },
                timeout=5
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.warning("Using fallback introspection - should not happen in prod")
                return {
                    'user_id': user_data.get('id'),
                    'email': user_data.get('email'),
                    'role': user_data.get('role', 'authenticated')
                }
            else:
                raise HTTPException(status_code=401, detail="Token validation failed")
                
    except Exception as e:
        logger.error(f"Fallback introspection failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")