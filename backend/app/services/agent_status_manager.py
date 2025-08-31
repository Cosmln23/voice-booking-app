"""
Voice Agent Status Management System
Handles agent state, activity tracking, and status updates
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum
import json

from app.core.logging import get_logger
from app.models.user import AgentStatus, ActivityLog, ActivityLogType

# Define ActivityLogType if not in models  
class ActivityLogTypeLocal:
    SYSTEM_STATUS = "SYSTEM_STATUS"
    INCOMING_CALL = "INCOMING_CALL" 
    BOOKING_SUCCESS = "BOOKING_SUCCESS"
    BOOKING_FAILED = "BOOKING_FAILED"
    VOICE_PROCESSING = "VOICE_PROCESSING"
from app.database.supabase_client import get_supabase

logger = get_logger(__name__)


class AgentState(str, Enum):
    """Extended agent states for internal management"""
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPING = "stopping"


class VoiceAgentStatusManager:
    """Manages voice agent status and activity"""
    
    def __init__(self):
        self.current_status = AgentState.INACTIVE
        self.start_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.activity_logs: List[Dict] = []
        self.connected_sessions: Dict[str, Dict] = {}
        self.processing_queue: List[str] = []
        
    async def start_agent(self) -> bool:
        """Start the voice agent"""
        try:
            if self.current_status != AgentState.INACTIVE:
                logger.warning(f"Cannot start agent - current status: {self.current_status}")
                return False
                
            self.current_status = AgentState.STARTING
            self.start_time = datetime.now()
            self.last_activity = datetime.now()
            
            # Log agent start
            await self.log_activity(
                ActivityLogTypeLocal.SYSTEM_STATUS,
                "Agent vocal pornit",
                details={
                    "start_time": self.start_time.isoformat(),
                    "previous_uptime": self._calculate_previous_uptime()
                }
            )
            
            # Simulate initialization process
            await asyncio.sleep(0.5)  # Brief initialization delay
            
            self.current_status = AgentState.ACTIVE
            logger.info("Voice agent started successfully")
            
            return True
            
        except Exception as e:
            self.current_status = AgentState.ERROR
            logger.error(f"Failed to start voice agent: {e}", exc_info=True)
            
            await self.log_activity(
                ActivityLogTypeLocal.SYSTEM_STATUS,
                f"Eroare la pornirea agentului: {str(e)}",
                details={"error_type": type(e).__name__, "error_message": str(e)}
            )
            
            return False
    
    async def stop_agent(self) -> bool:
        """Stop the voice agent"""
        try:
            if self.current_status == AgentState.INACTIVE:
                logger.warning("Agent is already inactive")
                return True
                
            self.current_status = AgentState.STOPPING
            
            # Calculate uptime
            uptime_minutes = 0
            if self.start_time:
                uptime_delta = datetime.now() - self.start_time
                uptime_minutes = int(uptime_delta.total_seconds() / 60)
            
            # Log agent stop
            await self.log_activity(
                ActivityLogTypeLocal.SYSTEM_STATUS,
                "Agent vocal oprit",
                details={
                    "uptime_minutes": uptime_minutes,
                    "total_calls": self.total_calls,
                    "success_rate": self.get_success_rate()
                }
            )
            
            # Reset status
            self.current_status = AgentState.INACTIVE
            self.start_time = None
            self.last_activity = datetime.now()
            
            logger.info(f"Voice agent stopped successfully (uptime: {uptime_minutes} minutes)")
            
            return True
            
        except Exception as e:
            self.current_status = AgentState.ERROR
            logger.error(f"Failed to stop voice agent: {e}", exc_info=True)
            
            await self.log_activity(
                ActivityLogTypeLocal.SYSTEM_STATUS,
                f"Eroare la oprirea agentului: {str(e)}",
                details={"error_type": type(e).__name__, "error_message": str(e)}
            )
            
            return False
    
    async def start_call(self, caller_info: str, session_id: str) -> bool:
        """Start processing a voice call"""
        try:
            if self.current_status != AgentState.ACTIVE:
                logger.warning(f"Cannot start call - agent status: {self.current_status}")
                return False
                
            # Add to processing queue
            self.processing_queue.append(session_id)
            self.current_status = AgentState.PROCESSING
            self.last_activity = datetime.now()
            
            # Store session info
            self.connected_sessions[session_id] = {
                "caller_info": caller_info,
                "start_time": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Log incoming call
            await self.log_activity(
                ActivityLogTypeLocal.INCOMING_CALL,
                f"Apel primit de la {caller_info}",
                client_info=caller_info,
                details={
                    "session_id": session_id,
                    "start_time": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Started call from {caller_info} (session: {session_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start call: {e}", exc_info=True)
            return False
    
    async def end_call(self, session_id: str, success: bool, booking_data: Optional[Dict] = None) -> bool:
        """End a voice call and log results"""
        try:
            if session_id not in self.connected_sessions:
                logger.warning(f"Unknown session ID: {session_id}")
                return False
                
            session = self.connected_sessions[session_id]
            caller_info = session.get("caller_info", "Unknown")
            
            # Update counters
            self.total_calls += 1
            if success:
                self.successful_calls += 1
            else:
                self.failed_calls += 1
            
            # Remove from processing queue
            if session_id in self.processing_queue:
                self.processing_queue.remove(session_id)
            
            # Update status
            if not self.processing_queue:
                self.current_status = AgentState.ACTIVE
            
            self.last_activity = datetime.now()
            
            # Calculate call duration
            start_time = datetime.fromisoformat(session["start_time"])
            duration_seconds = int((datetime.now() - start_time).total_seconds())
            
            # Log call result
            if success and booking_data:
                await self.log_activity(
                    ActivityLogTypeLocal.BOOKING_SUCCESS,
                    f"Programare confirmată pentru {booking_data.get('date', 'N/A')} la {booking_data.get('time', 'N/A')}",
                    client_info=caller_info,
                    details={
                        "session_id": session_id,
                        "duration_seconds": duration_seconds,
                        "booking_data": booking_data
                    }
                )
            else:
                await self.log_activity(
                    ActivityLogTypeLocal.BOOKING_FAILED,
                    "Programare nereușită - informații incomplete" if not success else "Apel încheiat fără programare",
                    client_info=caller_info,
                    details={
                        "session_id": session_id,
                        "duration_seconds": duration_seconds,
                        "reason": "incomplete_info" if not success else "no_booking"
                    }
                )
            
            # Clean up session
            del self.connected_sessions[session_id]
            
            logger.info(f"Ended call from {caller_info} (duration: {duration_seconds}s, success: {success})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end call: {e}", exc_info=True)
            return False
    
    async def log_activity(
        self, 
        activity_type: str, 
        message: str, 
        client_info: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Log agent activity"""
        try:
            activity = {
                "timestamp": datetime.now().isoformat(),
                "type": activity_type,
                "message": message,
                "client_info": client_info,
                "details": details or {}
            }
            
            # Add to local log (keep last 50 entries)
            self.activity_logs.insert(0, activity)
            if len(self.activity_logs) > 50:
                self.activity_logs = self.activity_logs[:50]
            
            # Store in database if available
            try:
                supabase = await get_supabase()
                if supabase.is_connected:
                    client = supabase.get_client()
                    if client:
                        client.table("agent_activity_log").insert({
                            "timestamp": activity["timestamp"],
                            "type": activity_type,
                            "message": message,
                            "client_info": client_info,
                            "details": details or {}
                        }).execute()
            except Exception as db_error:
                logger.warning(f"Failed to store activity in database: {db_error}")
                
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
    
    def get_status_info(self) -> Dict:
        """Get current agent status information"""
        return {
            "status": self.current_status.value,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "total_calls": self.total_calls,
            "success_rate": self.get_success_rate(),
            "uptime_minutes": self._calculate_uptime(),
            "active_sessions": len(self.connected_sessions),
            "processing_queue": len(self.processing_queue),
            "activity_log": self.activity_logs[:10]  # Last 10 activities
        }
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_calls == 0:
            return 0.0
        return round((self.successful_calls / self.total_calls) * 100, 1)
    
    def _calculate_uptime(self) -> int:
        """Calculate current uptime in minutes"""
        if not self.start_time or self.current_status == AgentState.INACTIVE:
            return 0
        return int((datetime.now() - self.start_time).total_seconds() / 60)
    
    def _calculate_previous_uptime(self) -> int:
        """Calculate previous session uptime (mock for now)"""
        # In production, this would be stored and retrieved from database
        return 0
    
    async def health_check(self) -> Dict:
        """Perform agent health check"""
        try:
            health_status = {
                "healthy": True,
                "status": self.current_status.value,
                "uptime_minutes": self._calculate_uptime(),
                "total_calls": self.total_calls,
                "success_rate": self.get_success_rate(),
                "last_activity": self.last_activity.isoformat() if self.last_activity else None,
                "issues": []
            }
            
            # Check for issues
            if self.current_status == AgentState.ERROR:
                health_status["healthy"] = False
                health_status["issues"].append("Agent in error state")
            
            if self.last_activity:
                inactive_minutes = (datetime.now() - self.last_activity).total_seconds() / 60
                if inactive_minutes > 60:  # Inactive for over 1 hour
                    health_status["issues"].append(f"No activity for {int(inactive_minutes)} minutes")
            
            if len(self.processing_queue) > 5:  # Too many pending calls
                health_status["issues"].append(f"High processing queue: {len(self.processing_queue)} calls")
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "healthy": False,
                "status": "error",
                "issues": [f"Health check failed: {str(e)}"]
            }


# Global agent status manager instance
agent_status_manager = VoiceAgentStatusManager()


def get_agent_status_manager() -> VoiceAgentStatusManager:
    """Get the global agent status manager instance"""
    return agent_status_manager