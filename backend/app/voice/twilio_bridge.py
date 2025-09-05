"""
Twilio Bridge for OpenAI Realtime API
Handles WebSocket bridge between Twilio Media Streams and OpenAI Realtime API
"""

import asyncio
import json
import base64
import websockets
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import audioop

from app.core.logging import get_logger
from app.voice.openai_client import OpenAIRealtimeClient
from app.database import get_database

logger = get_logger(__name__)


class TwilioOpenAIBridge:
    """
    WebSocket bridge between Twilio Media Streams and OpenAI Realtime API
    Handles audio format conversion and bidirectional streaming
    """
    
    def __init__(self):
        # Audio format constants
        self.TWILIO_SAMPLE_RATE = 8000  # Twilio uses 8kHz
        self.OPENAI_SAMPLE_RATE = 24000  # OpenAI expects 24kHz
        self.TWILIO_CHANNELS = 1  # Mono
        self.OPENAI_CHANNELS = 1  # Mono
        
        # Connection state
        self.twilio_websocket = None
        self.openai_client = None
        self.active = False
        
        # Call information
        self.call_sid = None
        self.from_number = None
        self.to_number = None
        
        # Audio buffers
        self.twilio_audio_buffer = bytearray()
        self.openai_audio_buffer = bytearray()
        
        logger.info("Twilio-OpenAI bridge initialized")
    
    async def handle_twilio_connection(self, websocket, path):
        """
        Handle incoming Twilio Media Stream WebSocket connection
        
        Args:
            websocket: Twilio WebSocket connection
            path: WebSocket path (contains call information)
        """
        try:
            logger.info(f"New Twilio connection from {websocket.remote_address}")
            self.twilio_websocket = websocket
            self.active = True
            
            # Wait for Twilio start message
            async for message in websocket:
                data = json.loads(message)
                message_type = data.get("event")
                
                if message_type == "start":
                    await self._handle_twilio_start(data)
                    break
            
            # Handle ongoing messages
            async for message in websocket:
                data = json.loads(message)
                await self._handle_twilio_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("Twilio connection closed")
            await self._cleanup()
        except Exception as e:
            logger.error(f"Error handling Twilio connection: {e}", exc_info=True)
            await self._cleanup()
    
    async def _handle_twilio_start(self, data: Dict[str, Any]):
        """Handle Twilio stream start message"""
        try:
            start_data = data.get("start", {})
            self.call_sid = start_data.get("callSid")
            
            # Extract call information from custom parameters
            custom_params = start_data.get("customParameters", {})
            self.from_number = custom_params.get("From")
            self.to_number = custom_params.get("To")
            
            logger.info(f"Twilio call started: {self.call_sid}, from {self.from_number} to {self.to_number}")
            
            # Initialize OpenAI client
            database = get_database()
            supabase_client = database.get_client()
            
            self.openai_client = OpenAIRealtimeClient(supabase_client)
            
            # Connect to OpenAI with call information
            await self.openai_client.connect(
                twilio_call_sid=self.call_sid,
                caller_number=self.from_number,
                called_number=self.to_number
            )
            
            # Start listening for OpenAI responses
            asyncio.create_task(self._listen_openai_responses())
            
            logger.info("OpenAI connection established for Twilio call")
            
        except Exception as e:
            logger.error(f"Error handling Twilio start: {e}", exc_info=True)
            await self._send_twilio_error("Failed to initialize voice assistant")
    
    async def _handle_twilio_message(self, data: Dict[str, Any]):
        """Handle different Twilio message types"""
        
        message_type = data.get("event")
        
        if message_type == "media":
            await self._handle_twilio_media(data)
        
        elif message_type == "stop":
            logger.info("Twilio stream stopped")
            await self._cleanup()
        
        elif message_type == "mark":
            # Mark message for audio synchronization
            mark_data = data.get("mark", {})
            logger.debug(f"Twilio mark: {mark_data}")
        
        else:
            logger.debug(f"Unhandled Twilio message type: {message_type}")
    
    async def _handle_twilio_media(self, data: Dict[str, Any]):
        """Handle incoming audio from Twilio"""
        try:
            media_data = data.get("media", {})
            payload = media_data.get("payload", "")
            
            if not payload:
                return
            
            # Decode audio from base64
            audio_bytes = base64.b64decode(payload)
            
            # Convert from μ-law to linear PCM
            linear_audio = audioop.ulaw2lin(audio_bytes, 2)
            
            # Resample from 8kHz to 24kHz for OpenAI
            resampled_audio = self._resample_audio(
                linear_audio, 
                self.TWILIO_SAMPLE_RATE, 
                self.OPENAI_SAMPLE_RATE
            )
            
            # Send to OpenAI
            if self.openai_client and self.openai_client.connected:
                await self.openai_client.handle_audio_input(resampled_audio)
            
        except Exception as e:
            logger.error(f"Error handling Twilio media: {e}")
    
    async def _listen_openai_responses(self):
        """Listen for OpenAI audio responses and forward to Twilio"""
        try:
            await self.openai_client.listen_for_responses(self._handle_openai_audio)
        except Exception as e:
            logger.error(f"Error listening to OpenAI responses: {e}")
    
    async def _handle_openai_audio(self, audio_bytes: bytes):
        """Handle audio response from OpenAI and send to Twilio"""
        try:
            # Resample from 24kHz to 8kHz for Twilio
            resampled_audio = self._resample_audio(
                audio_bytes,
                self.OPENAI_SAMPLE_RATE,
                self.TWILIO_SAMPLE_RATE
            )
            
            # Convert to μ-law for Twilio
            ulaw_audio = audioop.lin2ulaw(resampled_audio, 2)
            
            # Encode to base64
            audio_b64 = base64.b64encode(ulaw_audio).decode()
            
            # Send to Twilio
            media_message = {
                "event": "media",
                "streamSid": getattr(self, 'stream_sid', None),
                "media": {
                    "payload": audio_b64
                }
            }
            
            if self.twilio_websocket and not self.twilio_websocket.closed:
                await self.twilio_websocket.send(json.dumps(media_message))
            
        except Exception as e:
            logger.error(f"Error handling OpenAI audio: {e}")
    
    def _resample_audio(self, audio_data: bytes, from_rate: int, to_rate: int) -> bytes:
        """
        Resample audio between different sample rates
        
        Args:
            audio_data: Input audio bytes
            from_rate: Source sample rate
            to_rate: Target sample rate
            
        Returns:
            Resampled audio bytes
        """
        try:
            if from_rate == to_rate:
                return audio_data
            
            # Use audioop for simple resampling
            # For production, consider using a more sophisticated resampling library
            resampled = audioop.ratecv(
                audio_data,      # Input audio
                2,               # Sample width (16-bit)
                1,               # Channels (mono)
                from_rate,       # Input rate
                to_rate,         # Output rate
                None            # State (for streaming)
            )[0]
            
            return resampled
            
        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            return audio_data  # Return original if resampling fails
    
    async def _send_twilio_error(self, error_message: str):
        """Send error message to Twilio as audio"""
        try:
            # For simplicity, we'll just log the error
            # In production, you might want to use TTS to create error audio
            logger.error(f"Sending error to Twilio: {error_message}")
            
            # Optionally, you could generate TTS audio for the error message
            # and send it through the normal audio pipeline
            
        except Exception as e:
            logger.error(f"Error sending Twilio error: {e}")
    
    async def _cleanup(self):
        """Cleanup bridge resources"""
        try:
            self.active = False
            
            # Disconnect OpenAI client
            if self.openai_client:
                await self.openai_client.disconnect()
                self.openai_client = None
            
            # Close Twilio connection
            if self.twilio_websocket and not self.twilio_websocket.closed:
                await self.twilio_websocket.close()
            
            logger.info(f"Bridge cleanup completed for call {self.call_sid}")
            
        except Exception as e:
            logger.error(f"Error during bridge cleanup: {e}")
    
    def get_call_status(self) -> Dict[str, Any]:
        """Get current call status"""
        return {
            "active": self.active,
            "call_sid": self.call_sid,
            "from_number": self.from_number,
            "to_number": self.to_number,
            "openai_connected": self.openai_client.connected if self.openai_client else False,
            "twilio_connected": self.twilio_websocket is not None and not self.twilio_websocket.closed
        }


class TwilioBridgeServer:
    """
    WebSocket server for handling Twilio Media Stream connections
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self.active_bridges = {}  # call_sid -> TwilioOpenAIBridge
        
    async def start_server(self):
        """Start the Twilio bridge WebSocket server"""
        try:
            logger.info(f"Starting Twilio bridge server on {self.host}:{self.port}")
            
            self.server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
            
            logger.info(f"Twilio bridge server started on ws://{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start Twilio bridge server: {e}")
            raise
    
    async def _handle_connection(self, websocket, path):
        """Handle new WebSocket connection from Twilio"""
        try:
            logger.info(f"New connection from {websocket.remote_address} on path {path}")
            
            # Create new bridge instance
            bridge = TwilioOpenAIBridge()
            
            # Handle the connection
            await bridge.handle_twilio_connection(websocket, path)
            
        except Exception as e:
            logger.error(f"Error handling Twilio connection: {e}")
    
    async def stop_server(self):
        """Stop the Twilio bridge server"""
        try:
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            # Cleanup active bridges
            for bridge in self.active_bridges.values():
                await bridge._cleanup()
            
            self.active_bridges.clear()
            
            logger.info("Twilio bridge server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            "running": self.server is not None,
            "host": self.host,
            "port": self.port,
            "active_calls": len(self.active_bridges),
            "bridge_statuses": {
                call_sid: bridge.get_call_status() 
                for call_sid, bridge in self.active_bridges.items()
            }
        }