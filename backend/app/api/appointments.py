from datetime import datetime, date, time
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from uuid import uuid4

from app.models.appointment import (
    Appointment, AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    AppointmentListResponse, AppointmentStatus, AppointmentType, AppointmentPriority
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Mock data
MOCK_APPOINTMENTS = [
    {
        "id": str(uuid4()),
        "client_name": "Alexandru Popescu",
        "phone": "+40721123456",
        "service": "Tunsoare Clasică",
        "date": date.today(),
        "time": time(9, 0),
        "duration": "45min",
        "status": AppointmentStatus.CONFIRMED,
        "type": AppointmentType.VOICE,
        "priority": AppointmentPriority.NORMAL,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "notes": "Client preferat, punctual",
    },
    {
        "id": str(uuid4()),
        "client_name": "Maria Ionescu",
        "phone": "+40722234567", 
        "service": "Barbă Completă",
        "date": date.today(),
        "time": time(11, 30),
        "duration": "30min",
        "status": AppointmentStatus.IN_PROGRESS,
        "type": AppointmentType.MANUAL,
        "priority": AppointmentPriority.HIGH,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "id": str(uuid4()),
        "client_name": "Ion Georgescu",
        "phone": "+40723345678",
        "service": "Pachet Completă",
        "date": date.today(),
        "time": time(14, 0),
        "duration": "90min",
        "status": AppointmentStatus.COMPLETED,
        "type": AppointmentType.VOICE,
        "priority": AppointmentPriority.NORMAL,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "price": "120 RON",
    },
    {
        "id": str(uuid4()),
        "client_name": "Elena Vasile",
        "phone": "+40724456789",
        "service": "Tunsoare Clasică",
        "date": date.today(),
        "time": time(16, 30),
        "duration": "45min",
        "status": AppointmentStatus.PENDING,
        "type": AppointmentType.VOICE,
        "priority": AppointmentPriority.URGENT,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "notes": "Programare de urgență",
    }
]


@router.get("/appointments", response_model=AppointmentListResponse)
async def get_appointments(
    date_filter: Optional[date] = Query(None, alias="date", description="Filter by date"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get appointments with optional filtering"""
    try:
        appointments = MOCK_APPOINTMENTS.copy()
        
        # Apply filters
        if date_filter:
            appointments = [apt for apt in appointments if apt["date"] == date_filter]
            
        if status:
            appointments = [apt for apt in appointments if apt["status"] == status]
        
        # Apply pagination
        total = len(appointments)
        appointments = appointments[offset:offset + limit]
        
        # Convert to Pydantic models
        appointment_objects = [Appointment(**apt) for apt in appointments]
        
        logger.info(f"Retrieved {len(appointment_objects)} appointments", 
                   extra={"total": total, "filters": {"date": date_filter, "status": status}})
        
        return AppointmentListResponse(
            success=True,
            data=appointment_objects,
            total=total,
            message=f"Retrieved {len(appointment_objects)} appointments"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve appointments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve appointments")


@router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(appointment_data: AppointmentCreate):
    """Create a new appointment"""
    try:
        # Create new appointment
        new_appointment = {
            "id": str(uuid4()),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            **appointment_data.model_dump()
        }
        
        # Add to mock data
        MOCK_APPOINTMENTS.append(new_appointment)
        
        appointment_obj = Appointment(**new_appointment)
        
        logger.info(f"Created appointment {appointment_obj.id} for {appointment_obj.client_name}",
                   extra={"appointment_id": appointment_obj.id, "client": appointment_obj.client_name})
        
        return AppointmentResponse(
            success=True,
            data=appointment_obj,
            message="Appointment created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create appointment")


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: str, appointment_data: AppointmentUpdate):
    """Update an existing appointment"""
    try:
        # Find appointment
        appointment = next((apt for apt in MOCK_APPOINTMENTS if apt["id"] == appointment_id), None)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Update fields
        update_data = appointment_data.model_dump(exclude_unset=True)
        appointment.update(update_data)
        appointment["updated_at"] = datetime.now()
        
        appointment_obj = Appointment(**appointment)
        
        logger.info(f"Updated appointment {appointment_id}",
                   extra={"appointment_id": appointment_id, "updated_fields": list(update_data.keys())})
        
        return AppointmentResponse(
            success=True,
            data=appointment_obj,
            message="Appointment updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update appointment {appointment_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@router.delete("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def delete_appointment(appointment_id: str):
    """Delete an appointment"""
    try:
        # Find and remove appointment
        global MOCK_APPOINTMENTS
        appointment = next((apt for apt in MOCK_APPOINTMENTS if apt["id"] == appointment_id), None)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        MOCK_APPOINTMENTS = [apt for apt in MOCK_APPOINTMENTS if apt["id"] != appointment_id]
        
        logger.info(f"Deleted appointment {appointment_id}",
                   extra={"appointment_id": appointment_id, "client": appointment["client_name"]})
        
        return AppointmentResponse(
            success=True,
            message="Appointment deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete appointment {appointment_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete appointment")