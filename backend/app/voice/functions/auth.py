"""
Voice Authentication Strategy
Handles authentication and authorization for voice-based interactions
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

from app.core.logging import get_logger
from app.core.config import settings
from app.voice.functions.errors import VoiceError

logger = get_logger(__name__)


class VoiceAuthError(VoiceError):
    """Voice authentication specific error"""
    pass


async def get_voice_user_context(supabase_client) -> Dict[str, Any]:
    """
    Get Voice User Context
    
    For voice calls, we need to establish user context without traditional JWT auth.
    This function handles the business owner context for voice service operations.
    
    Voice calls are made TO the business, so we authenticate as the business owner
    who configured the voice service.
    
    Args:
        supabase_client: Supabase client instance
        
    Returns:
        Dict with user context including user_id, business_info, permissions
        
    Raises:
        VoiceAuthError: If voice authentication fails
    """
    try:
        logger.info("Establishing voice user context")
        
        # For voice service, we operate in the context of the business owner
        # This should be configured during voice service setup
        
        # Method 1: Use service role key to get business owner context
        # The business owner is determined by the phone number being called
        # or by the Twilio account configuration
        
        voice_business_user_id = await _get_voice_business_owner_id(supabase_client)
        
        if not voice_business_user_id:
            raise VoiceAuthError("No voice business owner configured")
        
        # Validate that this user exists and has voice permissions
        user_info = await _validate_voice_user(voice_business_user_id, supabase_client)
        
        if not user_info:
            raise VoiceAuthError(f"Voice business user not found: {voice_business_user_id}")
        
        logger.info(f"Voice context established for business owner: {voice_business_user_id}")
        
        return {
            "user_id": voice_business_user_id,
            "auth_type": "voice_service",
            "business_name": user_info.get("business_name", "Salon Voice Booking"),
            "phone_number": user_info.get("phone_number"),
            "permissions": ["voice_booking", "create_appointments", "manage_clients"],
            "session_start": datetime.now(),
            "context": "business_owner"
        }
        
    except VoiceAuthError:
        raise
    except Exception as e:
        logger.error(f"Error establishing voice user context: {e}", exc_info=True)
        raise VoiceAuthError("Failed to establish voice authentication context")


async def authenticate_voice_session(
    twilio_call_sid: Optional[str] = None,
    caller_number: Optional[str] = None,
    called_number: Optional[str] = None,
    supabase_client = None
) -> Dict[str, Any]:
    """
    Authenticate Voice Session
    
    Authenticates a voice session based on Twilio call information.
    
    Args:
        twilio_call_sid: Twilio Call SID for tracking
        caller_number: Phone number of the caller (customer)
        called_number: Phone number being called (business)
        supabase_client: Supabase client instance
        
    Returns:
        Dict with voice session authentication info
    """
    try:
        logger.info(f"Authenticating voice session: {twilio_call_sid}, from {caller_number} to {called_number}")
        
        # Get business owner context based on called number
        user_context = await get_voice_user_context(supabase_client)
        
        # Validate the called number belongs to this business
        if called_number:
            is_valid_business_number = await _validate_business_phone_number(
                called_number, user_context["user_id"], supabase_client
            )
            
            if not is_valid_business_number:
                logger.warning(f"Call to unregistered business number: {called_number}")
                # Still allow the call but log the warning
        
        # Create voice session record
        voice_session = await _create_voice_session(
            twilio_call_sid=twilio_call_sid,
            caller_number=caller_number,
            called_number=called_number,
            business_user_id=user_context["user_id"],
            supabase_client=supabase_client
        )
        
        return {
            "success": True,
            "session_id": voice_session["id"],
            "user_context": user_context,
            "caller_info": {
                "phone": caller_number,
                "call_sid": twilio_call_sid
            },
            "business_info": {
                "name": user_context["business_name"],
                "phone": called_number
            },
            "authenticated_at": datetime.now().isoformat()
        }
        
    except VoiceAuthError:
        raise
    except Exception as e:
        logger.error(f"Error authenticating voice session: {e}", exc_info=True)
        raise VoiceAuthError("Voice session authentication failed")


async def validate_voice_operation_permissions(
    operation: str,
    user_context: Dict[str, Any]
) -> bool:
    """
    Validate Voice Operation Permissions
    
    Checks if the current voice context has permission for specific operations.
    
    Args:
        operation: Operation to validate ("create_appointment", "access_clients", etc.)
        user_context: Current voice user context
        
    Returns:
        bool: True if operation is allowed
    """
    try:
        if user_context.get("auth_type") != "voice_service":
            return False
        
        permissions = user_context.get("permissions", [])
        
        permission_map = {
            "get_services": "voice_booking",
            "check_availability": "voice_booking",
            "create_appointment": "create_appointments",
            "find_client": "manage_clients",
            "access_client_history": "manage_clients",
            "modify_appointment": "create_appointments"
        }
        
        required_permission = permission_map.get(operation, "voice_booking")
        return required_permission in permissions
        
    except Exception as e:
        logger.error(f"Error validating voice permissions: {e}")
        return False


async def _get_voice_business_owner_id(supabase_client) -> Optional[str]:
    """
    Get Voice Business Owner ID
    
    Determines which user account owns the voice service.
    This can be configured through environment variables or database settings.
    """
    try:
        # Method 1: Environment variable (for single-tenant setup)
        env_user_id = os.getenv("VOICE_BUSINESS_OWNER_ID")
        if env_user_id:
            return env_user_id
        
        # Method 2: Query business_settings for voice-enabled user
        # This allows multiple businesses to use voice service
        try:
            response = supabase_client.table("business_settings").select(
                "user_id, business_name, voice_enabled"
            ).eq("voice_enabled", True).limit(1).execute()
            
            if response.data:
                return response.data[0]["user_id"]
        except Exception as e:
            logger.error(f"Error querying voice business owner: {e}")
        
        # Method 3: Use the first active user as fallback
        # This is for development/demo purposes
        try:
            response = supabase_client.auth.admin.list_users()
            if response.users:
                return response.users[0].id
        except Exception as e:
            logger.error(f"Error getting fallback user: {e}")
        
        return None
        
    except Exception as e:
        logger.error(f"Error determining voice business owner: {e}")
        return None


async def _validate_voice_user(user_id: str, supabase_client) -> Optional[Dict[str, Any]]:
    """Validate that the user exists and can use voice services"""
    try:
        # Get user info from auth
        user = supabase_client.auth.admin.get_user_by_id(user_id)
        if not user:
            return None
        
        # Get business settings
        response = supabase_client.table("business_settings").select(
            "business_name, phone_number, voice_enabled"
        ).eq("user_id", user_id).limit(1).execute()
        
        business_info = response.data[0] if response.data else {}
        
        return {
            "user_id": user_id,
            "email": user.user.email,
            "business_name": business_info.get("business_name", "Salon Voice Booking"),
            "phone_number": business_info.get("phone_number"),
            "voice_enabled": business_info.get("voice_enabled", True)
        }
        
    except Exception as e:
        logger.error(f"Error validating voice user {user_id}: {e}")
        return None


async def _validate_business_phone_number(
    called_number: str,
    business_user_id: str,
    supabase_client
) -> bool:
    """Validate that the called number belongs to this business"""
    try:
        response = supabase_client.table("business_settings").select(
            "phone_number"
        ).eq("user_id", business_user_id).limit(1).execute()
        
        if not response.data:
            return False
        
        registered_phone = response.data[0].get("phone_number")
        
        # Clean and compare phone numbers
        cleaned_called = ''.join(filter(str.isdigit, called_number or ''))
        cleaned_registered = ''.join(filter(str.isdigit, registered_phone or ''))
        
        return cleaned_called.endswith(cleaned_registered) or cleaned_registered.endswith(cleaned_called)
        
    except Exception as e:
        logger.error(f"Error validating business phone number: {e}")
        return False


async def _create_voice_session(
    twilio_call_sid: Optional[str],
    caller_number: Optional[str],
    called_number: Optional[str],
    business_user_id: str,
    supabase_client
) -> Dict[str, Any]:
    """Create a voice session record for tracking and analytics"""
    try:
        session_data = {
            "id": f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{twilio_call_sid or 'test'}",
            "twilio_call_sid": twilio_call_sid,
            "caller_number": caller_number,
            "called_number": called_number,
            "business_user_id": business_user_id,
            "session_start": datetime.now().isoformat(),
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # Insert into voice_sessions table (if it exists)
        try:
            response = supabase_client.table("voice_sessions").insert(session_data).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            logger.warning(f"Could not create voice session record: {e}")
        
        # Return session data even if DB insert failed
        return session_data
        
    except Exception as e:
        logger.error(f"Error creating voice session: {e}")
        return {
            "id": f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }


# Voice session management utilities

async def end_voice_session(
    session_id: str,
    supabase_client,
    session_summary: Optional[Dict[str, Any]] = None
):
    """End a voice session and update records"""
    try:
        update_data = {
            "status": "completed",
            "session_end": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if session_summary:
            update_data.update({
                "appointments_created": session_summary.get("appointments_created", 0),
                "client_interactions": session_summary.get("client_interactions", 0),
                "session_duration": session_summary.get("duration_seconds", 0)
            })
        
        # Update voice session record
        try:
            supabase_client.table("voice_sessions").update(update_data).eq("id", session_id).execute()
        except Exception as e:
            logger.warning(f"Could not update voice session {session_id}: {e}")
        
        logger.info(f"Voice session ended: {session_id}")
        
    except Exception as e:
        logger.error(f"Error ending voice session {session_id}: {e}")