from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from supabase import Client

from app.models.user import (
    BusinessSettings, WorkingHours, NotificationSettings, AgentConfiguration
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class BusinessSettingsCRUD:
    """CRUD operations for business settings"""
    
    def __init__(self, client: Client):
        self.client = client
        self.table = "business_settings"
    
    async def get_business_settings(self) -> BusinessSettings:
        """Get current business settings"""
        try:
            # Get business settings (should be only one record)
            response = self.client.table(self.table)\
                                 .select("*")\
                                 .limit(1)\
                                 .execute()
            
            if not response.data:
                # If no settings exist, create default settings
                return await self.create_default_settings()
            
            row = response.data[0]
            
            # Convert working hours from JSON to WorkingHours objects
            working_hours = []
            if row.get("working_hours"):
                for wh_data in row["working_hours"]:
                    working_hours.append(WorkingHours(**wh_data))
            
            # Convert notifications from JSON to NotificationSettings
            notifications = NotificationSettings(**row.get("notifications", {}))
            
            # Convert agent config from JSON to AgentConfiguration  
            agent_config = AgentConfiguration(**row.get("agent_config", {}))
            
            # Convert database row to Pydantic model
            settings = BusinessSettings(
                name=row["name"],
                address=row["address"],
                phone=row["phone"],
                email=row["email"],
                working_hours=working_hours,
                notifications=notifications,
                agent_config=agent_config,
                timezone=row.get("timezone", "Europe/Bucharest")
            )
            
            logger.info("Retrieved business settings from database",
                       extra={"salon_name": settings.name, "working_days": len([wh for wh in working_hours if not wh.is_closed])})
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to retrieve business settings: {e}", exc_info=True)
            raise
    
    async def update_business_settings(self, settings: BusinessSettings) -> BusinessSettings:
        """Update business settings"""
        try:
            # Convert Pydantic models to JSON for database storage
            db_data = {
                "name": settings.name,
                "address": settings.address,
                "phone": settings.phone,
                "email": settings.email,
                "working_hours": [wh.model_dump() for wh in settings.working_hours],
                "notifications": settings.notifications.model_dump(),
                "agent_config": settings.agent_config.model_dump(),
                "timezone": settings.timezone,
                "updated_at": datetime.now().isoformat()
            }
            
            # Check if settings exist
            existing_response = self.client.table(self.table)\
                                         .select("id")\
                                         .limit(1)\
                                         .execute()
            
            if existing_response.data:
                # Update existing settings
                response = self.client.table(self.table)\
                                    .update(db_data)\
                                    .eq("id", existing_response.data[0]["id"])\
                                    .execute()
            else:
                # Create new settings record
                db_data["id"] = str(uuid4())
                db_data["created_at"] = datetime.now().isoformat()
                response = self.client.table(self.table).insert(db_data).execute()
            
            if not response.data:
                raise Exception("Failed to update business settings")
            
            working_days = len([wh for wh in settings.working_hours if not wh.is_closed])
            
            logger.info("Updated business settings successfully",
                       extra={
                           "salon_name": settings.name,
                           "working_days": working_days,
                           "agent_enabled": settings.agent_config.enabled
                       })
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to update business settings: {e}", exc_info=True)
            raise
    
    async def get_working_hours(self) -> List[WorkingHours]:
        """Get business working hours"""
        try:
            response = self.client.table(self.table)\
                                 .select("working_hours")\
                                 .limit(1)\
                                 .execute()
            
            if not response.data or not response.data[0].get("working_hours"):
                return self.get_default_working_hours()
            
            working_hours = []
            for wh_data in response.data[0]["working_hours"]:
                working_hours.append(WorkingHours(**wh_data))
            
            working_days = len([wh for wh in working_hours if not wh.is_closed])
            
            logger.info(f"Retrieved working hours - {working_days} working days")
            
            return working_hours
            
        except Exception as e:
            logger.error(f"Failed to retrieve working hours: {e}", exc_info=True)
            raise
    
    async def update_working_hours(self, working_hours: List[WorkingHours]) -> List[WorkingHours]:
        """Update business working hours"""
        try:
            # Convert to JSON format
            working_hours_data = [wh.model_dump() for wh in working_hours]
            
            # Update in database
            existing_response = self.client.table(self.table)\
                                         .select("id")\
                                         .limit(1)\
                                         .execute()
            
            if existing_response.data:
                response = self.client.table(self.table)\
                                    .update({
                                        "working_hours": working_hours_data,
                                        "updated_at": datetime.now().isoformat()
                                    })\
                                    .eq("id", existing_response.data[0]["id"])\
                                    .execute()
                
                if not response.data:
                    raise Exception("Failed to update working hours")
            
            working_days = len([wh for wh in working_hours if not wh.is_closed])
            
            logger.info(f"Updated working hours - {working_days} working days configured")
            
            return working_hours
            
        except Exception as e:
            logger.error(f"Failed to update working hours: {e}", exc_info=True)
            raise
    
    async def get_notification_settings(self) -> NotificationSettings:
        """Get notification settings"""
        try:
            response = self.client.table(self.table)\
                                 .select("notifications")\
                                 .limit(1)\
                                 .execute()
            
            if not response.data or not response.data[0].get("notifications"):
                return self.get_default_notifications()
            
            notifications = NotificationSettings(**response.data[0]["notifications"])
            
            logger.info("Retrieved notification settings from database")
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to retrieve notification settings: {e}", exc_info=True)
            raise
    
    async def update_notification_settings(self, notifications: NotificationSettings) -> NotificationSettings:
        """Update notification settings"""
        try:
            # Update in database
            existing_response = self.client.table(self.table)\
                                         .select("id")\
                                         .limit(1)\
                                         .execute()
            
            if existing_response.data:
                response = self.client.table(self.table)\
                                    .update({
                                        "notifications": notifications.model_dump(),
                                        "updated_at": datetime.now().isoformat()
                                    })\
                                    .eq("id", existing_response.data[0]["id"])\
                                    .execute()
                
                if not response.data:
                    raise Exception("Failed to update notification settings")
            
            enabled_count = sum([
                notifications.email_notifications,
                notifications.sms_notifications,
                notifications.appointment_reminders,
                notifications.new_booking_alerts,
                notifications.system_updates
            ])
            
            logger.info(f"Updated notification settings - {enabled_count} notifications enabled")
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to update notification settings: {e}", exc_info=True)
            raise
    
    async def get_agent_settings(self) -> AgentConfiguration:
        """Get voice agent settings"""
        try:
            response = self.client.table(self.table)\
                                 .select("agent_config")\
                                 .limit(1)\
                                 .execute()
            
            if not response.data or not response.data[0].get("agent_config"):
                return self.get_default_agent_config()
            
            agent_config = AgentConfiguration(**response.data[0]["agent_config"])
            
            logger.info("Retrieved agent settings from database",
                       extra={"enabled": agent_config.enabled, "model": agent_config.model})
            
            return agent_config
            
        except Exception as e:
            logger.error(f"Failed to retrieve agent settings: {e}", exc_info=True)
            raise
    
    async def update_agent_settings(self, agent_config: AgentConfiguration) -> AgentConfiguration:
        """Update voice agent settings"""
        try:
            # Update in database
            existing_response = self.client.table(self.table)\
                                         .select("id")\
                                         .limit(1)\
                                         .execute()
            
            if existing_response.data:
                response = self.client.table(self.table)\
                                    .update({
                                        "agent_config": agent_config.model_dump(),
                                        "updated_at": datetime.now().isoformat()
                                    })\
                                    .eq("id", existing_response.data[0]["id"])\
                                    .execute()
                
                if not response.data:
                    raise Exception("Failed to update agent settings")
            
            logger.info(f"Updated agent settings - enabled: {agent_config.enabled}",
                       extra={
                           "enabled": agent_config.enabled,
                           "model": agent_config.model,
                           "language": agent_config.language
                       })
            
            return agent_config
            
        except Exception as e:
            logger.error(f"Failed to update agent settings: {e}", exc_info=True)
            raise
    
    async def create_default_settings(self) -> BusinessSettings:
        """Create default business settings if none exist"""
        try:
            default_settings = BusinessSettings(
                name="Salon Clasic",
                address="Str. Victoriei nr. 25, București, România",
                phone="+40721234567",
                email="contact@salonclasic.ro",
                working_hours=self.get_default_working_hours(),
                notifications=self.get_default_notifications(),
                agent_config=self.get_default_agent_config(),
                timezone="Europe/Bucharest"
            )
            
            # Save to database
            await self.update_business_settings(default_settings)
            
            logger.info("Created default business settings")
            
            return default_settings
            
        except Exception as e:
            logger.error(f"Failed to create default settings: {e}", exc_info=True)
            raise
    
    def get_default_working_hours(self) -> List[WorkingHours]:
        """Get default working hours"""
        from datetime import time
        return [
            WorkingHours(day_of_week=0, start_time=time(9, 0), end_time=time(18, 0), is_closed=False),  # Monday
            WorkingHours(day_of_week=1, start_time=time(9, 0), end_time=time(18, 0), is_closed=False),  # Tuesday
            WorkingHours(day_of_week=2, start_time=time(9, 0), end_time=time(18, 0), is_closed=False),  # Wednesday
            WorkingHours(day_of_week=3, start_time=time(9, 0), end_time=time(18, 0), is_closed=False),  # Thursday
            WorkingHours(day_of_week=4, start_time=time(9, 0), end_time=time(19, 0), is_closed=False),  # Friday
            WorkingHours(day_of_week=5, start_time=time(10, 0), end_time=time(16, 0), is_closed=False), # Saturday
            WorkingHours(day_of_week=6, start_time=time(9, 0), end_time=time(17, 0), is_closed=True),   # Sunday
        ]
    
    def get_default_notifications(self) -> NotificationSettings:
        """Get default notification settings"""
        return NotificationSettings(
            email_notifications=True,
            sms_notifications=False,
            appointment_reminders=True,
            new_booking_alerts=True,
            system_updates=True
        )
    
    def get_default_agent_config(self) -> AgentConfiguration:
        """Get default agent configuration"""
        return AgentConfiguration(
            enabled=False,
            model="gpt-4o-realtime-preview",
            language="ro-RO",
            voice="nova",
            auto_booking=False,
            confirmation_required=True
        )