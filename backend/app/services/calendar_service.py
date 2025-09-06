"""
Google Calendar Integration Service
Manages calendar events synchronization for voice booking appointments
"""

import base64
import json
import logging
from datetime import datetime, timedelta, time, date
from typing import Dict, List, Optional, Any, Tuple
import pytz

from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuth2Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.core.logging import get_logger
from app.models.appointment import Appointment, AppointmentStatus
from app.models.calendar_settings import CalendarSettings, GoogleCalendarCredentials
from app.database.crud_calendar_settings import CalendarSettingsCRUD

logger = get_logger(__name__)


class GoogleCalendarService:
    """Google Calendar integration for appointment synchronization"""
    
    # Calendar scopes required
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(
        self, 
        user_id: Optional[str] = None, 
        business_calendar_id: Optional[str] = None,
        supabase_client = None
    ):
        self.user_id = user_id
        self.supabase_client = supabase_client
        self.business_settings: Optional[CalendarSettings] = None
        
        # Initialize business-specific settings
        self.is_enabled = False
        self.calendar_id = settings.google_calendar_id  # Fallback
        self.timezone = pytz.timezone(settings.google_calendar_timezone)
        self.credentials = None
        self.service = None
        
        # Load business-specific calendar settings
        if user_id and supabase_client:
            self._load_business_calendar_settings()
        else:
            # Fallback to global settings
            self.is_enabled = settings.google_calendar_enabled
            if self.is_enabled and settings.google_calendar_credentials_b64:
                self._initialize_service_from_global_settings()
    
    async def _load_business_calendar_settings(self):
        """Load business-specific calendar settings from database"""
        try:
            calendar_crud = CalendarSettingsCRUD(self.supabase_client)
            self.business_settings = await calendar_crud.get_calendar_settings(self.user_id)
            
            if self.business_settings and self.business_settings.is_fully_configured():
                self.is_enabled = self.business_settings.google_calendar_enabled
                self.calendar_id = self.business_settings.google_calendar_id
                self.timezone = pytz.timezone(self.business_settings.google_calendar_timezone)
                
                # Initialize service with business credentials
                if self.is_enabled:
                    self._initialize_service_from_business_settings()
                    
                logger.info(f"Loaded business calendar settings for user {self.user_id}: {self.calendar_id}")
            else:
                logger.warning(f"No calendar settings found for user {self.user_id}, using fallback")
                
        except Exception as e:
            logger.error(f"Error loading business calendar settings for user {self.user_id}: {e}")
    
    def _initialize_service_from_business_settings(self) -> bool:
        """Initialize service from business-specific credentials"""
        try:
            if not self.business_settings or not self.business_settings.google_calendar_credentials:
                logger.error("No business calendar credentials available")
                return False
            
            # Use business-specific credentials
            credentials_dict = self.business_settings.google_calendar_credentials.to_dict()
            
            # Create service account credentials
            self.credentials = ServiceAccountCredentials.from_service_account_info(
                credentials_dict, scopes=self.SCOPES
            )
            
            # Build Calendar API service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            
            logger.info(f"Business calendar service initialized: {self.calendar_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize business calendar service: {e}")
            self.is_enabled = False
            return False
    
    def _initialize_service_from_global_settings(self) -> bool:
        """Initialize service from global settings (fallback)"""
        try:
            if not settings.google_calendar_credentials_b64:
                logger.warning("Global calendar credentials not configured")
                return False
            
            # Decode base64 credentials
            credentials_json = base64.b64decode(
                settings.google_calendar_credentials_b64
            ).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            
            # Create service account credentials
            self.credentials = ServiceAccountCredentials.from_service_account_info(
                credentials_info, scopes=self.SCOPES
            )
            
            # Build Calendar API service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            
            logger.info(f"Global calendar service initialized: {self.calendar_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize global calendar service: {e}")
            self.is_enabled = False
            return False
    
    def _appointment_to_event(
        self, 
        appointment: Dict[str, Any], 
        client_name: str = "Client"
    ) -> Dict[str, Any]:
        """
        Convert appointment data to Google Calendar event format
        
        Args:
            appointment: Appointment data from database
            client_name: Client name for event title
            
        Returns:
            Google Calendar event dict
        """
        try:
            # Parse appointment datetime
            appt_date = appointment.get('date')
            appt_time = appointment.get('time')
            
            if isinstance(appt_date, str):
                appt_date = datetime.fromisoformat(appt_date).date()
            if isinstance(appt_time, str):
                appt_time = datetime.fromisoformat(appt_time).time()
            
            # Create datetime objects
            start_datetime = datetime.combine(appt_date, appt_time)
            start_datetime = self.timezone.localize(start_datetime)
            
            # Calculate end time (default 60 minutes)
            duration = timedelta(minutes=appointment.get('duration', 60))
            end_datetime = start_datetime + duration
            
            # Create Romanian event title
            service_name = appointment.get('service', 'Serviciu')
            event_title = f"Programare {service_name} - {client_name}"
            
            # Build event description
            description_parts = [
                f"Client: {client_name}",
                f"Serviciu: {service_name}",
                f"Durată: {appointment.get('duration', 60)} minute"
            ]
            
            if appointment.get('phone'):
                description_parts.append(f"Telefon: {appointment.get('phone')}")
            
            if appointment.get('notes'):
                description_parts.append(f"Notițe: {appointment.get('notes')}")
            
            description_parts.append(f"ID Programare: {appointment.get('id', 'N/A')}")
            
            # Create calendar event
            event = {
                'summary': event_title,
                'description': '\\n'.join(description_parts),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': settings.google_calendar_timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': settings.google_calendar_timezone,
                },
                'location': 'Salon Voice Booking',
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},        # 30 min before
                    ],
                },
                'colorId': '2',  # Green color for appointments
                'source': {
                    'title': 'Voice Booking System',
                    'url': 'https://voice-booking.salon'
                }
            }
            
            return event
            
        except Exception as e:
            logger.error(f"Error converting appointment to event: {e}")
            raise
    
    async def create_calendar_event(
        self, 
        appointment: Dict[str, Any], 
        client_name: str
    ) -> Optional[str]:
        """
        Create Google Calendar event for appointment
        
        Args:
            appointment: Appointment data
            client_name: Client name
            
        Returns:
            Google Calendar event ID or None if failed
        """
        if not self.is_enabled or not self.service:
            logger.debug("Google Calendar integration disabled")
            return None
        
        try:
            # Convert appointment to calendar event
            event = self._appointment_to_event(appointment, client_name)
            
            # Create event in Google Calendar
            created_event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event
            ).execute()
            
            event_id = created_event['id']
            event_link = created_event.get('htmlLink', '')
            
            logger.info(
                f"Created calendar event {event_id} for appointment {appointment.get('id')}"
            )
            
            return event_id
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return None
    
    async def update_calendar_event(
        self, 
        event_id: str, 
        appointment: Dict[str, Any], 
        client_name: str
    ) -> bool:
        """
        Update existing Google Calendar event
        
        Args:
            event_id: Google Calendar event ID
            appointment: Updated appointment data
            client_name: Client name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled or not self.service:
            return False
        
        try:
            # Convert appointment to calendar event
            event = self._appointment_to_event(appointment, client_name)
            
            # Update event in Google Calendar
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated calendar event {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API error updating event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating calendar event: {e}")
            return False
    
    async def delete_calendar_event(self, event_id: str) -> bool:
        """
        Delete Google Calendar event
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled or not self.service:
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted calendar event {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Calendar event {event_id} not found (already deleted?)")
                return True
            logger.error(f"Google Calendar API error deleting event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}")
            return False
    
    async def check_availability(
        self, 
        start_datetime: datetime, 
        end_datetime: datetime
    ) -> bool:
        """
        Check if time slot is available in Google Calendar
        
        Args:
            start_datetime: Start of time slot
            end_datetime: End of time slot
            
        Returns:
            True if available, False if conflicting events exist
        """
        if not self.is_enabled or not self.service:
            # If calendar not available, assume slot is free
            return True
        
        try:
            # Localize datetimes to Romanian timezone
            if start_datetime.tzinfo is None:
                start_datetime = self.timezone.localize(start_datetime)
            if end_datetime.tzinfo is None:
                end_datetime = self.timezone.localize(end_datetime)
            
            # Query events in the time range
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_datetime.isoformat(),
                timeMax=end_datetime.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Check for conflicts
            for event in events:
                # Skip declined events
                if event.get('status') == 'cancelled':
                    continue
                
                # Check if event overlaps with requested time slot
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                
                if event_start and event_end:
                    event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                    event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                    
                    # Check for overlap
                    if (start_datetime < event_end_dt and end_datetime > event_start_dt):
                        logger.info(f"Calendar conflict found: {event.get('summary', 'Unknown event')}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking calendar availability: {e}")
            # If check fails, assume slot is available to avoid blocking bookings
            return True
    
    async def get_busy_slots(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Tuple[datetime, datetime]]:
        """
        Get all busy time slots from Google Calendar
        
        Args:
            start_date: Start date to check
            end_date: End date to check
            
        Returns:
            List of (start_datetime, end_datetime) tuples for busy slots
        """
        if not self.is_enabled or not self.service:
            return []
        
        try:
            # Create datetime range
            start_datetime = self.timezone.localize(
                datetime.combine(start_date, time.min)
            )
            end_datetime = self.timezone.localize(
                datetime.combine(end_date, time.max)
            )
            
            # Query events
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_datetime.isoformat(),
                timeMax=end_datetime.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            busy_slots = []
            
            for event in events:
                # Skip cancelled events
                if event.get('status') == 'cancelled':
                    continue
                
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                
                if event_start and event_end:
                    try:
                        event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                        event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                        busy_slots.append((event_start_dt, event_end_dt))
                    except ValueError as e:
                        logger.warning(f"Could not parse event datetime: {e}")
                        continue
            
            return busy_slots
            
        except Exception as e:
            logger.error(f"Error getting busy slots: {e}")
            return []
    
    async def sync_appointment_to_calendar(
        self, 
        appointment_id: str,
        appointment_data: Dict[str, Any],
        client_name: str,
        calendar_event_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Sync appointment to Google Calendar (create or update)
        
        Args:
            appointment_id: Database appointment ID
            appointment_data: Appointment data
            client_name: Client name
            calendar_event_id: Existing calendar event ID (if updating)
            
        Returns:
            Calendar event ID or None if failed
        """
        if not self.is_enabled:
            return None
        
        try:
            if calendar_event_id:
                # Update existing event
                success = await self.update_calendar_event(
                    calendar_event_id, appointment_data, client_name
                )
                return calendar_event_id if success else None
            else:
                # Create new event
                return await self.create_calendar_event(appointment_data, client_name)
                
        except Exception as e:
            logger.error(f"Error syncing appointment {appointment_id} to calendar: {e}")
            return None


# Global calendar service instance (fallback)
calendar_service = GoogleCalendarService()


# Business-specific calendar service factory
async def get_business_calendar_service(
    user_id: str, 
    supabase_client,
    business_calendar_id: Optional[str] = None
) -> GoogleCalendarService:
    """Get calendar service for specific business with full isolation"""
    service = GoogleCalendarService(
        user_id=user_id, 
        business_calendar_id=business_calendar_id,
        supabase_client=supabase_client
    )
    # Load settings is called in __init__ but is async, so we need to ensure it completes
    if user_id and supabase_client:
        await service._load_business_calendar_settings()
    return service


# Convenience functions for voice functions integration with complete business isolation
async def create_appointment_calendar_event(
    appointment: Dict[str, Any], 
    client_name: str,
    user_id: Optional[str] = None,
    supabase_client = None
) -> Optional[str]:
    """Create calendar event for new appointment with complete business isolation"""
    if user_id and supabase_client:
        business_calendar = await get_business_calendar_service(user_id, supabase_client)
        return await business_calendar.create_calendar_event(appointment, client_name)
    else:
        # Fallback to global service
        return await calendar_service.create_calendar_event(appointment, client_name)


async def check_calendar_availability(
    start_datetime: datetime, 
    duration_minutes: int = 60,
    user_id: Optional[str] = None,
    supabase_client = None
) -> bool:
    """Check if time slot is available with complete business isolation"""
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    
    if user_id and supabase_client:
        business_calendar = await get_business_calendar_service(user_id, supabase_client)
        return await business_calendar.check_availability(start_datetime, end_datetime)
    else:
        # Fallback to global service
        return await calendar_service.check_availability(start_datetime, end_datetime)


async def get_calendar_busy_times(
    start_date: date, 
    end_date: date,
    user_id: Optional[str] = None,
    supabase_client = None
) -> List[Tuple[datetime, datetime]]:
    """Get busy time slots from calendar with complete business isolation"""
    if user_id and supabase_client:
        business_calendar = await get_business_calendar_service(user_id, supabase_client)
        return await business_calendar.get_busy_slots(start_date, end_date)
    else:
        # Fallback to global service  
        return await calendar_service.get_busy_slots(start_date, end_date)