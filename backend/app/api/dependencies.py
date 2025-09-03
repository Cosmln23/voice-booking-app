"""
FastAPI dependencies for user-isolated operations
Provides dependency injection for user-specific CRUD operations with RLS
"""

from typing import Dict, Any
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth import require_user
from app.database.user_crud_clients import UserClientCRUD
from app.database.user_crud_appointments import UserAppointmentCRUD

security = HTTPBearer()


async def get_user_client_crud(
    user_info: Dict[str, Any] = Depends(require_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserClientCRUD:
    """
    FastAPI dependency for user-isolated client CRUD operations
    
    Args:
        user_info: User info from JWT verification
        credentials: JWT token from Authorization header
        
    Returns:
        UserClientCRUD instance with RLS enforcement
    """
    return UserClientCRUD(credentials.credentials, user_info)


async def get_user_appointment_crud(
    user_info: Dict[str, Any] = Depends(require_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserAppointmentCRUD:
    """
    FastAPI dependency for user-isolated appointment CRUD operations
    
    Args:
        user_info: User info from JWT verification
        credentials: JWT token from Authorization header
        
    Returns:
        UserAppointmentCRUD instance with RLS enforcement
    """
    return UserAppointmentCRUD(credentials.credentials, user_info)


# Add more user CRUD dependencies as needed:
# - get_user_service_crud
# - get_user_business_settings_crud