"""
User-isolated CRUD operations for clients
Uses user JWT for RLS enforcement - ensures data isolation per user/salon
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4

from app.models.client import Client as ClientModel, ClientCreate, ClientUpdate, ClientStatus
from app.core.logging import get_logger
from app.core.supabase_user import create_supabase_for_user, extract_user_id_from_jwt

logger = get_logger(__name__)


class UserClientCRUD:
    """User-isolated CRUD operations for clients with RLS enforcement"""
    
    def __init__(self, jwt_token: str, user_info: Dict[str, Any]):
        """
        Initialize with user JWT for RLS enforcement
        
        Args:
            jwt_token: User's JWT access token
            user_info: User info from require_user dependency
        """
        self.client = create_supabase_for_user(jwt_token)
        self.user_info = user_info
        self.user_id = extract_user_id_from_jwt(user_info)
        self.table = "clients"
    
    async def get_clients(
        self, 
        search: Optional[str] = None,
        status: Optional[ClientStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ClientModel], int]:
        """
        Get clients for current user with optional search and filtering
        RLS automatically filters to user's data only
        """
        try:
            # RLS will automatically filter by created_by = auth.uid()
            query = self.client.table(self.table).select("*")
            
            # Apply additional filters
            if search:
                query = query.ilike("name", f"%{search}%")
            
            if status:
                query = query.eq("status", status.value)
            
            # Count total for pagination (also RLS filtered)
            count_query = self.client.table(self.table).select("id", count="exact")
            if search:
                count_query = count_query.ilike("name", f"%{search}%")
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
                    "created_by": row.get("created_by"),
                    "avatar": avatar,
                    "total_appointments": row.get("total_appointments", 0),
                    "last_appointment": datetime.fromisoformat(
                        row["last_appointment"].replace("Z", "+00:00")
                    ) if row.get("last_appointment") else None,
                    "created_at": datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                    "updated_at": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
                }
                clients.append(ClientModel(**client_data))
            
            logger.info(f"Retrieved {len(clients)} clients for user {self.user_info.get('email')}",
                       extra={"total": total, "search": search, "status": status, "user_id": self.user_id})
            
            return clients, total
            
        except Exception as e:
            logger.error(f"Failed to retrieve clients for user {self.user_id}: {e}", exc_info=True)
            raise

    async def get_client_by_id(self, client_id: str) -> Optional[ClientModel]:
        """
        Get client by ID for current user
        RLS automatically ensures user can only access their own clients
        """
        try:
            response = self.client.table(self.table)\
                                 .select("*")\
                                 .eq("id", client_id)\
                                 .single()\
                                 .execute()
            
            if not response.data:
                return None
            
            row = response.data
            
            # Generate avatar if not present
            avatar = row.get("avatar")
            if not avatar:
                name_parts = row["name"].split()
                avatar = "".join([part[0].upper() for part in name_parts[:2]])
            
            client_data = {
                "id": row["id"],
                "name": row["name"],
                "phone": row["phone"],
                "email": row.get("email"),
                "notes": row.get("notes"),
                "status": ClientStatus(row["status"]),
                "created_by": row.get("created_by"),
                "avatar": avatar,
                "total_appointments": row.get("total_appointments", 0),
                "last_appointment": datetime.fromisoformat(
                    row["last_appointment"].replace("Z", "+00:00")
                ) if row.get("last_appointment") else None,
                "created_at": datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                "updated_at": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            }
            
            logger.debug(f"Retrieved client {client_id} for user {self.user_id}")
            return ClientModel(**client_data)
            
        except Exception as e:
            logger.error(f"Failed to retrieve client {client_id} for user {self.user_id}: {e}", exc_info=True)
            raise

    async def create_client(self, client_data: ClientCreate) -> ClientModel:
        """
        Create new client for current user
        created_by is automatically set by trigger
        """
        try:
            # Prepare data for database
            db_data = {
                "id": str(uuid4()),
                "name": client_data.name,
                "phone": client_data.phone,
                "email": client_data.email,
                "notes": client_data.notes,
                "status": client_data.status.value,
                # created_by will be set by trigger to auth.uid()
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            response = self.client.table(self.table).insert(db_data).execute()
            
            if not response.data:
                raise Exception("Failed to create client")
            
            # Return created client
            created_client = await self.get_client_by_id(response.data[0]["id"])
            
            logger.info(f"Created client {created_client.name} for user {self.user_info.get('email')}",
                       extra={"client_id": created_client.id, "user_id": self.user_id})
            
            return created_client
            
        except Exception as e:
            logger.error(f"Failed to create client for user {self.user_id}: {e}", exc_info=True)
            raise

    async def update_client(self, client_id: str, client_data: ClientUpdate) -> Optional[ClientModel]:
        """
        Update client for current user
        RLS automatically ensures user can only update their own clients
        """
        try:
            # Prepare update data (only include non-None values)
            update_data = {"updated_at": datetime.now().isoformat()}
            
            if client_data.name is not None:
                update_data["name"] = client_data.name
            if client_data.phone is not None:
                update_data["phone"] = client_data.phone
            if client_data.email is not None:
                update_data["email"] = client_data.email
            if client_data.notes is not None:
                update_data["notes"] = client_data.notes
            if client_data.status is not None:
                update_data["status"] = client_data.status.value
            
            response = self.client.table(self.table)\
                                 .update(update_data)\
                                 .eq("id", client_id)\
                                 .execute()
            
            if not response.data:
                return None  # Client not found or not owned by user
            
            # Return updated client
            updated_client = await self.get_client_by_id(client_id)
            
            logger.info(f"Updated client {client_id} for user {self.user_info.get('email')}",
                       extra={"client_id": client_id, "user_id": self.user_id})
            
            return updated_client
            
        except Exception as e:
            logger.error(f"Failed to update client {client_id} for user {self.user_id}: {e}", exc_info=True)
            raise

    async def delete_client(self, client_id: str) -> bool:
        """
        Delete client for current user
        RLS automatically ensures user can only delete their own clients
        """
        try:
            response = self.client.table(self.table)\
                                 .delete()\
                                 .eq("id", client_id)\
                                 .execute()
            
            success = bool(response.data)
            
            if success:
                logger.info(f"Deleted client {client_id} for user {self.user_info.get('email')}",
                           extra={"client_id": client_id, "user_id": self.user_id})
            else:
                logger.warning(f"Client {client_id} not found or not owned by user {self.user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete client {client_id} for user {self.user_id}: {e}", exc_info=True)
            raise

    async def get_client_stats(self) -> Dict[str, Any]:
        """
        Get client statistics for current user
        RLS automatically filters to user's data only
        """
        try:
            # Get total clients count (RLS filtered)
            total_response = self.client.table(self.table)\
                                      .select("id", count="exact")\
                                      .execute()
            total_clients = total_response.count or 0
            
            # Get active clients count (RLS filtered)
            active_response = self.client.table(self.table)\
                                       .select("id", count="exact")\
                                       .eq("status", ClientStatus.ACTIVE.value)\
                                       .execute()
            active_clients = active_response.count or 0
            
            # Calculate stats
            inactive_clients = total_clients - active_clients
            active_percentage = (active_clients / total_clients * 100) if total_clients > 0 else 0
            
            stats = {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "inactive_clients": inactive_clients,
                "active_percentage": round(active_percentage, 1)
            }
            
            logger.debug(f"Retrieved client stats for user {self.user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to retrieve client stats for user {self.user_id}: {e}", exc_info=True)
            raise