from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends

from app.models.user import (
    AgentStatusInfo, AgentStatus, ActivityLog, ActivityLogType,
    AgentConfiguration
)
from app.core.logging import get_logger
from app.core.logging_sanitize import safe_extra
from app.database.crud_agent import AgentCRUD
from app.database import get_database

router = APIRouter()
logger = get_logger(__name__)


async def get_agent_crud(db = Depends(get_database)) -> AgentCRUD:
    """Dependency injection for AgentCRUD"""
    return AgentCRUD(db.get_client())






@router.get("/agent/status")
async def get_agent_status(
    agent_crud: AgentCRUD = Depends(get_agent_crud)
):
    """Get current voice agent status"""
    try:
        status_info = await agent_crud.get_agent_status()
        
        logger.info(f"Agent status retrieved from database: {status_info.status}",
                   extra={"status": status_info.status, "total_calls": status_info.total_calls})
        
        return {
            "success": True,
            "data": status_info,
            "message": f"Agent status: {status_info.status.value}"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent status")


@router.post("/agent/start")
async def start_agent(
    agent_crud: AgentCRUD = Depends(get_agent_crud)
):
    """Start the voice agent"""
    try:
        # Check current status
        current_status = await agent_crud.get_agent_status()
        
        if current_status.status == AgentStatus.ACTIVE:
            return {
                "success": False,
                "message": "Agent is already active"
            }
        
        # Update agent status in database
        success = await agent_crud.update_agent_status(AgentStatus.ACTIVE)
        
        if success:
            logger.info("Voice agent started successfully in database",
                       extra={"status": "active", "timestamp": datetime.now()})
            
            return {
                "success": True,
                "data": {"status": AgentStatus.ACTIVE},
                "message": "Agent vocal pornit cu succes"
            }
        
        raise Exception("Failed to update agent status")
        
    except Exception as e:
        logger.error(f"Failed to start voice agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start voice agent")


@router.post("/agent/stop")
async def stop_agent(
    agent_crud: AgentCRUD = Depends(get_agent_crud)
):
    """Stop the voice agent"""
    try:
        # Check current status
        current_status = await agent_crud.get_agent_status()
        
        if current_status.status == AgentStatus.INACTIVE:
            return {
                "success": False,
                "message": "Agent is already inactive"
            }
        
        # Update agent status in database
        success = await agent_crud.update_agent_status(AgentStatus.INACTIVE)
        
        if success:
            logger.info("Voice agent stopped successfully in database",
                       extra={"status": "inactive", "timestamp": datetime.now()})
            
            return {
                "success": True,
                "data": {"status": AgentStatus.INACTIVE},
                "message": "Agent vocal oprit cu succes"
            }
        
        raise Exception("Failed to update agent status")
        
    except Exception as e:
        logger.error(f"Failed to stop voice agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to stop voice agent")


@router.get("/agent/logs")
async def get_agent_logs(
    limit: int = 20,
    log_type: Optional[ActivityLogType] = None,
    agent_crud: AgentCRUD = Depends(get_agent_crud)
):
    """Get agent activity logs"""
    try:
        activity_logs, total = await agent_crud.get_activity_logs(limit, log_type)
        
        logger.info(f"Retrieved {len(activity_logs)} activity logs from database",
                   extra={"total_logs": total, "filter": log_type})
        
        return {
            "success": True,
            "data": activity_logs,
            "total": total,
            "message": f"Retrieved {len(activity_logs)} activity logs"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent logs")


@router.get("/agent/config")
async def get_agent_config(
    agent_crud: AgentCRUD = Depends(get_agent_crud)
):
    """Get agent configuration"""
    try:
        config = await agent_crud.get_agent_config()
        
        return {
            "success": True,
            "data": config,
            "message": "Agent configuration retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent configuration")


@router.put("/agent/config")
async def update_agent_config(
    config: AgentConfiguration,
    agent_crud: AgentCRUD = Depends(get_agent_crud)
):
    """Update agent configuration"""
    try:
        updated_config = await agent_crud.update_agent_config(config)
        
        logger.info("Agent configuration updated in database",
                   extra=safe_extra({"config_changes": config.model_dump()}))
        
        return {
            "success": True,
            "data": updated_config,
            "message": "Configurația agentului a fost actualizată cu succes"
        }
        
    except Exception as e:
        logger.error(f"Failed to update agent config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update agent configuration")


# Simulate incoming call (for testing)
@router.post("/agent/simulate-call")
async def simulate_incoming_call(
    agent_crud: AgentCRUD = Depends(get_agent_crud)
):
    """Simulate an incoming call for testing purposes"""
    try:
        call_result = await agent_crud.simulate_incoming_call()
        
        logger.info(f"Call simulated: {'success' if call_result['call_successful'] else 'failed'}",
                   extra={"client": call_result["client"], "success": call_result["call_successful"]})
        
        return {
            "success": True,
            "data": call_result,
            "message": f"Apel simulat: {'succes' if call_result['call_successful'] else 'eșuat'}"
        }
        
    except Exception as e:
        logger.error(f"Failed to simulate call: {e}", exc_info=True)
        if "must be active" in str(e).lower():
            raise HTTPException(status_code=400, detail="Agent must be active to receive calls")
        raise HTTPException(status_code=500, detail="Failed to simulate call")