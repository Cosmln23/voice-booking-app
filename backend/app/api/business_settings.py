from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.user import BusinessSettings, WorkingHours, NotificationSettings, AgentConfiguration
from app.core.logging import get_logger
from app.core.auth import require_user
from app.database.crud_business_settings import BusinessSettingsCRUD
from app.database import get_database

router = APIRouter()
logger = get_logger(__name__)


async def get_business_settings_crud(db = Depends(get_database)) -> BusinessSettingsCRUD:
    """Dependency injection for BusinessSettingsCRUD"""
    return BusinessSettingsCRUD(db.get_client())



@router.get("/settings")
async def get_business_settings(
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Get current business settings"""
    try:
        settings = await settings_crud.get_business_settings()
        
        logger.info("Business settings retrieved successfully from database",
                   extra={"salon_name": settings.name})
        
        return {
            "success": True,
            "data": settings,
            "message": "Business settings retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve business settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve business settings")


@router.put("/settings")
async def update_business_settings(
    settings: BusinessSettings,
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Update business settings"""
    try:
        updated_settings = await settings_crud.update_business_settings(settings)
        
        working_days = len([wh for wh in settings.working_hours if not wh.is_closed])
        logger.info("Business settings updated successfully in database",
                   extra={
                       "salon_name": settings.name,
                       "working_days": working_days
                   })
        
        return {
            "success": True,
            "data": updated_settings,
            "message": "Business settings updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update business settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update business settings")


@router.get("/settings/working-hours")
async def get_working_hours(
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Get business working hours"""
    try:
        working_hours = await settings_crud.get_working_hours()
        
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
async def update_working_hours(
    working_hours: list[WorkingHours],
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Update business working hours"""
    try:
        if len(working_hours) != 7:
            raise HTTPException(status_code=400, detail="Must provide working hours for all 7 days of the week")
        
        # Validate day_of_week values
        days_provided = {wh.day_of_week for wh in working_hours}
        if days_provided != {0, 1, 2, 3, 4, 5, 6}:
            raise HTTPException(status_code=400, detail="Must provide working hours for days 0-6 (Monday-Sunday)")
        
        # Update working hours in database
        updated_hours = await settings_crud.update_working_hours(working_hours)
        
        working_days = len([wh for wh in working_hours if not wh.is_closed])
        
        logger.info(f"Working hours updated in database - {working_days} working days",
                   extra={"working_days": working_days})
        
        return {
            "success": True,
            "data": updated_hours,
            "message": f"Working hours updated - {working_days} working days configured"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update working hours: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update working hours")


@router.get("/settings/notifications")
async def get_notification_settings(
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Get notification settings"""
    try:
        notifications = await settings_crud.get_notification_settings()
        
        return {
            "success": True,
            "data": notifications,
            "message": "Notification settings retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve notification settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve notification settings")


@router.put("/settings/notifications")
async def update_notification_settings(
    notifications: NotificationSettings,
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Update notification settings"""
    try:
        updated_notifications = await settings_crud.update_notification_settings(notifications)
        
        enabled_count = sum([
            notifications.email_notifications,
            notifications.sms_notifications,
            notifications.appointment_reminders,
            notifications.new_booking_alerts,
            notifications.system_updates
        ])
        
        logger.info(f"Notification settings updated in database - {enabled_count} notifications enabled")
        
        return {
            "success": True,
            "data": updated_notifications,
            "message": f"Notification settings updated - {enabled_count} notifications enabled"
        }
        
    except Exception as e:
        logger.error(f"Failed to update notification settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update notification settings")


@router.get("/settings/agent")
async def get_agent_settings(
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Get voice agent settings"""
    try:
        agent_config = await settings_crud.get_agent_settings()
        
        return {
            "success": True,
            "data": agent_config,
            "message": "Voice agent settings retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent settings")


@router.put("/settings/agent")
async def update_agent_settings(
    agent_config: AgentConfiguration,
    settings_crud: BusinessSettingsCRUD = Depends(get_business_settings_crud),
    user: dict = Depends(require_user)
):
    """Update voice agent settings"""
    try:
        updated_config = await settings_crud.update_agent_settings(agent_config)
        
        logger.info(f"Agent settings updated in database - enabled: {agent_config.enabled}",
                   extra={
                       "enabled": agent_config.enabled,
                       "model": agent_config.model,
                       "language": agent_config.language
                   })
        
        return {
            "success": True,
            "data": updated_config,
            "message": "Voice agent settings updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update agent settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update agent settings")