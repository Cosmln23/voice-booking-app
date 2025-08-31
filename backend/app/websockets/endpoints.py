"""
WebSocket endpoints for real-time communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
from typing import Optional

from app.websockets.connection_manager import connection_manager, handle_websocket_message
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    connection_type: str = Query("client", description="Connection type: client, admin, or agent")
):
    """
    Main WebSocket endpoint for real-time communication
    
    Connection types:
    - client: Regular client connections
    - admin: Dashboard admin connections 
    - agent: Voice agent connections
    """
    connection_id = None
    
    try:
        # Validate connection type
        if connection_type not in ["client", "admin", "agent"]:
            await websocket.close(code=1000, reason="Invalid connection type")
            return
        
        # Accept connection and get ID
        connection_id = await connection_manager.connect(websocket, connection_type)
        
        # Handle incoming messages
        while True:
            try:
                # Receive message
                raw_message = await websocket.receive_text()
                
                # Parse JSON message
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {connection_id}: {raw_message}")
                    continue
                
                # Handle message
                await handle_websocket_message(connection_id, message)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop for {connection_id}: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if connection_id:
            connection_manager.disconnect(connection_id)


@router.websocket("/ws/voice")
async def voice_websocket_endpoint(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for voice agent communication
    Handles audio streaming and real-time voice processing
    """
    connection_id = None
    
    try:
        # Accept connection as agent type
        connection_id = await connection_manager.connect(websocket, "agent")
        
        # Send voice connection ready message
        await connection_manager.send_personal_message(connection_id, {
            "type": "voice_connection_ready",
            "connection_id": connection_id,
            "capabilities": ["audio_streaming", "real_time_processing", "booking_management"],
            "timestamp": connection_manager.connection_metadata[connection_id]["connected_at"]
        })
        
        # Handle voice-specific messages
        while True:
            try:
                # Receive message (could be text or binary for audio)
                try:
                    raw_message = await websocket.receive_text()
                    # Handle text messages
                    message = json.loads(raw_message)
                    await handle_voice_message(connection_id, message)
                    
                except json.JSONDecodeError:
                    # If not JSON, might be binary audio data
                    binary_data = await websocket.receive_bytes()
                    await handle_voice_audio(connection_id, binary_data)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in voice WebSocket loop for {connection_id}: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Voice WebSocket connection error: {e}")
    finally:
        if connection_id:
            connection_manager.disconnect(connection_id)
            
            # Notify admins that voice agent disconnected
            await connection_manager.broadcast_to_admins({
                "type": "voice_agent_disconnected",
                "connection_id": connection_id,
                "timestamp": connection_manager.connection_metadata.get(connection_id, {}).get("connected_at")
            })


async def handle_voice_message(connection_id: str, message: dict):
    """Handle voice-specific WebSocket messages"""
    try:
        message_type = message.get("type")
        
        if message_type == "voice_status":
            # Update voice agent status
            await connection_manager.broadcast_to_admins({
                "type": "voice_agent_status",
                "connection_id": connection_id,
                "status": message.get("status"),
                "data": message.get("data"),
                "timestamp": message.get("timestamp")
            })
            
        elif message_type == "call_started":
            # Voice call initiated
            await connection_manager.broadcast_to_admins({
                "type": "voice_call_started",
                "connection_id": connection_id,
                "call_data": message.get("data"),
                "timestamp": message.get("timestamp")
            })
            
        elif message_type == "call_ended":
            # Voice call completed
            await connection_manager.broadcast_to_admins({
                "type": "voice_call_ended",
                "connection_id": connection_id,
                "call_result": message.get("result"),
                "duration": message.get("duration"),
                "timestamp": message.get("timestamp")
            })
            
        elif message_type == "booking_attempt":
            # Booking attempt from voice
            await connection_manager.broadcast_to_admins({
                "type": "voice_booking_attempt",
                "connection_id": connection_id,
                "booking_data": message.get("data"),
                "timestamp": message.get("timestamp")
            })
            
        elif message_type == "transcription":
            # Real-time transcription
            await connection_manager.broadcast_to_admins({
                "type": "voice_transcription",
                "connection_id": connection_id,
                "text": message.get("text"),
                "confidence": message.get("confidence"),
                "timestamp": message.get("timestamp")
            })
            
        else:
            logger.warning(f"Unknown voice message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling voice message: {e}", exc_info=True)


async def handle_voice_audio(connection_id: str, audio_data: bytes):
    """Handle binary audio data from voice connections"""
    try:
        # Log audio data received (in production, this would process the audio)
        logger.info(f"Received audio data from {connection_id}: {len(audio_data)} bytes")
        
        # Notify admins of audio activity
        await connection_manager.broadcast_to_admins({
            "type": "voice_audio_activity",
            "connection_id": connection_id,
            "audio_size": len(audio_data),
            "timestamp": connection_manager.connection_metadata.get(connection_id, {}).get("last_activity")
        })
        
        # In production, this would:
        # 1. Send audio to OpenAI Realtime API
        # 2. Process the response
        # 3. Handle booking requests
        # 4. Send audio response back
        
        # For now, just acknowledge receipt
        await connection_manager.send_personal_message(connection_id, {
            "type": "audio_received",
            "size": len(audio_data),
            "timestamp": connection_manager.connection_metadata.get(connection_id, {}).get("last_activity")
        })
        
    except Exception as e:
        logger.error(f"Error handling voice audio: {e}", exc_info=True)