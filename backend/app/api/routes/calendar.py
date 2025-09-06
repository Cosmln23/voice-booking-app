"""
Calendar Management API Routes
Handles business calendar setup, validation, and management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any

from app.models.calendar_settings import CalendarSetupRequest, CalendarSettings
from app.services.calendar_management import (
    CalendarManagementService,
    setup_business_calendar_service,
    validate_business_calendar_service,
    test_business_calendar_integration
)
from app.core.auth import require_user
from app.core.bootstrap import make_supabase_clients

def get_supabase_client():
    """Get Supabase client for calendar operations"""
    sb_anon, sb_service = make_supabase_clients()
    return sb_service or sb_anon
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/setup", response_model=Dict[str, Any])
async def setup_business_calendar(
    setup_request: CalendarSetupRequest,
    current_user = Depends(require_user)
):
    """
    Set up Google Calendar integration for business
    
    Requires valid JWT token and calendar credentials.
    Creates or updates calendar settings for the business.
    """
    try:
        logger.info(f"Calendar setup request from user {current_user['user_id']}")
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Setup calendar
        success, message, calendar_settings = await setup_business_calendar_service(
            supabase_client,
            current_user["user_id"],
            setup_request
        )
        
        if success:
            return {
                "success": True,
                "message": message,
                "calendar_settings": {
                    "enabled": calendar_settings.google_calendar_enabled,
                    "calendar_id": calendar_settings.google_calendar_id,
                    "calendar_name": calendar_settings.google_calendar_name,
                    "timezone": calendar_settings.google_calendar_timezone,
                    "auto_create_events": calendar_settings.auto_create_events,
                    "created_at": calendar_settings.calendar_created_at.isoformat() if calendar_settings.calendar_created_at else None
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in calendar setup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Calendar setup failed"
        )


@router.get("/validate", response_model=Dict[str, Any])
async def validate_calendar_integration(
    current_user = Depends(require_user)
):
    """
    Validate existing calendar integration
    
    Checks if calendar credentials are valid and calendar is accessible.
    """
    try:
        logger.info(f"Calendar validation request from user {current_user['user_id']}")
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Validate calendar
        is_valid, message, calendar_info = await validate_business_calendar_service(
            supabase_client,
            current_user["user_id"]
        )
        
        return {
            "success": is_valid,
            "message": message,
            "calendar_info": calendar_info,
            "is_valid": is_valid
        }
        
    except Exception as e:
        logger.error(f"Error in calendar validation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Calendar validation failed"
        )


@router.post("/test", response_model=Dict[str, Any])
async def test_calendar_integration(
    current_user = Depends(require_user)
):
    """
    Test calendar integration by creating and deleting a test event
    
    Verifies that the calendar integration is working correctly.
    """
    try:
        logger.info(f"Calendar test request from user {current_user['user_id']}")
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Test integration
        success, message, test_results = await test_business_calendar_integration(
            supabase_client,
            current_user["user_id"]
        )
        
        return {
            "success": success,
            "message": message,
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"Error in calendar test: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Calendar test failed"
        )


@router.get("/info", response_model=Dict[str, Any])
async def get_calendar_info(
    current_user = Depends(require_user)
):
    """
    Get current calendar configuration and status
    
    Returns calendar settings and integration status.
    """
    try:
        logger.info(f"Calendar info request from user {current_user['user_id']}")
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get calendar service
        service = CalendarManagementService(supabase_client)
        calendar_info = await service.get_business_calendar_info(current_user["user_id"])
        
        if calendar_info:
            return {
                "success": True,
                "calendar_info": calendar_info
            }
        else:
            return {
                "success": False,
                "message": "No calendar configuration found",
                "calendar_info": None
            }
        
    except Exception as e:
        logger.error(f"Error getting calendar info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get calendar info"
        )


@router.put("/disable", response_model=Dict[str, Any])
async def disable_calendar_integration(
    current_user = Depends(require_user)
):
    """
    Disable calendar integration for business
    
    Disables calendar integration without deleting credentials.
    """
    try:
        logger.info(f"Calendar disable request from user {current_user['user_id']}")
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get calendar service
        service = CalendarManagementService(supabase_client)
        success, message = await service.disable_business_calendar(current_user["user_id"])
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error disabling calendar: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable calendar"
        )


@router.put("/enable", response_model=Dict[str, Any])
async def enable_calendar_integration(
    current_user = Depends(require_user)
):
    """
    Enable calendar integration for business
    
    Re-enables previously configured calendar integration.
    """
    try:
        logger.info(f"Calendar enable request from user {current_user['user_id']}")
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get current settings
        service = CalendarManagementService(supabase_client)
        calendar_info = await service.get_business_calendar_info(current_user["user_id"])
        
        if not calendar_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No calendar configuration found. Please set up calendar first."
            )
        
        if not calendar_info["configured"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Calendar not properly configured. Please complete setup first."
            )
        
        # Validate calendar access before enabling
        is_valid, validation_message, _ = await validate_business_calendar_service(
            supabase_client,
            current_user["user_id"]
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot enable calendar: {validation_message}"
            )
        
        # Get calendar settings and enable
        from app.database.crud_calendar_settings import CalendarSettingsCRUD
        calendar_crud = CalendarSettingsCRUD(supabase_client)
        settings = await calendar_crud.get_calendar_settings(current_user["user_id"])
        
        if settings:
            settings.google_calendar_enabled = True
            success = await calendar_crud.update_calendar_settings(current_user["user_id"], settings)
            
            if success:
                return {
                    "success": True,
                    "message": "Calendar integration enabled successfully"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to enable calendar integration"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar settings not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling calendar: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable calendar"
        )


@router.get("/setup-guide", response_model=Dict[str, Any])
async def get_setup_guide():
    """
    Get calendar setup guide and instructions
    
    Returns step-by-step instructions for setting up Google Calendar integration.
    """
    return {
        "setup_steps": [
            {
                "step": 1,
                "title": "Create Google Cloud Project",
                "description": "Create a new project in Google Cloud Console or use existing one",
                "details": [
                    "Go to https://console.cloud.google.com/",
                    "Create new project or select existing project",
                    "Note down the Project ID"
                ]
            },
            {
                "step": 2,
                "title": "Enable Calendar API",
                "description": "Enable Google Calendar API for your project",
                "details": [
                    "Go to APIs & Services > Library",
                    "Search for 'Google Calendar API'",
                    "Click 'Enable'"
                ]
            },
            {
                "step": 3,
                "title": "Create Service Account",
                "description": "Create a service account for server-to-server authentication",
                "details": [
                    "Go to IAM & Admin > Service Accounts",
                    "Click 'Create Service Account'",
                    "Give it a name like 'calendar-booking-service'",
                    "Skip role assignment (not needed for calendar access)"
                ]
            },
            {
                "step": 4,
                "title": "Generate Service Account Key",
                "description": "Create and download the service account credentials",
                "details": [
                    "Click on the created service account",
                    "Go to 'Keys' tab",
                    "Click 'Add Key' > 'Create new key'",
                    "Choose JSON format",
                    "Download and save the JSON file securely"
                ]
            },
            {
                "step": 5,
                "title": "Create or Share Calendar",
                "description": "Create a dedicated calendar or use existing one",
                "details": [
                    "Go to Google Calendar (calendar.google.com)",
                    "Create a new calendar for bookings",
                    "Or use your primary calendar",
                    "Copy the Calendar ID from calendar settings"
                ]
            },
            {
                "step": 6,
                "title": "Share Calendar with Service Account",
                "description": "Grant the service account access to your calendar",
                "details": [
                    "In Google Calendar, open calendar settings",
                    "Go to 'Share with specific people or groups'",
                    "Add the service account email (from JSON file)",
                    "Set permission to 'Make changes to events'"
                ]
            },
            {
                "step": 7,
                "title": "Complete Setup",
                "description": "Use the setup endpoint with your credentials",
                "details": [
                    "Use the /calendar/setup endpoint",
                    "Provide calendar name and ID",
                    "Upload the service account JSON credentials",
                    "Test the integration"
                ]
            }
        ],
        "important_notes": [
            "Keep your service account JSON file secure and never commit it to version control",
            "The service account email must have 'Make changes to events' permission on the calendar",
            "Calendar ID can be found in calendar settings under 'Integrate calendar'",
            "You can use the same service account for multiple calendars by sharing each calendar with it"
        ],
        "common_issues": [
            {
                "issue": "403 Forbidden Error",
                "solution": "Check that the service account has proper permissions on the calendar"
            },
            {
                "issue": "Calendar not found",
                "solution": "Verify the Calendar ID is correct and the calendar exists"
            },
            {
                "issue": "Invalid credentials",
                "solution": "Check that the JSON file is valid and all required fields are present"
            }
        ]
    }