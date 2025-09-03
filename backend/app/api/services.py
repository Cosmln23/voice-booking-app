from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from uuid import uuid4

from app.models.service import (
    Service, ServiceCreate, ServiceUpdate, ServiceResponse,
    ServiceListResponse, ServiceStats, ServiceCategory, ServiceStatus
)
from app.core.logging import get_logger
from app.core.auth import require_user
from app.database.crud_services import ServiceCRUD
from app.database import get_database

router = APIRouter()
logger = get_logger(__name__)


async def get_service_crud(db = Depends(get_database)) -> ServiceCRUD:
    """Dependency injection for ServiceCRUD"""
    return ServiceCRUD(db.get_client())

# Mock data
MOCK_SERVICES = [
    {
        "id": str(uuid4()),
        "name": "Tunsoare Clasică",
        "price": 35.0,
        "currency": "RON",
        "duration": "45min",
        "category": ServiceCategory.INDIVIDUAL,
        "description": "Tunsoare clasică pentru bărbați cu foarfecă și mașină",
        "status": ServiceStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "popularity_score": 85.5
    },
    {
        "id": str(uuid4()),
        "name": "Barbă Completă",
        "price": 25.0,
        "currency": "RON",
        "duration": "30min",
        "category": ServiceCategory.INDIVIDUAL,
        "description": "Aranjare și modelarea completă a bărbii",
        "status": ServiceStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "popularity_score": 72.3
    },
    {
        "id": str(uuid4()),
        "name": "Pachet Completă",
        "price": 120.0,
        "currency": "RON",
        "duration": "90min",
        "category": ServiceCategory.PACKAGE,
        "description": "Tunsoare + Barbă + Spălat + Styling complet",
        "status": ServiceStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "popularity_score": 95.2
    },
    {
        "id": str(uuid4()),
        "name": "Pachet Premium",
        "price": 150.0,
        "currency": "RON",
        "duration": "120min",
        "category": ServiceCategory.PACKAGE,
        "description": "Servicii complete + masaj facial + tratament păr",
        "status": ServiceStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "popularity_score": 68.9
    },
    {
        "id": str(uuid4()),
        "name": "Doar Spălat",
        "price": 15.0,
        "currency": "RON",
        "duration": "15min",
        "category": ServiceCategory.INDIVIDUAL,
        "description": "Spălat și uscat păr",
        "status": ServiceStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "popularity_score": 45.1
    },
    {
        "id": str(uuid4()),
        "name": "Tunsoare Retro",
        "price": 40.0,
        "currency": "RON",
        "duration": "60min",
        "category": ServiceCategory.INDIVIDUAL,
        "description": "Tunsoare în stil retro cu brici clasic",
        "status": ServiceStatus.INACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "popularity_score": 32.4
    }
]


@router.get("/services/stats")
async def get_service_stats(service_crud: ServiceCRUD = Depends(get_service_crud), user: dict = Depends(require_user)):
    """Get service statistics"""
    try:
        # Get statistics from database using CRUD
        stats = await service_crud.get_service_stats()
        
        logger.info("Retrieved service statistics from database",
                   extra={"total_services": stats.total_services, "active_services": stats.active_services})
        
        return {
            "success": True,
            "data": stats,
            "message": "Service statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve service stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve service statistics")


@router.get("/services", response_model=ServiceListResponse)
async def get_services(
    category: Optional[ServiceCategory] = Query(None, description="Filter by category"),
    status: Optional[ServiceStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service_crud: ServiceCRUD = Depends(get_service_crud),
    user: dict = Depends(require_user)
):
    """Get services with optional filtering"""
    try:
        # Get services from database using CRUD
        service_objects, total = await service_crud.get_services(
            category=category,
            status=status,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Retrieved {len(service_objects)} services from database",
                   extra={"total": total, "filters": {"category": category, "status": status}})
        
        return ServiceListResponse(
            success=True,
            data=service_objects,
            total=total,
            message=f"Retrieved {len(service_objects)} services"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve services: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve services")


@router.post("/services", response_model=ServiceResponse)
async def create_service(service_data: ServiceCreate, service_crud: ServiceCRUD = Depends(get_service_crud), user: dict = Depends(require_user)):
    """Create a new service"""
    try:
        # Create service in database using CRUD with user isolation
        user_id = user.get("sub")  # Get user ID from JWT token
        logger.info(f"Creating service for user_id: {user_id}, user: {user}")
        service_obj = await service_crud.create_service(service_data, user_id)
        
        logger.info(f"Created service {service_obj.id}: {service_obj.name}",
                   extra={"service_id": str(service_obj.id), "service_name": service_obj.name, "price": service_obj.price})
        
        return ServiceResponse(
            success=True,
            data=service_obj,
            message="Service created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create service")


@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, service_data: ServiceUpdate, service_crud: ServiceCRUD = Depends(get_service_crud), user: dict = Depends(require_user)):
    """Update an existing service"""
    try:
        # Update service in database using CRUD
        service_obj = await service_crud.update_service(service_id, service_data)
        
        if not service_obj:
            raise HTTPException(status_code=404, detail="Service not found")
        
        update_fields = list(service_data.model_dump(exclude_unset=True).keys())
        logger.info(f"Updated service {service_id}",
                   extra={"service_id": service_id, "updated_fields": update_fields})
        
        return ServiceResponse(
            success=True,
            data=service_obj,
            message="Service updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update service {service_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update service")


@router.delete("/services/{service_id}", response_model=ServiceResponse)
async def delete_service(service_id: str, service_crud: ServiceCRUD = Depends(get_service_crud), user: dict = Depends(require_user)):
    """Delete a service"""
    try:
        # Delete service from database using CRUD
        deleted = await service_crud.delete_service(service_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Service not found")
        
        logger.info(f"Deleted service {service_id}",
                   extra={"service_id": service_id})
        
        return ServiceResponse(
            success=True,
            message="Service deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete service {service_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete service")