from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from supabase import Client

from app.models.user import (
    AgentStatusInfo, AgentStatus, ActivityLog, ActivityLogType, 
    AgentConfiguration
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global agent state tracking since agent_state table doesn't exist
_GLOBAL_AGENT_STATUS = AgentStatus.INACTIVE


class AgentCRUD:
    """CRUD operations for voice agent state and activity logs"""
    
    def __init__(self, client: Client):
        self.client = client
        # agent_state table doesn't exist - using defaults
        self.agent_table = "agent_state"
        # agent_activity_log table exists (singular name)
        self.logs_table = "agent_activity_log"
    
    async def get_agent_status(self) -> AgentStatusInfo:
        """Get current agent status with activity logs (using defaults for missing tables)"""
        try:
            # Use default agent state since agent_state table doesn't exist
            default_config = self.get_default_agent_config()
            
            # Try to get activity logs from existing table (if any)
            activity_logs = []
            try:
                # Try with singular table name from hint
                logs_response = self.client.table("agent_activity_log")\
                    .select("*")\
                    .order("timestamp", desc=True)\
                    .limit(50)\
                    .execute()
                
                for log_data in logs_response.data:
                    activity_logs.append(ActivityLog(
                        timestamp=datetime.fromisoformat(log_data["timestamp"].replace("Z", "+00:00")),
                        type=ActivityLogType(log_data["type"]),
                        message=log_data["message"],
                        client_info=log_data.get("client_info"),
                        details=log_data.get("details")
                    ))
            except Exception:
                # If logs table doesn't exist or has issues, use empty list
                logger.info("Activity logs table not available, using empty list")
                activity_logs = []
            
            # Return status info with global agent status
            global _GLOBAL_AGENT_STATUS
            status_info = AgentStatusInfo(
                status=_GLOBAL_AGENT_STATUS,  # Use global status
                last_activity=None,
                total_calls=0,
                success_rate=0.0,
                activity_log=activity_logs
            )
            
            logger.info(f"Retrieved agent status (defaults): {status_info.status}",
                       extra={"status": status_info.status, "total_calls": status_info.total_calls, "logs_count": len(activity_logs)})
            
            return status_info
            
        except Exception as e:
            logger.error(f"Failed to retrieve agent status: {e}", exc_info=True)
            raise
    
    async def update_agent_status(self, status: AgentStatus) -> bool:
        """Update agent status (global variable since agent_state table doesn't exist)"""
        try:
            # Update global status
            global _GLOBAL_AGENT_STATUS
            _GLOBAL_AGENT_STATUS = status
            
            # Add activity log for status change
            await self.add_activity_log(
                ActivityLogType.SYSTEM_STATUS,
                f"Agent vocal {'pornit' if status == AgentStatus.ACTIVE else 'oprit'}",
                details={"new_status": status.value}
            )
            
            logger.info(f"Agent status updated to: {status} (global variable)",
                       extra={"status": status.value, "note": "agent_state table missing - using global variable"})
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent status: {e}", exc_info=True)
            raise
    
    async def get_agent_config(self) -> AgentConfiguration:
        """Get agent configuration (returns defaults since agent_state table doesn't exist)"""
        try:
            # Since agent_state table doesn't exist, return default config
            config = self.get_default_agent_config()
            
            logger.info("Retrieved agent configuration (defaults)",
                       extra={"enabled": config.enabled, "model": config.model, "note": "agent_state table missing"})
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to retrieve agent config: {e}", exc_info=True)
            raise
    
    async def update_agent_config(self, config: AgentConfiguration) -> AgentConfiguration:
        """Update agent configuration (simulated since agent_state table doesn't exist)"""
        try:
            # Since agent_state table doesn't exist, simulate the update
            # and only store the config change in activity logs
            
            # Add activity log for config update
            await self.add_activity_log(
                ActivityLogType.SYSTEM_STATUS,
                "Configurație agent actualizată",
                details=config.model_dump()
            )
            
            logger.info("Agent configuration updated (simulated)",
                       extra={"enabled": config.enabled, "model": config.model, "note": "agent_state table missing - using activity logs only"})
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to update agent config: {e}", exc_info=True)
            raise
    
    async def add_activity_log(
        self, 
        log_type: ActivityLogType, 
        message: str, 
        client_info: Optional[str] = None, 
        details: Optional[dict] = None
    ) -> ActivityLog:
        """Add new activity log entry"""
        try:
            activity_data = {
                "id": str(uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": log_type.value,
                "message": message,
                "client_info": client_info,
                "details": details,
                "created_at": datetime.now().isoformat()
            }
            
            response = self.client.table(self.logs_table).insert(activity_data).execute()
            
            if response.data:
                log_entry = ActivityLog(
                    timestamp=datetime.now(),
                    type=log_type,
                    message=message,
                    client_info=client_info,
                    details=details
                )
                
                # Clean up old logs (keep only last 100)
                await self._cleanup_old_logs()
                
                logger.info(f"Activity log added: {log_type.value}",
                           extra={"type": log_type.value, "log_message": message})
                
                return log_entry
            
            raise Exception("Failed to add activity log")
            
        except Exception as e:
            logger.error(f"Failed to add activity log: {e}", exc_info=True)
            raise
    
    async def get_activity_logs(
        self, 
        limit: int = 20, 
        log_type: Optional[ActivityLogType] = None
    ) -> tuple[List[ActivityLog], int]:
        """Get activity logs with optional filtering"""
        try:
            query = self.client.table(self.logs_table).select("*")
            
            # Filter by type if specified
            if log_type:
                query = query.eq("type", log_type.value)
            
            # Count total for pagination
            count_query = self.client.table(self.logs_table).select("id", count="exact")
            if log_type:
                count_query = count_query.eq("type", log_type.value)
            
            count_response = count_query.execute()
            total = count_response.count or 0
            
            # Get logs ordered by timestamp (most recent first)
            response = query.order("timestamp", desc=True)\
                          .limit(limit)\
                          .execute()
            
            activity_logs = []
            for log_data in response.data:
                activity_logs.append(ActivityLog(
                    timestamp=datetime.fromisoformat(log_data["timestamp"].replace("Z", "+00:00")),
                    type=ActivityLogType(log_data["type"]),
                    message=log_data["message"],
                    client_info=log_data.get("client_info"),
                    details=log_data.get("details")
                ))
            
            logger.info(f"Retrieved {len(activity_logs)} activity logs from database",
                       extra={"total": total, "filter": log_type.value if log_type else None})
            
            return activity_logs, total
            
        except Exception as e:
            logger.error(f"Failed to retrieve activity logs: {e}", exc_info=True)
            raise
    
    async def increment_call_stats(self, success: bool) -> dict:
        """Increment call statistics (simulated since agent_state table doesn't exist)"""
        try:
            # Since agent_state table doesn't exist, we calculate stats from activity logs
            
            # Get recent activity logs to estimate stats
            try:
                logs_response = self.client.table(self.logs_table)\
                    .select("*")\
                    .in_("type", ["booking_success", "booking_failed"])\
                    .order("timestamp", desc=True)\
                    .limit(100)\
                    .execute()
                
                total_calls = len(logs_response.data)
                successful_calls = len([log for log in logs_response.data if log["type"] == "booking_success"])
                
            except Exception:
                # If can't get logs, use defaults
                total_calls = 0
                successful_calls = 0
            
            # Calculate new stats
            new_total_calls = total_calls + 1
            new_successful = successful_calls + (1 if success else 0)
            new_success_rate = (new_successful / new_total_calls) * 100 if new_total_calls > 0 else 0.0
            
            logger.info(f"Call stats calculated from logs: total={new_total_calls}, success_rate={new_success_rate:.1f}% (simulated)",
                       extra={"total_calls": new_total_calls, "success_rate": new_success_rate, "note": "agent_state table missing"})
            
            return {
                "total_calls": new_total_calls,
                "success_rate": new_success_rate,
                "call_successful": success
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate call stats: {e}", exc_info=True)
            raise
    
    async def simulate_incoming_call(self) -> dict:
        """Simulate incoming call for testing (creates real activity logs)"""
        try:
            # Check if agent is active using global status
            global _GLOBAL_AGENT_STATUS
            if _GLOBAL_AGENT_STATUS != AgentStatus.ACTIVE:
                raise Exception("Agent must be active to receive calls")
            
            # Generate realistic client info
            clients = ["Alexandru P.", "Maria I.", "Ion G.", "Elena V.", "Mihai D.", "Ana R.", "Cristian L."]
            phones = ["+40721***456", "+40722***567", "+40723***678", "+40724***789", "+40725***890"]
            services = ["Tunsoare Clasică", "Barbă Completă", "Pachet Completă", "Tunsoare + Barbă"]
            
            import random
            client = random.choice(clients)
            phone = random.choice(phones)
            service = random.choice(services)
            
            # Simulate call outcome (85% success rate)
            success = random.random() < 0.85
            
            if success:
                # Successful booking
                await self.add_activity_log(
                    ActivityLogType.BOOKING_SUCCESS,
                    f"Programare confirmată pentru {(datetime.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')}",
                    client_info=client,
                    details={
                        "phone": phone,
                        "service": service,
                        "time": f"{random.randint(9, 17)}:{'00' if random.choice([True, False]) else '30'}",
                        "duration": f"{random.randint(30, 90)} min",
                        "price": f"{random.randint(25, 120)} RON"
                    }
                )
            else:
                # Failed booking
                reasons = ["incomplete_info", "slot_occupied", "technical_error", "client_cancelled"]
                reason = random.choice(reasons)
                reason_messages = {
                    "incomplete_info": "Informații incomplete",
                    "slot_occupied": "Slot ocupat",
                    "technical_error": "Eroare tehnică",
                    "client_cancelled": "Client a anulat"
                }
                
                await self.add_activity_log(
                    ActivityLogType.BOOKING_FAILED,
                    f"Programare nereușită - {reason_messages[reason]}",
                    client_info=client,
                    details={
                        "phone": phone,
                        "requested_service": service,
                        "reason": reason
                    }
                )
            
            # Update call statistics
            stats = await self.increment_call_stats(success)
            
            return {
                "call_successful": success,
                "client": client,
                "phone": phone,
                "service": service if success else None,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Failed to simulate call: {e}", exc_info=True)
            raise
    
    async def create_default_agent_state(self) -> bool:
        """Create default agent state (simulated since agent_state table doesn't exist)"""
        try:
            # Since agent_state table doesn't exist, we simulate creating default state
            # by logging that the agent is initialized with defaults
            
            await self.add_activity_log(
                ActivityLogType.SYSTEM_STATUS,
                "Agent inicializat cu configurația implicită",
                details=self.get_default_agent_config().model_dump()
            )
            
            logger.info("Agent default state simulated (agent_state table missing)",
                       extra={"note": "Default state logged in activity logs only"})
            return True
            
        except Exception as e:
            logger.error(f"Failed to simulate default agent state: {e}", exc_info=True)
            raise
    
    async def _cleanup_old_logs(self) -> bool:
        """Clean up old activity logs (keep only last 100)"""
        try:
            # Get total count
            count_response = self.client.table(self.logs_table)\
                .select("id", count="exact")\
                .execute()
            
            total_logs = count_response.count or 0
            
            if total_logs > 100:
                # Get IDs of logs to delete (keep newest 100)
                logs_to_keep = self.client.table(self.logs_table)\
                    .select("id")\
                    .order("timestamp", desc=True)\
                    .limit(100)\
                    .execute()
                
                keep_ids = [log["id"] for log in logs_to_keep.data]
                
                # Delete old logs
                keep_ids_str = "(" + ",".join([f"'{id}'" for id in keep_ids]) + ")"
                delete_response = self.client.table(self.logs_table)\
                    .delete()\
                    .not_("id", "in", keep_ids_str)\
                    .execute()
                
                deleted_count = len(delete_response.data) if delete_response.data else 0
                
                logger.info(f"Cleaned up {deleted_count} old activity logs",
                           extra={"deleted": deleted_count, "kept": len(keep_ids)})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}", exc_info=True)
            return False
    
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