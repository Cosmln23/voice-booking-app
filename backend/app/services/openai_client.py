"""
OpenAI Client Service for Voice Processing
Handles OpenAI API interactions for voice booking system
"""

import asyncio
import json
from typing import Optional, Dict, List, Any
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIVoiceClient:
    """OpenAI client for voice processing and conversation management"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o-realtime-preview"
        self.voice_model = "whisper-1"
        self.tts_model = "tts-1"
        self.is_available = bool(self.api_key)
        
        # Voice configuration
        self.voice_config = {
            "voice": "alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            "response_format": "mp3",
            "speed": 1.0
        }
        
        # Conversation context for booking
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build system prompt for voice booking agent"""
        return """Ești un asistent virtual pentru programarea de servicii în română.

INSTRUCȚIUNI:
- Vorbește doar în română
- Fii prietenos și profesional
- Colectează toate informațiile necesare pentru programare: nume, telefon, serviciu, data/ora preferată
- Confirmă toate detaliile înainte de finalizare
- Pentru servicii disponibile: Consultație generală (60 min, 150 RON), Tratament specializat (90 min, 250 RON), Control periodic (30 min, 100 RON)
- Program disponibil: Luni-Vineri 9:00-18:00, Sâmbătă 9:00-14:00
- Dacă clientul nu poate oferi informații complete, programează un callback

FORMAT RĂSPUNS:
- Pentru colectare info: conversație naturală
- Pentru finalizare: JSON cu { "action": "book_appointment", "data": {...} }
- Pentru callback: JSON cu { "action": "schedule_callback", "data": {...} }
- Pentru informații: conversație naturală

EXEMPLE PROGRAMĂRI:
✓ "Vreau să mă programez pentru o consultație generală marți la 14:00"
✓ "Am nevoie de un tratament specializat, sunt disponibil vinerea după-amiaza"
✗ Nu programa fără toate detaliile necesare"""

    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using Whisper API"""
        if not self.is_available:
            logger.warning("OpenAI API key not configured")
            return None
            
        try:
            # In production, this would call OpenAI Whisper API
            # For now, return mock transcription
            logger.info(f"Mock transcribing audio: {len(audio_data)} bytes")
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            return "Bună ziua, aș vrea să mă programez pentru o consultație."
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}", exc_info=True)
            return None
    
    async def process_conversation(self, text: str, conversation_history: List[Dict] = None) -> Dict:
        """Process conversation text and generate response"""
        if not self.is_available:
            return {
                "response": "Serviciul vocal nu este disponibil momentan. Vă rugăm să apelați direct.",
                "action": None
            }
        
        try:
            # Build conversation context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": text})
            
            # In production, this would call OpenAI GPT API
            # For now, return mock response based on text content
            logger.info(f"Processing conversation: {text}")
            
            # Simulate API call delay
            await asyncio.sleep(0.2)
            
            # Mock intelligent response based on content
            response = self._generate_mock_response(text, conversation_history or [])
            
            return response
            
        except Exception as e:
            logger.error(f"Conversation processing failed: {e}", exc_info=True)
            return {
                "response": "Ne pare rău, am întâmpinat o problemă tehnică. Vă rugăm să reîncercați.",
                "action": None
            }
    
    def _generate_mock_response(self, text: str, history: List[Dict]) -> Dict:
        """Generate mock intelligent response for testing"""
        text_lower = text.lower()
        
        # Check if this looks like a complete booking request
        has_service = any(word in text_lower for word in ["consultație", "tratament", "control"])
        has_time = any(word in text_lower for word in ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "dimineața", "după-amiaza", "ora"])
        
        # If user is providing booking details
        if has_service or has_time:
            # Check if we have enough info from conversation history
            context = " ".join([msg.get("content", "") for msg in history if msg.get("role") == "user"])
            full_context = context + " " + text
            
            has_name = any(word in full_context.lower() for word in ["numele", "mă numesc", "sunt"])
            has_phone = any(char.isdigit() for char in full_context) and len([c for c in full_context if c.isdigit()]) >= 9
            
            if has_service and has_time and has_name and has_phone:
                # Complete booking
                return {
                    "response": "Perfect! Am înregistrat programarea dumneavoastră. Vă voi trimite o confirmare SMS cu detaliile. Vă mulțumesc!",
                    "action": "book_appointment",
                    "data": {
                        "service": "Consultație generală" if "consultație" in text_lower else "Tratament specializat",
                        "date": "2024-09-05",
                        "time": "14:00",
                        "client_name": "Ion Popescu",
                        "client_phone": "0721123456",
                        "notes": f"Programare vocală: {text[:100]}..."
                    }
                }
            else:
                # Need more info
                missing = []
                if not has_name:
                    missing.append("numele")
                if not has_phone:
                    missing.append("numărul de telefon")
                if not has_service:
                    missing.append("tipul de serviciu")
                if not has_time:
                    missing.append("data și ora preferată")
                
                return {
                    "response": f"Pentru a finaliza programarea, mai am nevoie de: {', '.join(missing)}. Mă puteți ajuta cu aceste informații?",
                    "action": None
                }
        
        # Greeting or general inquiry
        elif any(word in text_lower for word in ["bună", "salut", "alo", "programare", "program"]):
            return {
                "response": "Bună ziua! Sunt asistentul virtual pentru programări. Vă pot ajuta să vă programați pentru: Consultație generală (150 RON), Tratament specializat (250 RON) sau Control periodic (100 RON). Cu ce vă pot ajuta?",
                "action": None
            }
        
        # Default response
        else:
            return {
                "response": "Vă înțeleg. Pentru a vă programa, am nevoie de numele dumneavoastră, numărul de telefon, tipul de serviciu și data/ora preferată. Începem?",
                "action": None
            }
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using OpenAI TTS"""
        if not self.is_available:
            logger.warning("OpenAI API key not configured for TTS")
            return None
            
        try:
            # In production, this would call OpenAI TTS API
            logger.info(f"Mock TTS generation for: {text[:50]}...")
            
            # Simulate API call delay
            await asyncio.sleep(0.3)
            
            # Return mock audio bytes
            return b"mock_audio_data_" + text.encode()[:100]
            
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}", exc_info=True)
            return None
    
    def get_service_status(self) -> Dict:
        """Get OpenAI service status and configuration"""
        return {
            "available": self.is_available,
            "model": self.model if self.is_available else None,
            "voice_model": self.voice_model if self.is_available else None,
            "tts_model": self.tts_model if self.is_available else None,
            "voice_config": self.voice_config if self.is_available else None,
            "configuration_status": "API key configured" if self.is_available else "API key not configured"
        }
    
    async def health_check(self) -> Dict:
        """Perform health check on OpenAI services"""
        try:
            if not self.is_available:
                return {
                    "healthy": False,
                    "issues": ["OpenAI API key not configured"],
                    "services": {
                        "transcription": False,
                        "conversation": False,
                        "text_to_speech": False
                    }
                }
            
            # In production, this would test actual API connectivity
            # For now, return mock healthy status
            await asyncio.sleep(0.1)
            
            return {
                "healthy": True,
                "issues": [],
                "services": {
                    "transcription": True,
                    "conversation": True,
                    "text_to_speech": True
                },
                "models": {
                    "realtime": self.model,
                    "whisper": self.voice_model,
                    "tts": self.tts_model
                }
            }
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}", exc_info=True)
            return {
                "healthy": False,
                "issues": [f"Health check failed: {str(e)}"],
                "services": {
                    "transcription": False,
                    "conversation": False,
                    "text_to_speech": False
                }
            }


# Global OpenAI client instance
openai_voice_client = OpenAIVoiceClient()


def get_openai_voice_client() -> OpenAIVoiceClient:
    """Get the global OpenAI voice client instance"""
    return openai_voice_client