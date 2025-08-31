import asyncio
from typing import Dict, Callable, Any, Optional
from supabase import Client
from app.core.logging import get_logger

logger = get_logger(__name__)


class RealtimeManager:
    """Manages Supabase real-time subscriptions"""
    
    def __init__(self, client: Client):
        self.client = client
        self.subscriptions: Dict[str, Any] = {}
        self.callbacks: Dict[str, Callable] = {}
    
    def subscribe_to_appointments(self, callback: Callable[[Dict], None]) -> str:
        """Subscribe to real-time appointment changes"""
        try:
            subscription_id = "appointments_subscription"
            
            # Store callback
            self.callbacks[subscription_id] = callback
            
            # Create subscription
            subscription = self.client.table("appointments").on("*", self._handle_appointment_change)
            
            self.subscriptions[subscription_id] = subscription
            
            logger.info("Subscribed to appointments real-time updates")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Failed to subscribe to appointments: {e}", exc_info=True)
            raise
    
    def subscribe_to_clients(self, callback: Callable[[Dict], None]) -> str:
        """Subscribe to real-time client changes"""
        try:
            subscription_id = "clients_subscription"
            
            # Store callback
            self.callbacks[subscription_id] = callback
            
            # Create subscription
            subscription = self.client.table("clients").on("*", self._handle_client_change)
            
            self.subscriptions[subscription_id] = subscription
            
            logger.info("Subscribed to clients real-time updates")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Failed to subscribe to clients: {e}", exc_info=True)
            raise
    
    def subscribe_to_services(self, callback: Callable[[Dict], None]) -> str:
        """Subscribe to real-time service changes"""
        try:
            subscription_id = "services_subscription"
            
            # Store callback
            self.callbacks[subscription_id] = callback
            
            # Create subscription
            subscription = self.client.table("services").on("*", self._handle_service_change)
            
            self.subscriptions[subscription_id] = subscription
            
            logger.info("Subscribed to services real-time updates")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Failed to subscribe to services: {e}", exc_info=True)
            raise
    
    def subscribe_to_agent_logs(self, callback: Callable[[Dict], None]) -> str:
        """Subscribe to real-time agent activity log changes"""
        try:
            subscription_id = "agent_logs_subscription"
            
            # Store callback
            self.callbacks[subscription_id] = callback
            
            # Create subscription
            subscription = self.client.table("agent_activity_log").on("INSERT", self._handle_agent_log_change)
            
            self.subscriptions[subscription_id] = subscription
            
            logger.info("Subscribed to agent logs real-time updates")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Failed to subscribe to agent logs: {e}", exc_info=True)
            raise
    
    def _handle_appointment_change(self, payload: Dict) -> None:
        """Handle appointment table changes"""
        try:
            subscription_id = "appointments_subscription"
            
            if subscription_id in self.callbacks:
                event_data = {
                    "table": "appointments",
                    "event_type": payload.get("eventType"),
                    "record": payload.get("new") or payload.get("old"),
                    "timestamp": payload.get("timestamp")
                }
                
                self.callbacks[subscription_id](event_data)
                
                logger.info(f"Appointment change event: {payload.get('eventType')}",
                           extra={"event": payload.get("eventType"), "record_id": payload.get("new", {}).get("id")})
            
        except Exception as e:
            logger.error(f"Error handling appointment change: {e}", exc_info=True)
    
    def _handle_client_change(self, payload: Dict) -> None:
        """Handle client table changes"""
        try:
            subscription_id = "clients_subscription"
            
            if subscription_id in self.callbacks:
                event_data = {
                    "table": "clients",
                    "event_type": payload.get("eventType"),
                    "record": payload.get("new") or payload.get("old"),
                    "timestamp": payload.get("timestamp")
                }
                
                self.callbacks[subscription_id](event_data)
                
                logger.info(f"Client change event: {payload.get('eventType')}",
                           extra={"event": payload.get("eventType"), "record_id": payload.get("new", {}).get("id")})
            
        except Exception as e:
            logger.error(f"Error handling client change: {e}", exc_info=True)
    
    def _handle_service_change(self, payload: Dict) -> None:
        """Handle service table changes"""
        try:
            subscription_id = "services_subscription"
            
            if subscription_id in self.callbacks:
                event_data = {
                    "table": "services",
                    "event_type": payload.get("eventType"),
                    "record": payload.get("new") or payload.get("old"),
                    "timestamp": payload.get("timestamp")
                }
                
                self.callbacks[subscription_id](event_data)
                
                logger.info(f"Service change event: {payload.get('eventType')}",
                           extra={"event": payload.get("eventType"), "record_id": payload.get("new", {}).get("id")})
            
        except Exception as e:
            logger.error(f"Error handling service change: {e}", exc_info=True)
    
    def _handle_agent_log_change(self, payload: Dict) -> None:
        """Handle agent activity log changes"""
        try:
            subscription_id = "agent_logs_subscription"
            
            if subscription_id in self.callbacks:
                event_data = {
                    "table": "agent_activity_log",
                    "event_type": payload.get("eventType"),
                    "record": payload.get("new"),
                    "timestamp": payload.get("timestamp")
                }
                
                self.callbacks[subscription_id](event_data)
                
                logger.info(f"Agent log event: {payload.get('eventType')}",
                           extra={"event": payload.get("eventType"), "log_type": payload.get("new", {}).get("type")})
            
        except Exception as e:
            logger.error(f"Error handling agent log change: {e}", exc_info=True)
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a real-time subscription"""
        try:
            if subscription_id in self.subscriptions:
                subscription = self.subscriptions[subscription_id]
                subscription.unsubscribe()
                
                del self.subscriptions[subscription_id]
                if subscription_id in self.callbacks:
                    del self.callbacks[subscription_id]
                
                logger.info(f"Unsubscribed from {subscription_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {subscription_id}: {e}", exc_info=True)
            return False
    
    def unsubscribe_all(self) -> None:
        """Unsubscribe from all real-time subscriptions"""
        try:
            subscription_ids = list(self.subscriptions.keys())
            
            for subscription_id in subscription_ids:
                self.unsubscribe(subscription_id)
            
            logger.info("Unsubscribed from all real-time subscriptions")
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from all subscriptions: {e}", exc_info=True)
    
    def get_active_subscriptions(self) -> List[str]:
        """Get list of active subscription IDs"""
        return list(self.subscriptions.keys())


# Global realtime manager instance
realtime_manager: Optional[RealtimeManager] = None


def get_realtime_manager(client: Client) -> RealtimeManager:
    """Get or create realtime manager instance"""
    global realtime_manager
    
    if not realtime_manager:
        realtime_manager = RealtimeManager(client)
    
    return realtime_manager