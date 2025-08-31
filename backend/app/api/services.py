from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from uuid import uuid4

from app.models.service import (
    Service, ServiceCreate, ServiceUpdate, ServiceResponse,
    ServiceListResponse, ServiceStats, ServiceCategory, ServiceStatus
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

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
async def get_service_stats():
    """Get service statistics"""
    try:
        active_services = [s for s in MOCK_SERVICES if s["status"] == ServiceStatus.ACTIVE]
        
        # Calculate stats
        total_services = len(MOCK_SERVICES)
        active_count = len(active_services)
        average_price = sum(s["price"] for s in active_services) / len(active_services) if active_services else 0
        
        # Find most popular service
        most_popular = max(active_services, key=lambda s: s["popularity_score"], default=None)
        most_popular_name = most_popular["name"] if most_popular else None
        
        stats = ServiceStats(
            total_services=total_services,
            active_services=active_count,
            most_popular=most_popular_name,
            average_price=round(average_price, 2)
        )
        
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
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get services with optional filtering"""
    try:
        services = MOCK_SERVICES.copy()
        
        # Apply filters
        if category:
            services = [service for service in services if service["category"] == category]
            
        if status:
            services = [service for service in services if service["status"] == status]
        
        # Sort by popularity (descending)
        services.sort(key=lambda s: s["popularity_score"], reverse=True)
        
        # Apply pagination
        total = len(services)
        services = services[offset:offset + limit]
        
        # Convert to Pydantic models
        service_objects = [Service(**service) for service in services]
        
        logger.info(f"Retrieved {len(service_objects)} services",
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
async def create_service(service_data: ServiceCreate):
    """Create a new service"""
    try:
        # Create new service
        new_service = {
            "id": str(uuid4()),
            "popularity_score": 0.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            **service_data.model_dump()
        }
        
        # Add to mock data
        MOCK_SERVICES.append(new_service)
        
        service_obj = Service(**new_service)
        
        logger.info(f"Created service {service_obj.id}: {service_obj.name}",
                   extra={"service_id": service_obj.id, "name": service_obj.name, "price": service_obj.price})
        
        return ServiceResponse(
            success=True,
            data=service_obj,
            message="Service created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create service")


@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, service_data: ServiceUpdate):
    """Update an existing service"""
    try:
        # Find service
        service = next((s for s in MOCK_SERVICES if s["id"] == service_id), None)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Update fields
        update_data = service_data.model_dump(exclude_unset=True)
        service.update(update_data)
        service["updated_at"] = datetime.now()
        
        service_obj = Service(**service)
        
        logger.info(f"Updated service {service_id}",
                   extra={"service_id": service_id, "updated_fields": list(update_data.keys())})
        
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
async def delete_service(service_id: str):
    """Delete a service"""
    try:
        # Find and remove service
        global MOCK_SERVICES
        service = next((s for s in MOCK_SERVICES if s["id"] == service_id), None)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        MOCK_SERVICES = [s for s in MOCK_SERVICES if s["id"] != service_id]
        
        logger.info(f"Deleted service {service_id}",
                   extra={"service_id": service_id, "name": service["name"]})
        
        return ServiceResponse(
            success=True,
            message="Service deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete service {service_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete service")