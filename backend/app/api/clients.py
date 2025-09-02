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
from app.database import get_database

router = APIRouter()
logger = get_logger(__name__)

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
async def get_client_stats():
    """Get client statistics"""
    try:
        active_clients = len([c for c in MOCK_CLIENTS if c["status"] == ClientStatus.ACTIVE])
        inactive_clients = len([c for c in MOCK_CLIENTS if c["status"] == ClientStatus.INACTIVE])
        
        # New clients this month (mock calculation)
        new_this_month = len([c for c in MOCK_CLIENTS if c["created_at"].month == datetime.now().month])
        
        stats = ClientStats(
            total_clients=len(MOCK_CLIENTS),
            new_this_month=new_this_month,
            active_clients=active_clients,
            inactive_clients=inactive_clients
        )
        
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
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get clients with optional search and filtering"""
    try:
        clients = MOCK_CLIENTS.copy()
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            clients = [
                client for client in clients
                if (search_lower in client["name"].lower() or
                    search_lower in client["phone"] or
                    (client["email"] and search_lower in client["email"].lower()))
            ]
        
        # Apply status filter
        if status:
            clients = [client for client in clients if client["status"] == status]
        
        # Apply pagination
        total = len(clients)
        clients = clients[offset:offset + limit]
        
        # Convert to Pydantic models
        client_objects = [Client(**client) for client in clients]
        
        logger.info(f"Retrieved {len(client_objects)} clients",
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
async def create_client(client_data: ClientCreate, request: Request):
    """Create a new client using Supabase"""
    sb_client = _get_write_client(request)
    
    if not sb_client:
        logger.error("No Supabase client available")
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        # Prepare client data for insertion
        new_client_data = {
            "name": client_data.name,
            "phone": client_data.phone,
            "email": client_data.email,
            "status": client_data.status.value if client_data.status else "active",
            "notes": client_data.notes
        }
        
        # Insert into Supabase
        response = sb_client.table("clients").insert(new_client_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create client - no data returned")
        
        created_client = response.data[0]
        
        logger.info(f"Created client {created_client['id']}: {created_client['name']}",
                   extra={"client_id": created_client['id'], "client_name": created_client['name']})
        
        # Convert to Client model
        client_obj = Client(**created_client)
        
        return ClientResponse(
            success=True,
            data=client_obj,
            message="Client created successfully"
        )
        
    except APIError as e:
        # PostgREST/Supabase specific errors
        error_msg = getattr(e, 'message', str(e))
        status_code = getattr(getattr(e, 'response', None), 'status_code', 400)
        
        logger.error(f"Supabase error creating client: {error_msg}", 
                    extra={"status_code": status_code})
        
        # Map common error codes
        if status_code == 409:
            raise HTTPException(status_code=409, detail=f"Conflict: {error_msg}")
        elif status_code == 422:
            raise HTTPException(status_code=422, detail=f"Validation error: {error_msg}")
        else:
            raise HTTPException(status_code=status_code, detail=f"Database error: {error_msg}")
            
    except Exception as e:
        logger.error(f"Failed to create client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, client_data: ClientUpdate):
    """Update an existing client"""
    try:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c["id"] == client_id), None)
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Update fields
        update_data = client_data.model_dump(exclude_unset=True)
        
        # Regenerate avatar if name changed
        if "name" in update_data:
            name_parts = update_data["name"].split()
            update_data["avatar"] = "".join([part[0].upper() for part in name_parts[:2]])
        
        client.update(update_data)
        client["updated_at"] = datetime.now()
        
        client_obj = Client(**client)
        
        logger.info(f"Updated client {client_id}",
                   extra={"client_id": client_id, "updated_fields": list(update_data.keys())})
        
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
async def delete_client(client_id: str):
    """Delete a client"""
    try:
        # Find and remove client
        global MOCK_CLIENTS
        client = next((c for c in MOCK_CLIENTS if c["id"] == client_id), None)
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        MOCK_CLIENTS = [c for c in MOCK_CLIENTS if c["id"] != client_id]
        
        logger.info(f"Deleted client {client_id}",
                   extra={"client_id": client_id, "client_name": client["name"]})
        
        return ClientResponse(
            success=True,
            message="Client deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete client {client_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete client")