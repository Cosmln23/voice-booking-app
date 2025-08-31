from datetime import datetime, time
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    STAFF = "staff"
    OWNER = "owner"


class AgentStatus(str, Enum):
    """Voice agent status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROCESSING = "processing"


class ActivityLogType(str, Enum):
    """Activity log type enumeration"""
    INCOMING_CALL = "incoming_call"
    BOOKING_SUCCESS = "booking_success"
    BOOKING_FAILED = "booking_failed"
    SYSTEM_STATUS = "system_status"


class WorkingHours(BaseModel):
    """Working hours model"""
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    is_closed: bool = False


class ActivityLog(BaseModel):
    """Activity log entry model"""
    timestamp: datetime
    type: ActivityLogType
    message: str
    client_info: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class NotificationSettings(BaseModel):
    """Notification preferences model"""
    email_notifications: bool = True
    sms_notifications: bool = False
    appointment_reminders: bool = True
    new_booking_alerts: bool = True
    system_updates: bool = True


class AgentConfiguration(BaseModel):
    """Voice agent configuration model"""
    enabled: bool = False
    model: str = "gpt-4o-realtime-preview"
    language: str = "ro-RO"
    voice: str = "nova"
    auto_booking: bool = False
    confirmation_required: bool = True


class BusinessSettings(BaseModel):
    """Business settings model"""
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    working_hours: list[WorkingHours] = []
    notifications: NotificationSettings = NotificationSettings()
    agent_config: AgentConfiguration = AgentConfiguration()
    timezone: str = "Europe/Bucharest"


class AgentStatusInfo(BaseModel):
    """Voice agent status information"""
    status: AgentStatus = AgentStatus.INACTIVE
    last_activity: Optional[datetime] = None
    total_calls: int = 0
    success_rate: float = 0.0
    activity_log: list[ActivityLog] = []


class UserBase(BaseModel):
    """Base user model"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.STAFF


class UserCreate(UserBase):
    """Create user model"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Update user model - all fields optional"""
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None


class User(UserBase):
    """Full user model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """API response wrapper for users"""
    success: bool = True
    data: Optional[User] = None
    message: Optional[str] = None