from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from supabase import Client

from app.models.client import (
    Client as ClientModel, ClientCreate, ClientUpdate, 
    ClientStats, ClientStatus
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClientCRUD:
    """CRUD operations for clients"""
    
    def __init__(self, client: Client):
        self.client = client
        self.table = "clients"
    
    async def get_clients(
        self, 
        search: Optional[str] = None,
        status: Optional[ClientStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ClientModel], int]:
        """Get clients with optional search and filtering"""
        try:
            query = self.client.table(self.table).select("*")
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                query = query.or_(f"name.ilike.%{search}%,phone.ilike.%{search}%,email.ilike.%{search}%")
            
            # Apply status filter
            if status:
                query = query.eq("status", status.value)
            
            # Count total for pagination
            count_query = self.client.table(self.table).select("id", count="exact")
            if search:
                count_query = count_query.or_(f"name.ilike.%{search}%,phone.ilike.%{search}%,email.ilike.%{search}%")
            if status:
                count_query = count_query.eq("status", status.value)
            
            count_response = count_query.execute()
            total = count_response.count or 0
            
            # Get paginated results
            response = query.order("name", desc=False)\
                          .range(offset, offset + limit - 1)\
                          .execute()
            
            clients = []
            for row in response.data:
                # Generate avatar if not present
                avatar = row.get("avatar")
                if not avatar:
                    name_parts = row["name"].split()
                    avatar = "".join([part[0].upper() for part in name_parts[:2]])
                
                # Convert database row to Pydantic model
                client_data = {
                    "id": row["id"],
                    "name": row["name"],
                    "phone": row["phone"],
                    "email": row.get("email"),
                    "notes": row.get("notes"),
                    "status": ClientStatus(row["status"]),
                    "avatar": avatar,
                    "total_appointments": row.get("total_appointments", 0),
                    "last_appointment": datetime.fromisoformat(
                        row["last_appointment"].replace("Z", "+00:00")
                    ) if row.get("last_appointment") else None,
                    "created_at": datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                    "updated_at": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
                }
                clients.append(ClientModel(**client_data))
            
            logger.info(f"Retrieved {len(clients)} clients",
                       extra={"total": total, "search": search, "status": status})
            
            return clients, total
            
        except Exception as e:
            logger.error(f"Failed to retrieve clients: {e}", exc_info=True)
            raise
    
    async def get_client_stats(self) -> ClientStats:
        """Get client statistics"""
        try:
            # Get total clients
            total_response = self.client.table(self.table)\
                                      .select("id", count="exact")\
                                      .execute()
            total_clients = total_response.count or 0
            
            # Get active clients
            active_response = self.client.table(self.table)\
                                       .select("id", count="exact")\
                                       .eq("status", "active")\
                                       .execute()
            active_clients = active_response.count or 0
            
            # Get inactive clients
            inactive_clients = total_clients - active_clients
            
            # Get new clients this month
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_response = self.client.table(self.table)\
                                    .select("id", count="exact")\
                                    .gte("created_at", current_month.isoformat())\
                                    .execute()
            new_this_month = new_response.count or 0
            
            stats = ClientStats(
                total_clients=total_clients,
                new_this_month=new_this_month,
                active_clients=active_clients,
                inactive_clients=inactive_clients
            )
            
            logger.info(f"Retrieved client stats: {total_clients} total, {new_this_month} new this month")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to retrieve client stats: {e}", exc_info=True)
            raise
    
    async def create_client(self, client_data: ClientCreate) -> ClientModel:
        """Create a new client"""
        try:
            # Generate avatar initials
            name_parts = client_data.name.split()
            avatar = "".join([part[0].upper() for part in name_parts[:2]])
            
            # Convert Pydantic model to database format
            db_data = {
                "id": str(uuid4()),
                "name": client_data.name,
                "phone": client_data.phone,
                "email": client_data.email,
                "notes": client_data.notes,
                "status": client_data.status.value,
                "avatar": avatar,
                "total_appointments": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insert client
            response = self.client.table(self.table).insert(db_data).execute()
            
            if not response.data:
                raise Exception("Failed to create client")
            
            # Convert back to Pydantic model
            row = response.data[0]
            client = ClientModel(
                id=row["id"],
                name=row["name"],
                phone=row["phone"],
                email=row.get("email"),
                notes=row.get("notes"),
                status=ClientStatus(row["status"]),
                avatar=row["avatar"],
                total_appointments=row["total_appointments"],
                last_appointment=None,
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            
            logger.info(f"Created client {client.id}: {client.name}",
                       extra={"client_id": client.id, "client_name": client.name})
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create client: {e}", exc_info=True)
            raise
    
    async def update_client(self, client_id: str, client_data: ClientUpdate) -> ClientModel:
        """Update an existing client"""
        try:
            # Convert update data to database format
            update_data = {}
            update_fields = client_data.model_dump(exclude_unset=True)
            
            for field, value in update_fields.items():
                if field == "status":
                    update_data[field] = value.value if hasattr(value, 'value') else value
                else:
                    update_data[field] = value
            
            # Regenerate avatar if name changed
            if "name" in update_fields:
                name_parts = update_fields["name"].split()
                update_data["avatar"] = "".join([part[0].upper() for part in name_parts[:2]])
            
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Update client
            response = self.client.table(self.table)\
                                 .update(update_data)\
                                 .eq("id", client_id)\
                                 .execute()
            
            if not response.data:
                raise Exception("Client not found")
            
            # Convert back to Pydantic model
            row = response.data[0]
            client = ClientModel(
                id=row["id"],
                name=row["name"],
                phone=row["phone"],
                email=row.get("email"),
                notes=row.get("notes"),
                status=ClientStatus(row["status"]),
                avatar=row["avatar"],
                total_appointments=row.get("total_appointments", 0),
                last_appointment=datetime.fromisoformat(
                    row["last_appointment"].replace("Z", "+00:00")
                ) if row.get("last_appointment") else None,
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            
            logger.info(f"Updated client {client_id}",
                       extra={"client_id": client_id, "updated_fields": list(update_fields.keys())})
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to update client {client_id}: {e}", exc_info=True)
            raise
    
    async def delete_client(self, client_id: str) -> bool:
        """Delete a client"""
        try:
            response = self.client.table(self.table)\
                                 .delete()\
                                 .eq("id", client_id)\
                                 .execute()
            
            if not response.data:
                raise Exception("Client not found")
            
            logger.info(f"Deleted client {client_id}",
                       extra={"client_id": client_id})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete client {client_id}: {e}", exc_info=True)
            raise