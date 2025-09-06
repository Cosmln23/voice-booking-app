"""
Calendar Management Functions
Handles business-specific calendar setup, validation, and management
"""

import json
import base64
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.logging import get_logger
from app.database.crud_calendar_settings import CalendarSettingsCRUD
from app.models.calendar_settings import CalendarSettings, GoogleCalendarCredentials, CalendarSetupRequest
from app.core.config import settings

logger = get_logger(__name__)


class CalendarManagementService:
    """Service for managing business calendar setup and configuration"""
    
    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
        self.calendar_crud = CalendarSettingsCRUD(supabase_client)
    
    async def setup_business_calendar(
        self, 
        user_id: str, 
        setup_request: CalendarSetupRequest
    ) -> Tuple[bool, str, Optional[CalendarSettings]]:
        """
        Set up Google Calendar for a business
        
        Args:
            user_id: Business owner's user ID
            setup_request: Calendar setup configuration
            
        Returns:
            Tuple of (success, message, calendar_settings)
        """
        try:
            logger.info(f"Setting up calendar for business user {user_id}")
            
            # Parse and validate credentials
            try:
                credentials_dict = self._parse_credentials(setup_request.google_calendar_credentials_json)
                google_credentials = GoogleCalendarCredentials(**credentials_dict)
            except Exception as e:
                return False, f"Invalid credentials format: {str(e)}", None
            
            # Validate calendar access
            validation_result, validation_message = await self._validate_calendar_access(
                google_credentials, setup_request.google_calendar_id
            )
            
            if not validation_result:
                return False, f"Calendar validation failed: {validation_message}", None
            
            # Create calendar settings
            calendar_settings = CalendarSettings(
                google_calendar_enabled=True,
                google_calendar_id=setup_request.google_calendar_id,
                google_calendar_name=setup_request.calendar_name,
                google_calendar_credentials=google_credentials,
                google_calendar_timezone=setup_request.timezone,
                auto_create_events=setup_request.auto_create_events,
                calendar_created_at=datetime.utcnow()
            )
            
            # Check if settings already exist
            existing_settings = await self.calendar_crud.get_calendar_settings(user_id)
            
            if existing_settings:
                # Update existing settings
                success = await self.calendar_crud.update_calendar_settings(user_id, calendar_settings)
                action = "updated"
            else:
                # Create new settings
                success = await self.calendar_crud.create_calendar_settings(user_id, calendar_settings)
                action = "created"
            
            if success:
                logger.info(f"Calendar settings {action} successfully for user {user_id}")
                return True, f"Calendar {action} successfully", calendar_settings
            else:
                return False, f"Failed to save calendar settings", None
                
        except Exception as e:
            logger.error(f"Error setting up business calendar for user {user_id}: {e}", exc_info=True)
            return False, f"Setup failed: {str(e)}", None
    
    async def validate_business_calendar(self, user_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate existing business calendar configuration
        
        Args:
            user_id: Business owner's user ID
            
        Returns:
            Tuple of (is_valid, message, calendar_info)
        """
        try:
            # Get calendar settings
            settings = await self.calendar_crud.get_calendar_settings(user_id)
            
            if not settings or not settings.is_fully_configured():
                return False, "Calendar not configured", None
            
            # Test calendar access
            validation_result, validation_message = await self._validate_calendar_access(
                settings.google_calendar_credentials,
                settings.google_calendar_id
            )
            
            if not validation_result:
                return False, f"Calendar access failed: {validation_message}", None
            
            # Get calendar info
            calendar_info = await self._get_calendar_info(
                settings.google_calendar_credentials,
                settings.google_calendar_id
            )
            
            return True, "Calendar validated successfully", calendar_info
            
        except Exception as e:
            logger.error(f"Error validating calendar for user {user_id}: {e}", exc_info=True)
            return False, f"Validation error: {str(e)}", None
    
    async def test_calendar_integration(self, user_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Test calendar integration by creating a test event
        
        Args:
            user_id: Business owner's user ID
            
        Returns:
            Tuple of (success, message, test_results)
        """
        try:
            # Get calendar settings
            settings = await self.calendar_crud.get_calendar_settings(user_id)
            
            if not settings or not settings.is_fully_configured():
                return False, "Calendar not configured", None
            
            # Create test event
            test_event = {
                'summary': '[TEST] Calendar Integration Test',
                'description': 'Test event created by voice booking system',
                'start': {
                    'dateTime': datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0).isoformat() + 'Z',
                    'timeZone': settings.google_calendar_timezone,
                },
                'end': {
                    'dateTime': datetime.utcnow().replace(hour=10, minute=30, second=0, microsecond=0).isoformat() + 'Z',
                    'timeZone': settings.google_calendar_timezone,
                },
                'colorId': settings.event_color_id,
                'reminders': {
                    'useDefault': False,
                    'overrides': [{'method': 'popup', 'minutes': minutes} for minutes in settings.reminder_minutes],
                }
            }
            
            # Create credentials and service
            credentials = service_account.Credentials.from_service_account_info(
                settings.google_calendar_credentials.to_dict(),
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            service = build('calendar', 'v3', credentials=credentials)
            
            # Create the test event
            created_event = service.events().insert(
                calendarId=settings.google_calendar_id,
                body=test_event
            ).execute()
            
            # Delete the test event immediately
            service.events().delete(
                calendarId=settings.google_calendar_id,
                eventId=created_event['id']
            ).execute()
            
            test_results = {
                'calendar_id': settings.google_calendar_id,
                'calendar_name': settings.google_calendar_name,
                'test_event_created': True,
                'test_event_deleted': True,
                'event_color_supported': True,
                'reminders_supported': True
            }
            
            logger.info(f"Calendar integration test successful for user {user_id}")
            return True, "Integration test successful", test_results
            
        except HttpError as e:
            error_details = json.loads(e.content.decode()) if e.content else {}
            return False, f"Google Calendar API error: {error_details.get('error', {}).get('message', str(e))}", None
        except Exception as e:
            logger.error(f"Error testing calendar integration for user {user_id}: {e}", exc_info=True)
            return False, f"Integration test failed: {str(e)}", None
    
    async def get_business_calendar_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get business calendar information and status
        
        Args:
            user_id: Business owner's user ID
            
        Returns:
            Calendar information dict or None
        """
        try:
            settings = await self.calendar_crud.get_calendar_settings(user_id)
            
            if not settings:
                return None
            
            return {
                'enabled': settings.google_calendar_enabled,
                'configured': settings.is_fully_configured(),
                'calendar_id': settings.google_calendar_id,
                'calendar_name': settings.google_calendar_name,
                'timezone': settings.google_calendar_timezone,
                'auto_create_events': settings.auto_create_events,
                'sync_bidirectional': settings.sync_bidirectional,
                'event_color_id': settings.event_color_id,
                'reminder_minutes': settings.reminder_minutes,
                'created_at': settings.calendar_created_at.isoformat() if settings.calendar_created_at else None,
                'last_sync': settings.calendar_last_sync.isoformat() if settings.calendar_last_sync else None
            }
            
        except Exception as e:
            logger.error(f"Error getting calendar info for user {user_id}: {e}", exc_info=True)
            return None
    
    async def disable_business_calendar(self, user_id: str) -> Tuple[bool, str]:
        """
        Disable calendar integration for a business
        
        Args:
            user_id: Business owner's user ID
            
        Returns:
            Tuple of (success, message)
        """
        try:
            settings = await self.calendar_crud.get_calendar_settings(user_id)
            
            if not settings:
                return False, "No calendar settings found"
            
            # Update settings to disable calendar
            settings.google_calendar_enabled = False
            
            success = await self.calendar_crud.update_calendar_settings(user_id, settings)
            
            if success:
                logger.info(f"Calendar disabled for user {user_id}")
                return True, "Calendar integration disabled"
            else:
                return False, "Failed to disable calendar"
                
        except Exception as e:
            logger.error(f"Error disabling calendar for user {user_id}: {e}", exc_info=True)
            return False, f"Disable failed: {str(e)}"
    
    def _parse_credentials(self, credentials_json: str) -> Dict[str, Any]:
        """Parse credentials from JSON string or base64"""
        try:
            if credentials_json.startswith('eyJ'):  # Base64 encoded
                decoded = base64.b64decode(credentials_json).decode('utf-8')
                return json.loads(decoded)
            else:  # Raw JSON
                return json.loads(credentials_json)
        except Exception as e:
            raise ValueError(f"Invalid credentials format: {e}")
    
    async def _validate_calendar_access(
        self, 
        credentials: GoogleCalendarCredentials, 
        calendar_id: str
    ) -> Tuple[bool, str]:
        """Validate access to Google Calendar"""
        try:
            # Create credentials and service
            creds = service_account.Credentials.from_service_account_info(
                credentials.to_dict(),
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            service = build('calendar', 'v3', credentials=creds)
            
            # Try to get calendar info
            calendar_info = service.calendars().get(calendarId=calendar_id).execute()
            
            # Check permissions by trying to list events
            events_result = service.events().list(
                calendarId=calendar_id,
                maxResults=1,
                singleEvents=True
            ).execute()
            
            return True, f"Access validated for calendar: {calendar_info.get('summary', calendar_id)}"
            
        except HttpError as e:
            error_details = json.loads(e.content.decode()) if e.content else {}
            error_message = error_details.get('error', {}).get('message', str(e))
            
            if e.resp.status == 404:
                return False, f"Calendar not found: {calendar_id}"
            elif e.resp.status == 403:
                return False, f"Access denied to calendar: {error_message}"
            else:
                return False, f"Calendar API error: {error_message}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    async def _get_calendar_info(
        self, 
        credentials: GoogleCalendarCredentials, 
        calendar_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed calendar information"""
        try:
            # Create credentials and service
            creds = service_account.Credentials.from_service_account_info(
                credentials.to_dict(),
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            service = build('calendar', 'v3', credentials=creds)
            
            # Get calendar info
            calendar_info = service.calendars().get(calendarId=calendar_id).execute()
            
            return {
                'id': calendar_info['id'],
                'summary': calendar_info.get('summary'),
                'description': calendar_info.get('description'),
                'timezone': calendar_info.get('timeZone'),
                'access_role': calendar_info.get('accessRole'),
                'selected': calendar_info.get('selected', False),
                'primary': calendar_info.get('primary', False)
            }
            
        except Exception as e:
            logger.error(f"Error getting calendar info: {e}")
            return None


# Utility functions for calendar management

async def setup_business_calendar_service(
    supabase_client, 
    user_id: str, 
    setup_request: CalendarSetupRequest
) -> Tuple[bool, str, Optional[CalendarSettings]]:
    """
    Utility function to setup business calendar
    
    Args:
        supabase_client: Supabase client instance
        user_id: Business owner's user ID
        setup_request: Calendar setup configuration
        
    Returns:
        Tuple of (success, message, calendar_settings)
    """
    service = CalendarManagementService(supabase_client)
    return await service.setup_business_calendar(user_id, setup_request)


async def validate_business_calendar_service(
    supabase_client,
    user_id: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Utility function to validate business calendar
    
    Args:
        supabase_client: Supabase client instance
        user_id: Business owner's user ID
        
    Returns:
        Tuple of (is_valid, message, calendar_info)
    """
    service = CalendarManagementService(supabase_client)
    return await service.validate_business_calendar(user_id)


async def test_business_calendar_integration(
    supabase_client,
    user_id: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Utility function to test calendar integration
    
    Args:
        supabase_client: Supabase client instance
        user_id: Business owner's user ID
        
    Returns:
        Tuple of (success, message, test_results)
    """
    service = CalendarManagementService(supabase_client)
    return await service.test_calendar_integration(user_id)