from datetime import datetime, date, time
from typing import Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status enumeration"""
    CONFIRMED = "confirmed"
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no-show"


class AppointmentType(str, Enum):
    """Appointment creation type"""
    VOICE = "voice"
    MANUAL = "manual"


class AppointmentPriority(str, Enum):
    """Appointment priority for pending appointments"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"


class AppointmentBase(BaseModel):
    """Base appointment model"""
    client_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    service: str = Field(..., min_length=1, max_length=100)
    date: date
    time: time
    duration: str = Field(..., pattern=r'^\d+min$')  # e.g., "45min"
    status: AppointmentStatus = AppointmentStatus.PENDING
    type: AppointmentType = AppointmentType.MANUAL
    priority: AppointmentPriority = AppointmentPriority.NORMAL
    notes: Optional[str] = Field(None, max_length=500)


class AppointmentCreate(AppointmentBase):
    """Create appointment model"""
    pass


class AppointmentUpdate(BaseModel):
    """Update appointment model - all fields optional"""
    client_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    service: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[date] = None
    time: Optional[time] = None
    duration: Optional[str] = Field(None, pattern=r'^\d+min$')
    status: Optional[AppointmentStatus] = None
    priority: Optional[AppointmentPriority] = None
    notes: Optional[str] = Field(None, max_length=500)


class Appointment(AppointmentBase):
    """Full appointment model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime
    price: Optional[str] = None  # Only for completed appointments
    
    class Config:
        from_attributes = True


class AppointmentResponse(BaseModel):
    """API response wrapper for appointments"""
    success: bool = True
    data: Optional[Appointment] = None
    message: Optional[str] = None


class AppointmentListResponse(BaseModel):
    """API response wrapper for appointment lists"""
    success: bool = True
    data: list[Appointment] = []
    total: int = 0
    message: Optional[str] = None