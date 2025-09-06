"""
WebSocket Connection Manager for Real-time Communication
Handles WebSocket connections, agent status, and real-time updates
"""

import asyncio
import json
from typing import Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self):
        # Active WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
        
        # Agent connections (for voice agent)
        self.agent_connections: Set[str] = set()
        
        # Admin connections (for dashboard updates)
        self.admin_connections: Set[str] = set()
        
        # Mobile connections (for mobile app)
        self.mobile_connections: Set[str] = set()
    
    async def connect(self, websocket: WebSocket, connection_type: str = "client", extra_data: dict = None) -> str:
        """Accept WebSocket connection and assign connection ID"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        # Store connection metadata
        metadata = {
            "type": connection_type,
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Add extra data if provided
        if extra_data:
            metadata.update(extra_data)
            
        self.connection_metadata[connection_id] = metadata
        
        # Add to specific connection sets based on type
        if connection_type == "agent":
            self.agent_connections.add(connection_id)
        elif connection_type == "admin":
            self.admin_connections.add(connection_id)
        elif connection_type == "mobile":
            self.mobile_connections.add(connection_id)
        
        logger.info(f"WebSocket connection established: {connection_id} ({connection_type})")
        
        # Send connection confirmation
        await self.send_personal_message(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
            
        # Remove from specific sets
        self.agent_connections.discard(connection_id)
        self.admin_connections.discard(connection_id)
        self.mobile_connections.discard(connection_id)
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def send_personal_message(self, connection_id: str, message: dict):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
                
                # Update last activity
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.now().isoformat()
                    
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def broadcast_to_admins(self, message: dict):
        """Broadcast message to all admin connections"""
        if not self.admin_connections:
            return
            
        disconnected = []
        for connection_id in self.admin_connections.copy():
            try:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Failed to broadcast to admin {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def broadcast_to_agents(self, message: dict):
        """Broadcast message to all agent connections"""
        if not self.agent_connections:
            return
            
        disconnected = []
        for connection_id in self.agent_connections.copy():
            try:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Failed to broadcast to agent {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connections"""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "admin_connections": len(self.admin_connections),
            "agent_connections": len(self.agent_connections),
            "mobile_connections": len(self.mobile_connections),
            "client_connections": len(self.active_connections) - len(self.admin_connections) - len(self.agent_connections) - len(self.mobile_connections),
            "connections": [
                {
                    "id": conn_id,
                    "type": metadata.get("type", "unknown"),
                    "connected_at": metadata.get("connected_at"),
                    "last_activity": metadata.get("last_activity")
                }
                for conn_id, metadata in self.connection_metadata.items()
            ]
        }


# Global connection manager instance
connection_manager = ConnectionManager()


async def handle_websocket_message(connection_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    try:
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to ping with pong
            await connection_manager.send_personal_message(connection_id, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "agent_status_update":
            # Broadcast agent status updates to admins
            await connection_manager.broadcast_to_admins({
                "type": "agent_status_changed",
                "data": message.get("data"),
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "appointment_update":
            # Broadcast appointment updates to all admin connections
            await connection_manager.broadcast_to_admins({
                "type": "appointment_updated",
                "data": message.get("data"),
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "voice_call_start":
            # Handle voice call initiation
            await connection_manager.broadcast_to_admins({
                "type": "voice_call_started",
                "data": message.get("data"),
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "voice_call_end":
            # Handle voice call completion
            await connection_manager.broadcast_to_admins({
                "type": "voice_call_ended",
                "data": message.get("data"),
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}", exc_info=True)