from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class ClientStatus(str, Enum):
    """Client status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ClientBase(BaseModel):
    """Base client model"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    notes: Optional[str] = Field(None, max_length=500)
    status: ClientStatus = ClientStatus.ACTIVE


class ClientCreate(ClientBase):
    """Create client model"""
    pass


class ClientUpdate(BaseModel):
    """Update client model - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[ClientStatus] = None


class Client(ClientBase):
    """Full client model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime
    avatar: Optional[str] = None  # URL or initials
    total_appointments: int = 0
    last_appointment: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClientResponse(BaseModel):
    """API response wrapper for clients"""
    success: bool = True
    data: Optional[Client] = None
    message: Optional[str] = None


class ClientListResponse(BaseModel):
    """API response wrapper for client lists"""
    success: bool = True
    data: list[Client] = []
    total: int = 0
    message: Optional[str] = None


class ClientStats(BaseModel):
    """Client statistics model"""
    total_clients: int = 0
    new_this_month: int = 0
    active_clients: int = 0
    inactive_clients: int = 0