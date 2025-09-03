"""
User-isolated CRUD operations for appointments
Uses user JWT for RLS enforcement - ensures data isolation per user/salon
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import uuid4

from app.models.appointment import (
    Appointment as AppointmentModel, AppointmentCreate, AppointmentUpdate, 
    AppointmentStatus, AppointmentType, AppointmentPriority
)
from app.core.logging import get_logger
from app.core.supabase_user import create_supabase_for_user, extract_user_id_from_jwt

logger = get_logger(__name__)


class UserAppointmentCRUD:
    """User-isolated CRUD operations for appointments with RLS enforcement"""
    
    def __init__(self, jwt_token: str, user_info: Dict[str, Any]):
        """
        Initialize with user JWT for RLS enforcement
        
        Args:
            jwt_token: User's JWT access token
            user_info: User info from require_user dependency
        """
        self.client = create_supabase_for_user(jwt_token)
        self.user_info = user_info
        self.user_id = extract_user_id_from_jwt(user_info)
        self.table = "appointments"
    
    async def get_appointments(
        self,
        appointment_date: Optional[date] = None,
        status: Optional[AppointmentStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[AppointmentModel], int]:
        """
        Get appointments for current user with optional filtering
        RLS automatically filters to user's data only
        """
        try:
            # RLS will automatically filter by created_by = auth.uid()
            query = self.client.table(self.table).select("*")
            
            # Apply filters
            if appointment_date:
                query = query.eq("appointment_date", appointment_date.isoformat())
            
            if status:
                query = query.eq("status", status.value)
            
            # Count total for pagination (also RLS filtered)
            count_query = self.client.table(self.table).select("id", count="exact")
            if appointment_date:
                count_query = count_query.eq("appointment_date", appointment_date.isoformat())
            if status:
                count_query = count_query.eq("status", status.value)
            
            count_response = count_query.execute()
            total = count_response.count or 0
            
            # Get paginated results
            response = query.order("appointment_date", desc=False)\
                          .order("appointment_time", desc=False)\
                          .range(offset, offset + limit - 1)\
                          .execute()
            
            appointments = []
            for row in response.data:
                # Convert database row to Pydantic model
                appointment_data = {
                    "id": row["id"],
                    "client_id": row["client_id"],
                    "service_id": row["service_id"],
                    "appointment_date": datetime.fromisoformat(
                        row["appointment_date"] + "T00:00:00"
                    ).date() if row.get("appointment_date") else None,
                    "appointment_time": datetime.strptime(
                        row["appointment_time"], "%H:%M:%S"
                    ).time() if row.get("appointment_time") else None,
                    "duration": row.get("duration"),
                    "status": AppointmentStatus(row["status"]),
                    "type": AppointmentType(row.get("type", "regular")),
                    "priority": AppointmentPriority(row.get("priority", "normal")),
                    "notes": row.get("notes"),
                    "price": row.get("price"),
                    "created_by": row.get("created_by"),
                    "created_at": datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                    "updated_at": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
                }
                appointments.append(AppointmentModel(**appointment_data))
            
            logger.info(f"Retrieved {len(appointments)} appointments for user {self.user_info.get('email')}",
                       extra={"total": total, "date": appointment_date, "status": status, "user_id": self.user_id})
            
            return appointments, total
            
        except Exception as e:
            logger.error(f"Failed to retrieve appointments for user {self.user_id}: {e}", exc_info=True)
            raise

    async def get_appointment_by_id(self, appointment_id: str) -> Optional[AppointmentModel]:
        """
        Get appointment by ID for current user
        RLS automatically ensures user can only access their own appointments
        """
        try:
            response = self.client.table(self.table)\
                                 .select("*")\
                                 .eq("id", appointment_id)\
                                 .single()\
                                 .execute()
            
            if not response.data:
                return None
            
            row = response.data
            
            appointment_data = {
                "id": row["id"],
                "client_id": row["client_id"],
                "service_id": row["service_id"],
                "appointment_date": datetime.fromisoformat(
                    row["appointment_date"] + "T00:00:00"
                ).date() if row.get("appointment_date") else None,
                "appointment_time": datetime.strptime(
                    row["appointment_time"], "%H:%M:%S"
                ).time() if row.get("appointment_time") else None,
                "duration": row.get("duration"),
                "status": AppointmentStatus(row["status"]),
                "type": AppointmentType(row.get("type", "regular")),
                "priority": AppointmentPriority(row.get("priority", "normal")),
                "notes": row.get("notes"),
                "price": row.get("price"),
                "created_by": row.get("created_by"),
                "created_at": datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                "updated_at": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            }
            
            logger.debug(f"Retrieved appointment {appointment_id} for user {self.user_id}")
            return AppointmentModel(**appointment_data)
            
        except Exception as e:
            logger.error(f"Failed to retrieve appointment {appointment_id} for user {self.user_id}: {e}", exc_info=True)
            raise

    async def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentModel:
        """
        Create new appointment for current user
        created_by is automatically set by trigger
        """
        try:
            # Prepare data for database
            db_data = {
                "id": str(uuid4()),
                "client_id": appointment_data.client_id,
                "service_id": appointment_data.service_id,
                "appointment_date": appointment_data.date.isoformat() if appointment_data.date else None,
                "appointment_time": appointment_data.time.strftime("%H:%M:%S") if appointment_data.time else None,
                "duration": appointment_data.duration,
                "status": appointment_data.status.value,
                "type": appointment_data.type.value,
                "priority": appointment_data.priority.value,
                "notes": appointment_data.notes,
                # created_by will be set by trigger to auth.uid()
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            response = self.client.table(self.table).insert(db_data).execute()
            
            if not response.data:
                raise Exception("Failed to create appointment")
            
            # Return created appointment
            created_appointment = await self.get_appointment_by_id(response.data[0]["id"])
            
            logger.info(f"Created appointment {created_appointment.id} for user {self.user_info.get('email')}",
                       extra={"appointment_id": created_appointment.id, "user_id": self.user_id})
            
            return created_appointment
            
        except Exception as e:
            logger.error(f"Failed to create appointment for user {self.user_id}: {e}", exc_info=True)
            raise

    async def update_appointment(self, appointment_id: str, appointment_data: AppointmentUpdate) -> Optional[AppointmentModel]:
        """
        Update appointment for current user
        RLS automatically ensures user can only update their own appointments
        """
        try:
            # Prepare update data (only include non-None values)
            update_data = {"updated_at": datetime.now().isoformat()}
            
            if appointment_data.client_id is not None:
                update_data["client_id"] = appointment_data.client_id
            if appointment_data.service_id is not None:
                update_data["service_id"] = appointment_data.service_id
            if appointment_data.date is not None:
                update_data["appointment_date"] = appointment_data.date.isoformat()
            if appointment_data.time is not None:
                update_data["appointment_time"] = appointment_data.time.strftime("%H:%M:%S")
            if appointment_data.duration is not None:
                update_data["duration"] = appointment_data.duration
            if appointment_data.status is not None:
                update_data["status"] = appointment_data.status.value
            if appointment_data.priority is not None:
                update_data["priority"] = appointment_data.priority.value
            if appointment_data.notes is not None:
                update_data["notes"] = appointment_data.notes
            
            response = self.client.table(self.table)\
                                 .update(update_data)\
                                 .eq("id", appointment_id)\
                                 .execute()
            
            if not response.data:
                return None  # Appointment not found or not owned by user
            
            # Return updated appointment
            updated_appointment = await self.get_appointment_by_id(appointment_id)
            
            logger.info(f"Updated appointment {appointment_id} for user {self.user_info.get('email')}",
                       extra={"appointment_id": appointment_id, "user_id": self.user_id})
            
            return updated_appointment
            
        except Exception as e:
            logger.error(f"Failed to update appointment {appointment_id} for user {self.user_id}: {e}", exc_info=True)
            raise

    async def delete_appointment(self, appointment_id: str) -> bool:
        """
        Delete appointment for current user
        RLS automatically ensures user can only delete their own appointments
        """
        try:
            response = self.client.table(self.table)\
                                 .delete()\
                                 .eq("id", appointment_id)\
                                 .execute()
            
            success = bool(response.data)
            
            if success:
                logger.info(f"Deleted appointment {appointment_id} for user {self.user_info.get('email')}",
                           extra={"appointment_id": appointment_id, "user_id": self.user_id})
            else:
                logger.warning(f"Appointment {appointment_id} not found or not owned by user {self.user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete appointment {appointment_id} for user {self.user_id}: {e}", exc_info=True)
            raise