"""
Calendar Synchronization CRUD Operations
Handles bidirectional sync between database appointments and Google Calendar events
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

from app.core.logging import get_logger
from app.services.calendar_service import calendar_service
from app.database.user_crud_appointments import UserAppointmentCRUD
from app.database.user_crud_clients import UserClientCRUD
from app.models.appointment import AppointmentStatus

logger = get_logger(__name__)


class CalendarSyncService:
    """Manages bidirectional sync between database and Google Calendar"""
    
    def __init__(self, supabase_client, user_id: str):
        self.supabase_client = supabase_client
        self.user_id = user_id
        self.appointment_crud = UserAppointmentCRUD(supabase_client, user_id)
        self.client_crud = UserClientCRUD(supabase_client, {"user_id": user_id})
    
    async def sync_appointment_to_calendar(
        self, 
        appointment_id: str,
        action: str = "create"  # create, update, delete
    ) -> Optional[str]:
        """
        Sync single appointment to Google Calendar
        
        Args:
            appointment_id: Database appointment ID
            action: Sync action (create, update, delete)
            
        Returns:
            Google Calendar event ID or None
        """
        try:
            if action == "delete":
                # Handle deletion - need to get calendar_event_id first
                # TODO: Implement calendar_event_id storage in database
                return await self._delete_calendar_event_by_appointment(appointment_id)
            
            # Get appointment details
            appointment = await self.appointment_crud.get_appointment_by_id(appointment_id)
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return None
            
            # Get client name
            client_name = appointment.client_name or "Client"
            
            # Prepare appointment data for calendar
            appointment_dict = {
                "id": str(appointment.id),
                "date": appointment.date,
                "time": appointment.time,
                "service": appointment.service,
                "duration": int(appointment.duration.replace("min", "")) if "min" in appointment.duration else 60,
                "phone": appointment.phone,
                "notes": appointment.notes
            }
            
            if action == "create":
                event_id = await calendar_service.create_calendar_event(
                    appointment_dict, client_name
                )
                
                if event_id:
                    # TODO: Store event_id in database appointment record
                    logger.info(f"Synced appointment {appointment_id} → calendar event {event_id}")
                
                return event_id
                
            elif action == "update":
                # TODO: Get existing calendar_event_id from database
                # For now, create new event (will be improved with database schema update)
                event_id = await calendar_service.create_calendar_event(
                    appointment_dict, client_name
                )
                
                return event_id
            
        except Exception as e:
            logger.error(f"Error syncing appointment {appointment_id} to calendar: {e}")
            return None
    
    async def sync_calendar_to_database(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, int]:
        """
        Sync Google Calendar events to database appointments
        WARNING: This is complex and requires careful conflict resolution
        
        Args:
            start_date: Start date range
            end_date: End date range
            
        Returns:
            Dict with sync statistics
        """
        try:
            # Get busy slots from calendar
            busy_slots = await calendar_service.get_busy_slots(
                start_date.date(), end_date.date()
            )
            
            # Get existing appointments from database
            appointments, _ = await self.appointment_crud.get_appointments(
                appointment_date=None,  # Get all in range
                status=None,
                limit=1000,
                offset=0
            )
            
            created = 0
            updated = 0
            conflicts = 0
            
            # This is a complex sync process that would require:
            # 1. Matching calendar events to database appointments
            # 2. Identifying external calendar events (not created by voice system)
            # 3. Conflict resolution strategies
            # 4. Two-way sync state management
            
            # For initial implementation, we focus on voice→calendar sync
            # Full bidirectional sync would be a Phase 2 feature
            
            logger.info(f"Calendar→Database sync: {len(busy_slots)} calendar events, {len(appointments)} db appointments")
            
            return {
                "created": created,
                "updated": updated,
                "conflicts": conflicts,
                "calendar_events": len(busy_slots),
                "db_appointments": len(appointments)
            }
            
        except Exception as e:
            logger.error(f"Error syncing calendar to database: {e}")
            return {"error": str(e)}
    
    async def _delete_calendar_event_by_appointment(self, appointment_id: str) -> bool:
        """Delete calendar event associated with appointment"""
        try:
            # TODO: Get calendar_event_id from database
            # For now, we can't delete calendar events without storing the event ID
            logger.warning(f"Cannot delete calendar event for appointment {appointment_id} - event ID not stored")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting calendar event for appointment {appointment_id}: {e}")
            return False
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status between database and calendar"""
        try:
            # Get recent appointments
            appointments, _ = await self.appointment_crud.get_appointments(
                appointment_date=None,
                status=AppointmentStatus.CONFIRMED,
                limit=50,
                offset=0
            )
            
            # Get calendar busy slots for next 30 days
            from datetime import date, timedelta
            start_date = date.today()
            end_date = start_date + timedelta(days=30)
            
            busy_slots = await calendar_service.get_busy_slots(start_date, end_date)
            
            return {
                "calendar_enabled": calendar_service.is_enabled,
                "db_appointments": len(appointments),
                "calendar_events": len(busy_slots),
                "sync_direction": "voice→calendar (one-way)",
                "last_sync": datetime.now().isoformat(),
                "status": "active" if calendar_service.is_enabled else "disabled"
            }
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {"error": str(e)}


# Convenience functions for voice integration
async def sync_voice_appointment_to_calendar(
    appointment_id: str,
    supabase_client,
    user_id: str
) -> Optional[str]:
    """Sync voice appointment to Google Calendar"""
    sync_service = CalendarSyncService(supabase_client, user_id)
    return await sync_service.sync_appointment_to_calendar(appointment_id, "create")


async def get_calendar_sync_status(supabase_client, user_id: str) -> Dict[str, Any]:
    """Get calendar synchronization status"""
    sync_service = CalendarSyncService(supabase_client, user_id)
    return await sync_service.get_sync_status()