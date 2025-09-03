from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from supabase import Client

from app.models.service import (
    Service as ServiceModel, ServiceCreate, ServiceUpdate, 
    ServiceStats, ServiceCategory, ServiceStatus
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ServiceCRUD:
    """CRUD operations for services"""
    
    def __init__(self, client: Client):
        self.client = client
        self.table = "services"
    
    async def get_services(
        self, 
        category: Optional[ServiceCategory] = None,
        status: Optional[ServiceStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ServiceModel], int]:
        """Get services with optional filtering"""
        try:
            query = self.client.table(self.table).select("*")
            
            # Apply filters
            if category:
                query = query.eq("category", category.value)
            
            if status:
                query = query.eq("status", status.value)
            
            # Count total for pagination
            count_query = self.client.table(self.table).select("id", count="exact")
            if category:
                count_query = count_query.eq("category", category.value)
            if status:
                count_query = count_query.eq("status", status.value)
            
            count_response = count_query.execute()
            total = count_response.count or 0
            
            # Get paginated results sorted by popularity
            response = query.order("popularity_score", desc=True)\
                          .range(offset, offset + limit - 1)\
                          .execute()
            
            services = []
            for row in response.data:
                # Convert database row to Pydantic model
                service_data = {
                    "id": row["id"],
                    "name": row["name"],
                    "price": float(row["price"]),
                    "currency": row["currency"],
                    "duration": row["duration"],
                    "category": ServiceCategory(row["category"]),
                    "description": row.get("description"),
                    "status": ServiceStatus(row["status"]),
                    "popularity_score": float(row.get("popularity_score", 0.0)),
                    "created_at": datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                    "updated_at": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
                }
                services.append(ServiceModel(**service_data))
            
            logger.info(f"Retrieved {len(services)} services",
                       extra={"total": total, "filters": {"category": category, "status": status}})
            
            return services, total
            
        except Exception as e:
            logger.error(f"Failed to retrieve services: {e}", exc_info=True)
            raise
    
    async def get_service_stats(self) -> ServiceStats:
        """Get service statistics"""
        try:
            # Get total services
            total_response = self.client.table(self.table)\
                                      .select("id", count="exact")\
                                      .execute()
            total_services = total_response.count or 0
            
            # Get active services
            active_response = self.client.table(self.table)\
                                       .select("id", count="exact")\
                                       .eq("status", "active")\
                                       .execute()
            active_services = active_response.count or 0
            
            # Get most popular service
            popular_response = self.client.table(self.table)\
                                        .select("name, popularity_score")\
                                        .eq("status", "active")\
                                        .order("popularity_score", desc=True)\
                                        .limit(1)\
                                        .execute()
            
            most_popular = popular_response.data[0]["name"] if popular_response.data else None
            
            # Calculate average price for active services
            price_response = self.client.table(self.table)\
                                      .select("price")\
                                      .eq("status", "active")\
                                      .execute()
            
            average_price = 0.0
            if price_response.data:
                total_price = sum(float(row["price"]) for row in price_response.data)
                average_price = total_price / len(price_response.data)
            
            stats = ServiceStats(
                total_services=total_services,
                active_services=active_services,
                most_popular=most_popular,
                average_price=round(average_price, 2)
            )
            
            logger.info(f"Retrieved service stats: {total_services} total, {active_services} active")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to retrieve service stats: {e}", exc_info=True)
            raise
    
    async def create_service(self, service_data: ServiceCreate, user_id: str = None) -> ServiceModel:
        """Create a new service"""
        try:
            # Convert Pydantic model to database format
            db_data = {
                "id": str(uuid4()),
                "name": service_data.name,
                "price": service_data.price,
                "currency": service_data.currency,
                "duration": service_data.duration,
                "category": service_data.category.value,
                "description": service_data.description,
                "status": service_data.status.value,
                "popularity_score": 0.0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Add created_by for RLS policy compliance
            if user_id:
                db_data["created_by"] = user_id
                logger.info(f"Adding created_by field: {user_id}")
            else:
                logger.warning("No user_id provided for service creation - RLS may fail")
            
            logger.info(f"Service data before insert: {db_data}")
            # Insert service
            response = self.client.table(self.table).insert(db_data).execute()
            
            if not response.data:
                raise Exception("Failed to create service")
            
            # Convert back to Pydantic model
            row = response.data[0]
            service = ServiceModel(
                id=row["id"],
                name=row["name"],
                price=float(row["price"]),
                currency=row["currency"],
                duration=row["duration"],
                category=ServiceCategory(row["category"]),
                description=row.get("description"),
                status=ServiceStatus(row["status"]),
                popularity_score=float(row["popularity_score"]),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            
            logger.info(f"Created service {service.id}: {service.name}",
                       extra={"service_id": service.id, "service_name": service.name, "price": service.price})
            
            return service
            
        except Exception as e:
            logger.error(f"Failed to create service: {e}", exc_info=True)
            raise
    
    async def update_service(self, service_id: str, service_data: ServiceUpdate) -> ServiceModel:
        """Update an existing service"""
        try:
            # Convert update data to database format
            update_data = {}
            update_fields = service_data.model_dump(exclude_unset=True)
            
            for field, value in update_fields.items():
                if field in ["category", "status"]:
                    update_data[field] = value.value if hasattr(value, 'value') else value
                else:
                    update_data[field] = value
            
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Update service
            response = self.client.table(self.table)\
                                 .update(update_data)\
                                 .eq("id", service_id)\
                                 .execute()
            
            if not response.data:
                raise Exception("Service not found")
            
            # Convert back to Pydantic model
            row = response.data[0]
            service = ServiceModel(
                id=row["id"],
                name=row["name"],
                price=float(row["price"]),
                currency=row["currency"],
                duration=row["duration"],
                category=ServiceCategory(row["category"]),
                description=row.get("description"),
                status=ServiceStatus(row["status"]),
                popularity_score=float(row.get("popularity_score", 0.0)),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            
            logger.info(f"Updated service {service_id}",
                       extra={"service_id": service_id, "updated_fields": list(update_fields.keys())})
            
            return service
            
        except Exception as e:
            logger.error(f"Failed to update service {service_id}: {e}", exc_info=True)
            raise
    
    async def delete_service(self, service_id: str) -> bool:
        """Delete a service"""
        try:
            response = self.client.table(self.table)\
                                 .delete()\
                                 .eq("id", service_id)\
                                 .execute()
            
            if not response.data:
                raise Exception("Service not found")
            
            logger.info(f"Deleted service {service_id}",
                       extra={"service_id": service_id})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete service {service_id}: {e}", exc_info=True)
            raise