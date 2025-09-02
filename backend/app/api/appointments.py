from datetime import datetime, date, time
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query

from app.models.appointment import (
    Appointment, AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    AppointmentListResponse, AppointmentStatus, AppointmentType, AppointmentPriority
)
from app.core.logging import get_logger
from app.database.crud_appointments import AppointmentCRUD
from app.database import get_database

router = APIRouter()
logger = get_logger(__name__)


async def get_appointment_crud(db = Depends(get_database)) -> AppointmentCRUD:
    """Dependency injection for AppointmentCRUD"""
    return AppointmentCRUD(db.get_client())



@router.get("/appointments", response_model=AppointmentListResponse)
async def get_appointments(
    date_filter: Optional[date] = Query(None, alias="date", description="Filter by date"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    appointment_crud: AppointmentCRUD = Depends(get_appointment_crud)
):
    """Get appointments with optional filtering"""
    try:
        # Get appointments from database using CRUD
        appointment_objects, total = await appointment_crud.get_appointments(
            date_filter=date_filter,
            status=status,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Retrieved {len(appointment_objects)} appointments from database", 
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
async def create_appointment(
    appointment_data: AppointmentCreate,
    appointment_crud: AppointmentCRUD = Depends(get_appointment_crud)
):
    """Create a new appointment"""
    try:
        appointment_obj = await appointment_crud.create_appointment(appointment_data)
        
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
async def update_appointment(
    appointment_id: str, 
    appointment_data: AppointmentUpdate,
    appointment_crud: AppointmentCRUD = Depends(get_appointment_crud)
):
    """Update an existing appointment"""
    try:
        appointment_obj = await appointment_crud.update_appointment(appointment_id, appointment_data)
        
        update_data = appointment_data.model_dump(exclude_unset=True)
        logger.info(f"Updated appointment {appointment_id}",
                   extra={"appointment_id": appointment_id, "updated_fields": list(update_data.keys())})
        
        return AppointmentResponse(
            success=True,
            data=appointment_obj,
            message="Appointment updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to update appointment {appointment_id}: {e}", exc_info=True)
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Appointment not found")
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@router.delete("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def delete_appointment(
    appointment_id: str,
    appointment_crud: AppointmentCRUD = Depends(get_appointment_crud)
):
    """Delete an appointment"""
    try:
        deleted = await appointment_crud.delete_appointment(appointment_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        logger.info(f"Deleted appointment {appointment_id}",
                   extra={"appointment_id": appointment_id})
        
        return AppointmentResponse(
            success=True,
            message="Appointment deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to delete appointment {appointment_id}: {e}", exc_info=True)
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Appointment not found")
        raise HTTPException(status_code=500, detail="Failed to delete appointment")