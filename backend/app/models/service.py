from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class ServiceCategory(str, Enum):
    """Service category enumeration"""
    INDIVIDUAL = "individual"
    PACKAGE = "package"


class ServiceStatus(str, Enum):
    """Service availability status"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ServiceBase(BaseModel):
    """Base service model"""
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    currency: str = Field(default="RON")
    duration: str = Field(..., pattern=r'^\d+min$')  # e.g., "45min"
    category: ServiceCategory = ServiceCategory.INDIVIDUAL
    description: Optional[str] = Field(None, max_length=500)
    status: ServiceStatus = ServiceStatus.ACTIVE


class ServiceCreate(ServiceBase):
    """Create service model"""
    pass


class ServiceUpdate(BaseModel):
    """Update service model - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    duration: Optional[str] = Field(None, pattern=r'^\d+min$')
    category: Optional[ServiceCategory] = None
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[ServiceStatus] = None


class Service(ServiceBase):
    """Full service model with database fields"""
    id: str
    created_by: Optional[str] = None  # User UUID who created this service
    created_at: datetime
    updated_at: datetime
    popularity_score: float = 0.0  # For analytics
    
    class Config:
        from_attributes = True


class ServiceResponse(BaseModel):
    """API response wrapper for services"""
    success: bool = True
    data: Optional[Service] = None
    message: Optional[str] = None


class ServiceListResponse(BaseModel):
    """API response wrapper for service lists"""
    success: bool = True
    data: list[Service] = []
    total: int = 0
    message: Optional[str] = None


class ServiceStats(BaseModel):
    """Service statistics model"""
    total_services: int = 0
    active_services: int = 0
    most_popular: Optional[str] = None
    average_price: float = 0.0