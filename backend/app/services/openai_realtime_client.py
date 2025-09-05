"""
OpenAI Realtime API Client for Voice Processing
Handles WebSocket connection to OpenAI Realtime API for real-time voice interactions
"""

import asyncio
import json
import base64
import websockets
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from datetime import datetime
import uuid
import aiohttp

from app.core.config import settings
from app.core.logging import get_logger
from app.voice.functions.registry import get_openai_tools_definition, execute_voice_function

logger = get_logger(__name__)


class OpenAIRealtimeClient:
    """OpenAI Realtime API client for voice processing"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.realtime_url = settings.openai_realtime_url
        self.model = settings.openai_realtime_model
        self.voice = settings.openai_voice
        self.is_available = bool(self.api_key)
        
        # Connection state
        self.websocket = None
        self.session_id = None
        self.conversation_id = None
        
        # Event handlers
        self.event_handlers = {}
        self.response_handlers = {}
        
        # Romanian conversation system prompt
        self.system_instructions = self._build_romanian_system_instructions()
        
        # Session configuration
        self.session_config = {
            "modalities": ["text", "audio"],
            "instructions": self.system_instructions,
            "voice": self.voice,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            },
            "tools": get_openai_tools_definition(),
            "tool_choice": "auto",
            "temperature": 0.8,
            "max_response_output_tokens": 4096
        }
    
    def _build_romanian_system_instructions(self) -> str:
        """Build comprehensive Romanian system instructions for appointment booking"""
        return """Ești un asistent vocal AI inteligent pentru un salon de frumusețe care vorbește EXCLUSIV în română. 
        
PERSONALITATEA TA:
- Fii prietenos, profesional și empatic
- Vorbește natural, nu robotic
- Folosește expresii românești familiare
- Asigură-te că clientul se simte bine venit și înțeles

REGULI FUNDAMENTALE:
- ÎNTOTDEAUNA vorbește în română
- NU folosi niciodată alte limbi în conversații
- Fii răbdător cu clienții mai în vârstă sau mai puțin tehnici
- Repetă informațiile dacă clientul nu înțelege

SERVICII DISPONIBILE:
1. Tuns clasic (45 min, 80 RON)
2. Tuns + Spălat (60 min, 100 RON)
3. Vopsit păr (120 min, 200 RON)
4. Coafat pentru evenimente (90 min, 150 RON)
5. Tuns + Barba (75 min, 120 RON)
6. Tratamente păr (90 min, 180 RON)

PROGRAM SALON:
- Luni - Vineri: 09:00 - 20:00
- Sâmbătă: 09:00 - 18:00
- Duminică: 11:00 - 17:00

FLUXUL CONVERSAȚIEI:
1. SALUTUL: Salută prietenos și întreabă cum poți ajuta
2. SERVICIUL: Află ce serviciu dorește clientul
3. DATA/ORA: Verifică disponibilitatea pentru data/ora dorită
4. DATELE CLIENTULUI: Colectează nume complet și numărul de telefon
5. CONFIRMARE: Repetă toate detaliile și confirmă programarea
6. ÎNCHIDERE: Mulțumește și spune că vor primi confirmare SMS

FUNCȚII DISPONIBILE:
- get_available_services: pentru a afla serviciile disponibile
- check_appointment_availability: pentru a verifica disponibilitatea
- find_existing_client: pentru a căuta clienți existenți
- create_voice_appointment: pentru a crea programarea
- confirm_voice_appointment: pentru a confirma detaliile finale

INSTRUCȚIUNI SPECIALE:
- Dacă clientul pare nedecis, oferă recomandări pe baza nevoilor lor
- Pentru clienți noi, explică pe scurt serviciile disponibile
- Pentru clienți recurenți, referă-te la istoricul lor dacă este disponibil
- Dacă nu poți programa pentru data dorită, oferă alternative apropiate
- În caz de probleme tehnice, propune rechemarea sau vizita directă

EXEMPLE DE RĂSPUNSURI:
"Bună ziua și bun venit la salonul nostru! Cu ce vă pot ajuta astăzi?"
"Îmi pare rău, dar la ora respectivă suntem ocupați. V-ar conveni cu o oră mai târziu?"
"Perfect! Am notat programarea pentru dumneavoastră. Veți primi un SMS cu confirmarea."

Fii întotdeauna util, precis și orientat către soluții!"""
    
    async def connect(self) -> bool:
        """Connect to OpenAI Realtime API via WebSocket"""
        if not self.is_available:
            logger.warning("OpenAI API key not configured")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            logger.info("Connecting to OpenAI Realtime API...")
            
            self.websocket = await websockets.connect(
                f"{self.realtime_url}?model={self.model}",
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            # Generate session ID
            self.session_id = str(uuid.uuid4())
            self.conversation_id = str(uuid.uuid4())
            
            logger.info(f"Connected to OpenAI Realtime API, session: {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Realtime API: {e}")
            return False
    
    async def configure_session(self, supabase_client=None, user_context: Dict = None) -> bool:
        """Configure the realtime session with tools and settings"""
        if not self.websocket:
            return False
        
        try:
            # Store context for function execution
            self.supabase_client = supabase_client
            self.user_context = user_context or {}
            
            # Send session update
            session_update = {
                "type": "session.update",
                "session": self.session_config
            }
            
            await self.websocket.send(json.dumps(session_update))
            logger.info("Session configured with Romanian instructions and tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure session: {e}")
            return False
    
    async def start_conversation(self) -> bool:
        """Start a new conversation"""
        if not self.websocket:
            return False
        
        try:
            # Create conversation
            conversation_create = {
                "type": "conversation.item.create",
                "item": {
                    "id": f"msg_{uuid.uuid4()}",
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Bună ziua, sunt gata să încep conversația."
                        }
                    ]
                }
            }
            
            await self.websocket.send(json.dumps(conversation_create))
            
            # Trigger response creation
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Salută clientul în română și întreabă cum îl poți ajuta cu programarea."
                }
            }
            
            await self.websocket.send(json.dumps(response_create))
            logger.info("Conversation started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            return False
    
    async def send_audio_chunk(self, audio_data: bytes) -> bool:
        """Send audio chunk to realtime API"""
        if not self.websocket:
            return False
        
        try:
            # Convert audio to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Send audio append event
            audio_append = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            
            await self.websocket.send(json.dumps(audio_append))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send audio chunk: {e}")
            return False
    
    async def send_text_message(self, text: str) -> bool:
        """Send text message to the conversation"""
        if not self.websocket:
            return False
        
        try:
            # Create conversation item
            conversation_item = {
                "type": "conversation.item.create",
                "item": {
                    "id": f"msg_{uuid.uuid4()}",
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            }
            
            await self.websocket.send(json.dumps(conversation_item))
            
            # Create response
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            
            await self.websocket.send(json.dumps(response_create))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
            return False
    
    async def commit_audio_buffer(self) -> bool:
        """Commit the current audio buffer and trigger response"""
        if not self.websocket:
            return False
        
        try:
            # Commit audio buffer
            commit_buffer = {
                "type": "input_audio_buffer.commit"
            }
            
            await self.websocket.send(json.dumps(commit_buffer))
            
            # Create response
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            
            await self.websocket.send(json.dumps(response_create))
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit audio buffer: {e}")
            return False
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler for specific event types"""
        self.event_handlers[event_type] = handler
    
    async def listen_for_events(self) -> AsyncGenerator[Dict, None]:
        """Listen for events from the realtime API"""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                try:
                    event = json.loads(message)
                    event_type = event.get("type")
                    
                    logger.debug(f"Received event: {event_type}")
                    
                    # Handle function calls
                    if event_type == "response.function_call_arguments.done":
                        await self._handle_function_call(event)
                    
                    # Call registered handlers
                    if event_type in self.event_handlers:
                        await self.event_handlers[event_type](event)
                    
                    yield event
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket message: {e}")
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error listening for events: {e}")
    
    async def _handle_function_call(self, event: Dict) -> None:
        """Handle function call from OpenAI and execute backend functions"""
        try:
            call_id = event.get("call_id")
            function_name = event.get("name")
            arguments_str = event.get("arguments", "{}")
            
            # Parse function arguments
            try:
                function_args = json.loads(arguments_str)
            except json.JSONDecodeError:
                function_args = {}
            
            logger.info(f"Executing function call: {function_name} with args: {function_args}")
            
            # Execute the function
            result = await execute_voice_function(
                function_name=function_name,
                function_args=function_args,
                supabase_client=self.supabase_client,
                user_context=self.user_context
            )
            
            # Send function call output back to OpenAI
            function_output = {
                "type": "conversation.item.create",
                "item": {
                    "id": f"func_result_{uuid.uuid4()}",
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result)
                }
            }
            
            await self.websocket.send(json.dumps(function_output))
            
            # Continue the response
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            
            await self.websocket.send(json.dumps(response_create))
            
        except Exception as e:
            logger.error(f"Error handling function call: {e}")
            
            # Send error response
            if 'call_id' in locals():
                error_output = {
                    "type": "conversation.item.create", 
                    "item": {
                        "id": f"func_error_{uuid.uuid4()}",
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps({
                            "success": False,
                            "error": str(e),
                            "voice_response": "Am întâmpinat o problemă tehnică. Vă rog să reîncercați."
                        })
                    }
                }
                await self.websocket.send(json.dumps(error_output))
    
    async def disconnect(self):
        """Disconnect from the realtime API"""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Disconnected from OpenAI Realtime API")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self.websocket = None
                self.session_id = None
                self.conversation_id = None


class RealtimeSessionManager:
    """Manages multiple realtime sessions for concurrent calls"""
    
    def __init__(self):
        self.sessions: Dict[str, OpenAIRealtimeClient] = {}
        self.session_metadata: Dict[str, Dict] = {}
    
    async def create_session(self, session_id: str, supabase_client=None, user_context: Dict = None) -> Optional[OpenAIRealtimeClient]:
        """Create a new realtime session"""
        try:
            client = OpenAIRealtimeClient()
            
            # Connect to OpenAI
            if not await client.connect():
                return None
            
            # Configure session
            if not await client.configure_session(supabase_client, user_context):
                await client.disconnect()
                return None
            
            # Store session
            self.sessions[session_id] = client
            self.session_metadata[session_id] = {
                "created_at": datetime.now(),
                "user_context": user_context or {},
                "status": "active"
            }
            
            logger.info(f"Created realtime session: {session_id}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return None
    
    async def get_session(self, session_id: str) -> Optional[OpenAIRealtimeClient]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    async def end_session(self, session_id: str):
        """End and cleanup a session"""
        if session_id in self.sessions:
            try:
                await self.sessions[session_id].disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting session {session_id}: {e}")
            
            del self.sessions[session_id]
            if session_id in self.session_metadata:
                del self.session_metadata[session_id]
            
            logger.info(f"Ended realtime session: {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.sessions.keys())
    
    async def cleanup_inactive_sessions(self, max_age_minutes: int = 30):
        """Cleanup sessions older than max_age_minutes"""
        now = datetime.now()
        to_cleanup = []
        
        for session_id, metadata in self.session_metadata.items():
            age_minutes = (now - metadata["created_at"]).seconds // 60
            if age_minutes > max_age_minutes:
                to_cleanup.append(session_id)
        
        for session_id in to_cleanup:
            await self.end_session(session_id)
            logger.info(f"Cleaned up inactive session: {session_id}")


# Global session manager
realtime_session_manager = RealtimeSessionManager()


def get_realtime_session_manager() -> RealtimeSessionManager:
    """Get the global realtime session manager"""
    return realtime_session_manager