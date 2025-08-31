from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
import random
from uuid import uuid4

from app.models.user import (
    AgentStatusInfo, AgentStatus, ActivityLog, ActivityLogType,
    AgentConfiguration
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Global agent status (in production this would be in database/redis)
AGENT_STATE = {
    "status": AgentStatus.INACTIVE,
    "last_activity": None,
    "total_calls": 0,
    "success_rate": 0.0,
    "activity_log": [],
    "config": {
        "enabled": False,
        "model": "gpt-4o-realtime-preview",
        "language": "ro-RO", 
        "voice": "nova",
        "auto_booking": False,
        "confirmation_required": True
    }
}

# Mock activity log entries
MOCK_ACTIVITIES = [
    {
        "timestamp": datetime.now() - timedelta(minutes=5),
        "type": ActivityLogType.INCOMING_CALL,
        "message": "Apel primit de la +40721***456",
        "client_info": "Alexandru P.",
        "details": {"duration": "2min 34s", "outcome": "success"}
    },
    {
        "timestamp": datetime.now() - timedelta(minutes=12),
        "type": ActivityLogType.BOOKING_SUCCESS,
        "message": "Programare confirmată pentru 2024-09-01 la 14:00",
        "client_info": "Maria I.",
        "details": {"service": "Tunsoare Clasică", "price": "35 RON"}
    },
    {
        "timestamp": datetime.now() - timedelta(minutes=25),
        "type": ActivityLogType.INCOMING_CALL,
        "message": "Apel primit de la +40722***789",
        "client_info": "Ion G.",
        "details": {"duration": "1min 45s", "outcome": "success"}
    },
    {
        "timestamp": datetime.now() - timedelta(minutes=43),
        "type": ActivityLogType.BOOKING_FAILED,
        "message": "Programare nereușită - slot ocupat",
        "client_info": "Elena V.",
        "details": {"requested_time": "2024-09-01 15:00", "reason": "slot_occupied"}
    },
    {
        "timestamp": datetime.now() - timedelta(hours=1, minutes=15),
        "type": ActivityLogType.SYSTEM_STATUS,
        "message": "Agent vocal pornit",
        "details": {"version": "1.0.0", "model": "gpt-4o-realtime-preview"}
    }
]


def add_activity_log(log_type: ActivityLogType, message: str, client_info: Optional[str] = None, details: Optional[dict] = None):
    """Add new activity to the log"""
    activity = ActivityLog(
        timestamp=datetime.now(),
        type=log_type,
        message=message,
        client_info=client_info,
        details=details
    )
    
    AGENT_STATE["activity_log"].insert(0, activity.model_dump())
    
    # Keep only last 50 entries
    if len(AGENT_STATE["activity_log"]) > 50:
        AGENT_STATE["activity_log"] = AGENT_STATE["activity_log"][:50]


@router.get("/agent/status")
async def get_agent_status():
    """Get current voice agent status"""
    try:
        # Initialize with mock data if empty
        if not AGENT_STATE["activity_log"]:
            AGENT_STATE["activity_log"] = [activity.copy() for activity in MOCK_ACTIVITIES]
            AGENT_STATE["total_calls"] = 127
            AGENT_STATE["success_rate"] = 89.5
            AGENT_STATE["last_activity"] = datetime.now() - timedelta(minutes=5)
        
        status_info = AgentStatusInfo(
            status=AGENT_STATE["status"],
            last_activity=AGENT_STATE["last_activity"],
            total_calls=AGENT_STATE["total_calls"],
            success_rate=AGENT_STATE["success_rate"],
            activity_log=[ActivityLog(**log) for log in AGENT_STATE["activity_log"]]
        )
        
        logger.info(f"Agent status retrieved: {AGENT_STATE['status']}",
                   extra={"status": AGENT_STATE["status"], "total_calls": AGENT_STATE["total_calls"]})
        
        return {
            "success": True,
            "data": status_info,
            "message": f"Agent status: {AGENT_STATE['status'].value}"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent status")


@router.post("/agent/start")
async def start_agent():
    """Start the voice agent"""
    try:
        if AGENT_STATE["status"] == AgentStatus.ACTIVE:
            return {
                "success": False,
                "message": "Agent is already active"
            }
        
        # Update agent status
        AGENT_STATE["status"] = AgentStatus.ACTIVE
        AGENT_STATE["last_activity"] = datetime.now()
        AGENT_STATE["config"]["enabled"] = True
        
        # Add activity log
        add_activity_log(
            ActivityLogType.SYSTEM_STATUS,
            "Agent vocal pornit",
            details={
                "model": AGENT_STATE["config"]["model"],
                "language": AGENT_STATE["config"]["language"],
                "voice": AGENT_STATE["config"]["voice"]
            }
        )
        
        logger.info("Voice agent started successfully",
                   extra={"status": "active", "timestamp": datetime.now()})
        
        return {
            "success": True,
            "data": {"status": AgentStatus.ACTIVE},
            "message": "Agent vocal pornit cu succes"
        }
        
    except Exception as e:
        logger.error(f"Failed to start voice agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start voice agent")


@router.post("/agent/stop")
async def stop_agent():
    """Stop the voice agent"""
    try:
        if AGENT_STATE["status"] == AgentStatus.INACTIVE:
            return {
                "success": False,
                "message": "Agent is already inactive"
            }
        
        # Update agent status
        AGENT_STATE["status"] = AgentStatus.INACTIVE
        AGENT_STATE["last_activity"] = datetime.now()
        AGENT_STATE["config"]["enabled"] = False
        
        # Add activity log
        add_activity_log(
            ActivityLogType.SYSTEM_STATUS,
            "Agent vocal oprit",
            details={"uptime_minutes": random.randint(45, 180)}
        )
        
        logger.info("Voice agent stopped successfully",
                   extra={"status": "inactive", "timestamp": datetime.now()})
        
        return {
            "success": True,
            "data": {"status": AgentStatus.INACTIVE},
            "message": "Agent vocal oprit cu succes"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop voice agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to stop voice agent")


@router.get("/agent/logs")
async def get_agent_logs(
    limit: int = 20,
    log_type: Optional[ActivityLogType] = None
):
    """Get agent activity logs"""
    try:
        logs = AGENT_STATE["activity_log"].copy()
        
        # Filter by type if specified
        if log_type:
            logs = [log for log in logs if log["type"] == log_type]
        
        # Apply limit
        logs = logs[:limit]
        
        # Convert to ActivityLog objects
        activity_logs = [ActivityLog(**log) for log in logs]
        
        logger.info(f"Retrieved {len(activity_logs)} activity logs",
                   extra={"total_logs": len(logs), "filter": log_type})
        
        return {
            "success": True,
            "data": activity_logs,
            "total": len(AGENT_STATE["activity_log"]),
            "message": f"Retrieved {len(activity_logs)} activity logs"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent logs")


@router.get("/agent/config")
async def get_agent_config():
    """Get agent configuration"""
    try:
        config = AgentConfiguration(**AGENT_STATE["config"])
        
        return {
            "success": True,
            "data": config,
            "message": "Agent configuration retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent configuration")


@router.put("/agent/config")
async def update_agent_config(config: AgentConfiguration):
    """Update agent configuration"""
    try:
        # Update configuration
        AGENT_STATE["config"].update(config.model_dump())
        
        # Add activity log
        add_activity_log(
            ActivityLogType.SYSTEM_STATUS,
            "Configurație agent actualizată",
            details=config.model_dump()
        )
        
        logger.info("Agent configuration updated",
                   extra={"config_changes": config.model_dump()})
        
        return {
            "success": True,
            "data": config,
            "message": "Configurația agentului a fost actualizată cu succes"
        }
        
    except Exception as e:
        logger.error(f"Failed to update agent config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update agent configuration")


# Simulate incoming call (for testing)
@router.post("/agent/simulate-call")
async def simulate_incoming_call():
    """Simulate an incoming call for testing purposes"""
    try:
        if AGENT_STATE["status"] != AgentStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Agent must be active to receive calls")
        
        # Generate random client info
        clients = ["Alexandru P.", "Maria I.", "Ion G.", "Elena V.", "Mihai D."]
        phones = ["+40721***456", "+40722***567", "+40723***678", "+40724***789", "+40725***890"]
        
        client = random.choice(clients)
        phone = random.choice(phones)
        
        # Simulate call outcome
        success = random.choice([True, True, True, False])  # 75% success rate
        
        if success:
            # Successful booking
            add_activity_log(
                ActivityLogType.BOOKING_SUCCESS,
                f"Programare confirmată pentru {datetime.now().strftime('%Y-%m-%d')}",
                client_info=client,
                details={
                    "phone": phone,
                    "service": random.choice(["Tunsoare Clasică", "Barbă Completă", "Pachet Completă"]),
                    "time": f"{random.randint(9, 17)}:00"
                }
            )
            AGENT_STATE["total_calls"] += 1
        else:
            # Failed booking
            add_activity_log(
                ActivityLogType.BOOKING_FAILED,
                "Programare nereușită - informații incomplete",
                client_info=client,
                details={
                    "phone": phone,
                    "reason": random.choice(["incomplete_info", "slot_occupied", "technical_error"])
                }
            )
            AGENT_STATE["total_calls"] += 1
        
        # Update success rate
        successful_calls = len([log for log in AGENT_STATE["activity_log"] if log["type"] == ActivityLogType.BOOKING_SUCCESS])
        AGENT_STATE["success_rate"] = (successful_calls / AGENT_STATE["total_calls"]) * 100 if AGENT_STATE["total_calls"] > 0 else 0
        AGENT_STATE["last_activity"] = datetime.now()
        
        return {
            "success": True,
            "data": {
                "call_successful": success,
                "client": client,
                "phone": phone
            },
            "message": f"Apel simulat: {'succes' if success else 'eșuat'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to simulate call: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to simulate call")