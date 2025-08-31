from datetime import time
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.models.user import BusinessSettings, WorkingHours, NotificationSettings, AgentConfiguration
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Mock business settings data
MOCK_SETTINGS = {
    "name": "Salon Clasic",
    "address": "Str. Victoriei nr. 25, București, România",
    "phone": "+40721234567",
    "email": "contact@salonclasic.ro",
    "working_hours": [
        {
            "day_of_week": 0,  # Monday
            "start_time": time(9, 0),
            "end_time": time(18, 0),
            "is_closed": False
        },
        {
            "day_of_week": 1,  # Tuesday
            "start_time": time(9, 0),
            "end_time": time(18, 0),
            "is_closed": False
        },
        {
            "day_of_week": 2,  # Wednesday
            "start_time": time(9, 0),
            "end_time": time(18, 0),
            "is_closed": False
        },
        {
            "day_of_week": 3,  # Thursday
            "start_time": time(9, 0),
            "end_time": time(18, 0),
            "is_closed": False
        },
        {
            "day_of_week": 4,  # Friday
            "start_time": time(9, 0),
            "end_time": time(19, 0),
            "is_closed": False
        },
        {
            "day_of_week": 5,  # Saturday
            "start_time": time(10, 0),
            "end_time": time(16, 0),
            "is_closed": False
        },
        {
            "day_of_week": 6,  # Sunday
            "start_time": time(9, 0),
            "end_time": time(17, 0),
            "is_closed": True
        }
    ],
    "notifications": {
        "email_notifications": True,
        "sms_notifications": False,
        "appointment_reminders": True,
        "new_booking_alerts": True,
        "system_updates": True
    },
    "agent_config": {
        "enabled": False,
        "model": "gpt-4o-realtime-preview",
        "language": "ro-RO",
        "voice": "nova",
        "auto_booking": False,
        "confirmation_required": True
    },
    "timezone": "Europe/Bucharest"
}


@router.get("/settings")
async def get_business_settings():
    """Get current business settings"""
    try:
        # Convert working hours
        working_hours = [WorkingHours(**wh) for wh in MOCK_SETTINGS["working_hours"]]
        
        # Create settings object
        settings = BusinessSettings(
            name=MOCK_SETTINGS["name"],
            address=MOCK_SETTINGS["address"],
            phone=MOCK_SETTINGS["phone"],
            email=MOCK_SETTINGS["email"],
            working_hours=working_hours,
            notifications=NotificationSettings(**MOCK_SETTINGS["notifications"]),
            agent_config=AgentConfiguration(**MOCK_SETTINGS["agent_config"]),
            timezone=MOCK_SETTINGS["timezone"]
        )
        
        logger.info("Business settings retrieved successfully")
        
        return {
            "success": True,
            "data": settings,
            "message": "Business settings retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve business settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve business settings")


@router.put("/settings")
async def update_business_settings(settings: BusinessSettings):
    """Update business settings"""
    try:
        # Update mock settings
        MOCK_SETTINGS.update({
            "name": settings.name,
            "address": settings.address,
            "phone": settings.phone,
            "email": settings.email,
            "working_hours": [wh.model_dump() for wh in settings.working_hours],
            "notifications": settings.notifications.model_dump(),
            "agent_config": settings.agent_config.model_dump(),
            "timezone": settings.timezone
        })
        
        logger.info("Business settings updated successfully",
                   extra={
                       "salon_name": settings.name,
                       "working_days": len([wh for wh in settings.working_hours if not wh.is_closed])
                   })
        
        return {
            "success": True,
            "data": settings,
            "message": "Business settings updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update business settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update business settings")


@router.get("/settings/working-hours")
async def get_working_hours():
    """Get business working hours"""
    try:
        working_hours = [WorkingHours(**wh) for wh in MOCK_SETTINGS["working_hours"]]
        
        # Calculate working days
        working_days = len([wh for wh in working_hours if not wh.is_closed])
        
        return {
            "success": True,
            "data": working_hours,
            "metadata": {
                "total_days": len(working_hours),
                "working_days": working_days,
                "closed_days": len(working_hours) - working_days
            },
            "message": f"Working hours retrieved - {working_days} working days"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve working hours: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve working hours")


@router.put("/settings/working-hours")
async def update_working_hours(working_hours: list[WorkingHours]):
    """Update business working hours"""
    try:
        if len(working_hours) != 7:
            raise HTTPException(status_code=400, detail="Must provide working hours for all 7 days of the week")
        
        # Validate day_of_week values
        days_provided = {wh.day_of_week for wh in working_hours}
        if days_provided != {0, 1, 2, 3, 4, 5, 6}:
            raise HTTPException(status_code=400, detail="Must provide working hours for days 0-6 (Monday-Sunday)")
        
        # Update working hours
        MOCK_SETTINGS["working_hours"] = [wh.model_dump() for wh in working_hours]
        
        working_days = len([wh for wh in working_hours if not wh.is_closed])
        
        logger.info(f"Working hours updated - {working_days} working days",
                   extra={"working_days": working_days})
        
        return {
            "success": True,
            "data": working_hours,
            "message": f"Working hours updated - {working_days} working days configured"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update working hours: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update working hours")


@router.get("/settings/notifications")
async def get_notification_settings():
    """Get notification settings"""
    try:
        notifications = NotificationSettings(**MOCK_SETTINGS["notifications"])
        
        return {
            "success": True,
            "data": notifications,
            "message": "Notification settings retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve notification settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve notification settings")


@router.put("/settings/notifications")
async def update_notification_settings(notifications: NotificationSettings):
    """Update notification settings"""
    try:
        MOCK_SETTINGS["notifications"] = notifications.model_dump()
        
        enabled_count = sum([
            notifications.email_notifications,
            notifications.sms_notifications,
            notifications.appointment_reminders,
            notifications.new_booking_alerts,
            notifications.system_updates
        ])
        
        logger.info(f"Notification settings updated - {enabled_count} notifications enabled")
        
        return {
            "success": True,
            "data": notifications,
            "message": f"Notification settings updated - {enabled_count} notifications enabled"
        }
        
    except Exception as e:
        logger.error(f"Failed to update notification settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update notification settings")


@router.get("/settings/agent")
async def get_agent_settings():
    """Get voice agent settings"""
    try:
        agent_config = AgentConfiguration(**MOCK_SETTINGS["agent_config"])
        
        return {
            "success": True,
            "data": agent_config,
            "message": "Voice agent settings retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent settings")


@router.put("/settings/agent")
async def update_agent_settings(agent_config: AgentConfiguration):
    """Update voice agent settings"""
    try:
        MOCK_SETTINGS["agent_config"] = agent_config.model_dump()
        
        logger.info(f"Agent settings updated - enabled: {agent_config.enabled}",
                   extra={
                       "enabled": agent_config.enabled,
                       "model": agent_config.model,
                       "language": agent_config.language
                   })
        
        return {
            "success": True,
            "data": agent_config,
            "message": "Voice agent settings updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update agent settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update agent settings")