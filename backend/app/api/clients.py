from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from uuid import uuid4
from postgrest import APIError

from app.models.client import (
    Client, ClientCreate, ClientUpdate, ClientResponse,
    ClientListResponse, ClientStats, ClientStatus
)
from app.core.logging import get_logger
from app.core.auth import require_user
from app.database.crud_clients import ClientCRUD
from app.database import get_database

router = APIRouter()
logger = get_logger(__name__)


async def get_client_crud(db = Depends(get_database)) -> ClientCRUD:
    """Dependency injection for ClientCRUD"""
    return ClientCRUD(db.get_client())

# Mock data
MOCK_CLIENTS = [
    {
        "id": str(uuid4()),
        "name": "Alexandru Popescu",
        "phone": "+40721123456",
        "email": "alex.popescu@email.com",
        "status": ClientStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "avatar": "AP",
        "total_appointments": 12,
        "last_appointment": datetime.now(),
        "notes": "Client VIP, preferă programări dimineața"
    },
    {
        "id": str(uuid4()),
        "name": "Maria Ionescu",
        "phone": "+40722234567",
        "email": "maria.ionescu@email.com",
        "status": ClientStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "avatar": "MI",
        "total_appointments": 8,
        "last_appointment": datetime(2024, 8, 20),
    },
    {
        "id": str(uuid4()),
        "name": "Ion Georgescu",
        "phone": "+40723345678",
        "email": None,
        "status": ClientStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "avatar": "IG",
        "total_appointments": 15,
        "last_appointment": datetime(2024, 8, 25),
        "notes": "Doar tuns, niciodată barbă"
    },
    {
        "id": str(uuid4()),
        "name": "Elena Vasile",
        "phone": "+40724456789",
        "email": "elena.v@email.com",
        "status": ClientStatus.INACTIVE,
        "created_at": datetime(2024, 6, 1),
        "updated_at": datetime.now(),
        "avatar": "EV",
        "total_appointments": 3,
        "last_appointment": datetime(2024, 6, 15),
    },
    {
        "id": str(uuid4()),
        "name": "Mihai Dumitrescu",
        "phone": "+40725567890",
        "email": "mihai.dumitrescu@email.com",
        "status": ClientStatus.ACTIVE,
        "created_at": datetime(2024, 8, 1),
        "updated_at": datetime.now(),
        "avatar": "MD",
        "total_appointments": 2,
        "last_appointment": datetime(2024, 8, 15),
        "notes": "Client nou, foarte punctual"
    }
]


@router.get("/clients/stats")
async def get_client_stats(
    client_crud: ClientCRUD = Depends(get_client_crud),
    user: dict = Depends(require_user)
):
    """Get client statistics"""
    try:
        # Get statistics from database using CRUD
        stats = await client_crud.get_client_stats()
        
        logger.info("Retrieved client statistics from database",
                   extra={"total_clients": stats.total_clients, "active_clients": stats.active_clients})
        
        return {
            "success": True,
            "data": stats,
            "message": "Client statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve client stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve client statistics")


@router.get("/clients", response_model=ClientListResponse)
async def get_clients(
    search: Optional[str] = Query(None, description="Search by name, phone, or email"),
    status: Optional[ClientStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    client_crud: ClientCRUD = Depends(get_client_crud),
    user: dict = Depends(require_user)
):
    """Get clients with optional search and filtering"""
    try:
        # Get clients from database using CRUD
        client_objects, total = await client_crud.get_clients(
            search=search,
            status=status,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Retrieved {len(client_objects)} clients from database",
                   extra={"total": total, "search": search, "status": status})
        
        return ClientListResponse(
            success=True,
            data=client_objects,
            total=total,
            message=f"Retrieved {len(client_objects)} clients"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve clients")


def _get_write_client(request: Request):
    """Get Supabase client for write operations"""
    return (getattr(request.app.state, "sb_service", None) or 
            getattr(request.app.state, "sb_anon", None))


@router.post("/clients", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate, 
    client_crud: ClientCRUD = Depends(get_client_crud),
    user: dict = Depends(require_user)
):
    """Create a new client"""
    try:
        # Create client in database using CRUD
        client_obj = await client_crud.create_client(client_data)
        
        logger.info(f"Created client {client_obj.id}: {client_obj.name}",
                   extra={"client_id": str(client_obj.id), "client_name": client_obj.name})
        
        return ClientResponse(
            success=True,
            data=client_obj,
            message="Client created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create client")


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str, 
    client_data: ClientUpdate, 
    client_crud: ClientCRUD = Depends(get_client_crud),
    user: dict = Depends(require_user)
):
    """Update an existing client"""
    try:
        # Update client in database using CRUD
        client_obj = await client_crud.update_client(client_id, client_data)
        
        if not client_obj:
            raise HTTPException(status_code=404, detail="Client not found")
        
        update_fields = list(client_data.model_dump(exclude_unset=True).keys())
        logger.info(f"Updated client {client_id}",
                   extra={"client_id": client_id, "updated_fields": update_fields})
        
        return ClientResponse(
            success=True,
            data=client_obj,
            message="Client updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update client {client_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update client")


@router.delete("/clients/{client_id}", response_model=ClientResponse)
async def delete_client(
    client_id: str, 
    client_crud: ClientCRUD = Depends(get_client_crud),
    user: dict = Depends(require_user)
):
    """Delete a client"""
    try:
        # Delete client from database using CRUD
        deleted = await client_crud.delete_client(client_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Client not found")
        
        logger.info(f"Deleted client {client_id}",
                   extra={"client_id": client_id})
        
        return ClientResponse(
            success=True,
            message="Client deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete client {client_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete client")