from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from supabase import Client

from app.models.appointment import (
    Appointment, AppointmentCreate, AppointmentUpdate, 
    AppointmentStatus, AppointmentType, AppointmentPriority
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AppointmentCRUD:
    """CRUD operations for appointments"""
    
    def __init__(self, client: Client):
        self.client = client
        self.table = "appointments"
    
    async def get_appointments(
        self, 
        date_filter: Optional[date] = None,
        status: Optional[AppointmentStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Appointment], int]:
        """Get appointments with optional filtering"""
        try:
            query = self.client.table(self.table).select("*")
            
            # Apply filters
            if date_filter:
                query = query.eq("appointment_date", date_filter.isoformat())
            
            if status:
                query = query.eq("status", status.value)
            
            # Count total for pagination
            count_query = self.client.table(self.table).select("id", count="exact")
            if date_filter:
                count_query = count_query.eq("appointment_date", date_filter.isoformat())
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
                    "client_name": row["client_name"],
                    "phone": row["phone"],
                    "service": row["service_name"],
                    "date": datetime.strptime(row["appointment_date"], "%Y-%m-%d").date(),
                    "time": datetime.strptime(row["appointment_time"], "%H:%M:%S").time(),
                    "duration": row["duration"],
                    "status": AppointmentStatus(row["status"]),
                    "type": AppointmentType(row["type"]),
                    "priority": AppointmentPriority(row["priority"]),
                    "notes": row.get("notes"),
                    "price": row.get("price"),
                    "created_at": datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                    "updated_at": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
                }
                appointments.append(Appointment(**appointment_data))
            
            logger.info(f"Retrieved {len(appointments)} appointments", 
                       extra={"total": total, "filters": {"date": date_filter, "status": status}})
            
            return appointments, total
            
        except Exception as e:
            logger.error(f"Failed to retrieve appointments: {e}", exc_info=True)
            raise
    
    async def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """Create a new appointment"""
        try:
            # Convert Pydantic model to database format
            db_data = {
                "id": str(uuid4()),
                "client_name": appointment_data.client_name,
                "phone": appointment_data.phone,
                "service_name": appointment_data.service,
                "appointment_date": appointment_data.date.isoformat(),
                "appointment_time": appointment_data.time.isoformat(),
                "duration": appointment_data.duration,
                "status": appointment_data.status.value,
                "type": appointment_data.type.value,
                "priority": appointment_data.priority.value,
                "notes": appointment_data.notes,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Check for existing client and link if found
            client_response = self.client.table("clients")\
                                        .select("id")\
                                        .eq("phone", appointment_data.phone)\
                                        .limit(1)\
                                        .execute()
            
            if client_response.data:
                db_data["client_id"] = client_response.data[0]["id"]
            
            # Check for existing service and link if found
            service_response = self.client.table("services")\
                                         .select("id")\
                                         .eq("name", appointment_data.service)\
                                         .limit(1)\
                                         .execute()
            
            if service_response.data:
                db_data["service_id"] = service_response.data[0]["id"]
            
            # Insert appointment
            response = self.client.table(self.table).insert(db_data).execute()
            
            if not response.data:
                raise Exception("Failed to create appointment")
            
            # Convert back to Pydantic model
            row = response.data[0]
            appointment = Appointment(
                id=row["id"],
                client_name=row["client_name"],
                phone=row["phone"],
                service=row["service_name"],
                date=datetime.strptime(row["appointment_date"], "%Y-%m-%d").date(),
                time=datetime.strptime(row["appointment_time"], "%H:%M:%S").time(),
                duration=row["duration"],
                status=AppointmentStatus(row["status"]),
                type=AppointmentType(row["type"]),
                priority=AppointmentPriority(row["priority"]),
                notes=row.get("notes"),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            
            logger.info(f"Created appointment {appointment.id} for {appointment.client_name}",
                       extra={"appointment_id": appointment.id, "client": appointment.client_name})
            
            return appointment
            
        except Exception as e:
            logger.error(f"Failed to create appointment: {e}", exc_info=True)
            raise
    
    async def update_appointment(self, appointment_id: str, appointment_data: AppointmentUpdate) -> Appointment:
        """Update an existing appointment"""
        try:
            # Convert update data to database format
            update_data = {}
            update_fields = appointment_data.model_dump(exclude_unset=True)
            
            for field, value in update_fields.items():
                if field == "service":
                    update_data["service_name"] = value
                elif field == "date":
                    update_data["appointment_date"] = value.isoformat()
                elif field == "time":
                    update_data["appointment_time"] = value.isoformat()
                elif field in ["status", "type", "priority"]:
                    update_data[field] = value.value if hasattr(value, 'value') else value
                else:
                    update_data[field] = value
            
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Update appointment
            response = self.client.table(self.table)\
                                 .update(update_data)\
                                 .eq("id", appointment_id)\
                                 .execute()
            
            if not response.data:
                raise Exception("Appointment not found")
            
            # Convert back to Pydantic model
            row = response.data[0]
            appointment = Appointment(
                id=row["id"],
                client_name=row["client_name"],
                phone=row["phone"],
                service=row["service_name"],
                date=datetime.strptime(row["appointment_date"], "%Y-%m-%d").date(),
                time=datetime.strptime(row["appointment_time"], "%H:%M:%S").time(),
                duration=row["duration"],
                status=AppointmentStatus(row["status"]),
                type=AppointmentType(row["type"]),
                priority=AppointmentPriority(row["priority"]),
                notes=row.get("notes"),
                price=row.get("price"),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            
            logger.info(f"Updated appointment {appointment_id}",
                       extra={"appointment_id": appointment_id, "updated_fields": list(update_fields.keys())})
            
            return appointment
            
        except Exception as e:
            logger.error(f"Failed to update appointment {appointment_id}: {e}", exc_info=True)
            raise
    
    async def delete_appointment(self, appointment_id: str) -> bool:
        """Delete an appointment"""
        try:
            response = self.client.table(self.table)\
                                 .delete()\
                                 .eq("id", appointment_id)\
                                 .execute()
            
            if not response.data:
                raise Exception("Appointment not found")
            
            logger.info(f"Deleted appointment {appointment_id}",
                       extra={"appointment_id": appointment_id})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete appointment {appointment_id}: {e}", exc_info=True)
            raise