"""
OpenAI Realtime API Client
Handles real-time voice interactions with function calling for appointment booking
"""

import asyncio
import json
import websockets
import base64
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import os

from app.core.config import settings
from app.core.logging import get_logger
from app.voice.functions.registry import (
    get_openai_tools_definition, 
    execute_voice_function,
    VOICE_FUNCTION_REGISTRY
)
from app.voice.functions.auth import authenticate_voice_session, end_voice_session
from app.voice.functions.errors import VoiceError, VoiceErrorType, handle_voice_error

logger = get_logger(__name__)


class OpenAIRealtimeClient:
    """
    OpenAI Realtime API Client for voice booking
    Handles WebSocket connection, function calling, and conversation flow
    """
    
    def __init__(self, supabase_client):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_realtime_model
        self.supabase_client = supabase_client
        
        # Connection state
        self.websocket = None
        self.connected = False
        self.session_id = None
        self.user_context = None
        
        # Conversation state
        self.conversation_state = "greeting"  # greeting, service_selection, availability, booking, confirmation
        self.booking_context = {}
        
        # Function calling
        self.pending_function_calls = {}
        
        logger.info("OpenAI Realtime client initialized")
    
    async def connect(self, twilio_call_sid: str = None, caller_number: str = None, called_number: str = None):
        """
        Connect to OpenAI Realtime API and setup session
        
        Args:
            twilio_call_sid: Twilio Call SID for tracking
            caller_number: Customer phone number
            called_number: Business phone number
        """
        try:
            logger.info(f"Connecting to OpenAI Realtime API, call_sid={twilio_call_sid}")
            
            # Authenticate voice session
            auth_result = await authenticate_voice_session(
                twilio_call_sid=twilio_call_sid,
                caller_number=caller_number,
                called_number=called_number,
                supabase_client=self.supabase_client
            )
            
            self.session_id = auth_result["session_id"]
            self.user_context = auth_result["user_context"]
            
            # Connect to OpenAI WebSocket
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            uri = "wss://api.openai.com/v1/realtime"
            
            self.websocket = await websockets.connect(uri, extra_headers=headers)
            self.connected = True
            
            # Send session configuration
            await self._configure_session()
            
            logger.info(f"OpenAI Realtime connection established, session={self.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Realtime: {e}", exc_info=True)
            raise VoiceError(
                message=f"OpenAI connection failed: {str(e)}",
                error_type=VoiceErrorType.EXTERNAL_SERVICE_ERROR
            )
    
    async def _configure_session(self):
        """Configure OpenAI session with Romanian booking assistant"""
        
        # Get function definitions for OpenAI
        tools = get_openai_tools_definition()
        
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": self._get_romanian_instructions(),
                "voice": "nova",  # Clear voice for Romanian
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 800
                },
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.7,
                "max_response_output_tokens": 4096
            }
        }
        
        await self.websocket.send(json.dumps(session_config))
        logger.info("OpenAI session configured with Romanian booking assistant")
    
    def _get_romanian_instructions(self) -> str:
        """Get Romanian conversation instructions for OpenAI"""
        business_name = self.user_context.get("business_name", "Salon Voice Booking")
        
        return f"""
Ești asistentul vocal al {business_name}, un salon de înfrumusețare din România. 
Vorbești DOAR în română și ajuți clienții să facă programări prin telefon.

PERSONALITATEA TA:
- Prietenoasă și profesională
- Vorbești natural, ca un om real
- Ești răbdătoare și înțelegătoare
- Folosești "dumneavoastră" pentru respect

FLUXUL DE PROGRAMARE:
1. SALUT: "Bună ziua! {business_name}, cu ce vă pot ajuta?"
2. SERVICII: Întrebi ce serviciu dorește (folosește get_available_services)
3. DISPONIBILITATE: Verifici când dorește programarea (folosește check_appointment_availability)
4. CLIENT: Ceri numele și telefonul (folosește find_existing_client dacă este cazul)
5. CONFIRMARE: Repeți detaliile și confirmi programarea (folosește create_voice_appointment)

REGULI IMPORTANTE:
- Folosește ÎNTOTDEAUNA funcțiile disponibile pentru a verifica servicii și disponibilitate
- NU inventezi servicii sau ore disponibile
- Ceri confirmarea finală înainte de a crea programarea
- La erori, oferi alternative și rămai pozitivă
- Dacă nu înțelegi, ceri să repete mai clar

EXEMPLE RĂSPUNSURI:
- "Ce serviciu doriți? Avem tuns, bărbierit, styling..."
- "Să verific disponibilitatea pentru data aceea..."
- "Perfect! Deci programez pe [nume] pentru [serviciu] pe [dată] la [oră]. Confirmați?"
- "Îmi pare rău, ora aceea este ocupată. Vă pot propune altă oră?"

Începe întotdeauna cu salutul și întreabă cum poți ajuta.
"""
    
    async def handle_audio_input(self, audio_data: bytes):
        """
        Handle incoming audio from Twilio
        
        Args:
            audio_data: Raw audio bytes from Twilio
        """
        try:
            if not self.connected:
                logger.warning("Attempting to send audio while not connected")
                return
            
            # Convert audio to base64 for OpenAI
            audio_b64 = base64.b64encode(audio_data).decode()
            
            # Send audio chunk to OpenAI
            audio_message = {
                "type": "input_audio_buffer.append",
                "audio": audio_b64
            }
            
            await self.websocket.send(json.dumps(audio_message))
            
        except Exception as e:
            logger.error(f"Error handling audio input: {e}")
    
    async def commit_audio_input(self):
        """Commit audio input and trigger processing"""
        try:
            commit_message = {
                "type": "input_audio_buffer.commit"
            }
            await self.websocket.send(json.dumps(commit_message))
            
        except Exception as e:
            logger.error(f"Error committing audio: {e}")
    
    async def listen_for_responses(self, audio_callback: Callable[[bytes], None]):
        """
        Listen for OpenAI responses and handle function calls
        
        Args:
            audio_callback: Callback function to handle audio output
        """
        try:
            while self.connected:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                await self._handle_openai_message(data, audio_callback)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("OpenAI connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Error listening for responses: {e}")
            self.connected = False
    
    async def _handle_openai_message(self, data: Dict[str, Any], audio_callback: Callable[[bytes], None]):
        """Handle different types of messages from OpenAI"""
        
        message_type = data.get("type")
        
        if message_type == "response.audio.delta":
            # Audio response chunk
            audio_b64 = data.get("delta", "")
            if audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
                audio_callback(audio_bytes)
        
        elif message_type == "response.function_call_delta":
            # Function call in progress
            call_id = data.get("call_id")
            name = data.get("name", "")
            arguments_delta = data.get("arguments", "")
            
            if call_id not in self.pending_function_calls:
                self.pending_function_calls[call_id] = {
                    "name": name,
                    "arguments": ""
                }
            
            self.pending_function_calls[call_id]["arguments"] += arguments_delta
        
        elif message_type == "response.function_call_done":
            # Function call complete - execute it
            call_id = data.get("call_id")
            
            if call_id in self.pending_function_calls:
                await self._execute_function_call(call_id)
        
        elif message_type == "response.done":
            # Response complete
            logger.info("OpenAI response completed")
        
        elif message_type == "error":
            # Handle OpenAI errors
            error_data = data.get("error", {})
            logger.error(f"OpenAI error: {error_data}")
        
        elif message_type == "session.created":
            logger.info("OpenAI session created successfully")
        
        else:
            logger.debug(f"Unhandled OpenAI message type: {message_type}")
    
    async def _execute_function_call(self, call_id: str):
        """Execute a function call and return result to OpenAI"""
        try:
            function_data = self.pending_function_calls[call_id]
            function_name = function_data["name"]
            arguments_str = function_data["arguments"]
            
            logger.info(f"Executing function call: {function_name}")
            
            # Parse function arguments
            try:
                function_args = json.loads(arguments_str) if arguments_str else {}
            except json.JSONDecodeError as e:
                logger.error(f"Invalid function arguments: {arguments_str}")
                function_args = {}
            
            # Execute the function
            result = await execute_voice_function(
                function_name=function_name,
                function_args=function_args,
                supabase_client=self.supabase_client,
                user_context=self.user_context
            )
            
            # Update booking context based on function result
            await self._update_booking_context(function_name, function_args, result)
            
            # Send result back to OpenAI
            function_result = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result, ensure_ascii=False)
                }
            }
            
            await self.websocket.send(json.dumps(function_result))
            
            # Trigger response generation
            generate_response = {
                "type": "response.create"
            }
            
            await self.websocket.send(json.dumps(generate_response))
            
            # Clean up
            del self.pending_function_calls[call_id]
            
            logger.info(f"Function {function_name} executed successfully")
            
        except Exception as e:
            logger.error(f"Error executing function call {call_id}: {e}")
            
            # Send error to OpenAI
            error_result = {
                "type": "conversation.item.create", 
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps({
                        "success": False,
                        "error": str(e),
                        "voice_response": "A apărut o problemă tehnică. Vă rog să încercați din nou."
                    }, ensure_ascii=False)
                }
            }
            
            await self.websocket.send(json.dumps(error_result))
    
    async def _update_booking_context(self, function_name: str, args: Dict, result: Dict):
        """Update conversation context based on function results"""
        
        if function_name == "get_available_services" and result.get("success"):
            self.booking_context["available_services"] = result.get("services", [])
        
        elif function_name == "find_existing_client" and result.get("success"):
            client_data = result.get("client")
            if client_data:
                self.booking_context["client"] = client_data
        
        elif function_name == "check_appointment_availability" and result.get("success"):
            self.booking_context["checked_date"] = args.get("date_requested")
            self.booking_context["available_slots"] = result.get("available_slots", [])
        
        elif function_name == "create_voice_appointment" and result.get("success"):
            self.booking_context["appointment"] = result.get("appointment")
            self.conversation_state = "completed"
    
    async def send_text_message(self, text: str):
        """Send text message to OpenAI (for testing)"""
        try:
            message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": text}]
                }
            }
            
            await self.websocket.send(json.dumps(message))
            
            # Trigger response
            response_msg = {"type": "response.create"}
            await self.websocket.send(json.dumps(response_msg))
            
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
    
    async def disconnect(self):
        """Disconnect from OpenAI and cleanup"""
        try:
            if self.connected and self.websocket:
                await self.websocket.close()
                self.connected = False
            
            # End voice session
            if self.session_id:
                session_summary = {
                    "appointments_created": 1 if self.conversation_state == "completed" else 0,
                    "duration_seconds": (datetime.now() - datetime.fromisoformat(self.user_context.get("session_start", datetime.now().isoformat()))).total_seconds(),
                    "conversation_state": self.conversation_state
                }
                
                await end_voice_session(
                    self.session_id, 
                    self.supabase_client,
                    session_summary
                )
            
            logger.info("OpenAI Realtime client disconnected")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def get_booking_context(self) -> Dict[str, Any]:
        """Get current booking context"""
        return {
            "conversation_state": self.conversation_state,
            "booking_context": self.booking_context,
            "session_id": self.session_id
        }