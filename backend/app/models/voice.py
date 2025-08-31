"""
Voice Processing Data Models
Pydantic models for voice-related API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VoiceTranscriptionRequest(BaseModel):
    """Request for audio transcription"""
    audio_format: Optional[str] = Field(None, description="Audio format (auto-detected from file)")
    language: Optional[str] = Field("ro", description="Expected language (ro, en)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "audio_format": "wav",
                "language": "ro"
            }
        }
    }


class VoiceTranscriptionResponse(BaseModel):
    """Response from audio transcription"""
    success: bool = Field(..., description="Whether transcription was successful")
    transcription: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    language: str = Field(..., description="Detected language")
    duration_ms: int = Field(..., description="Audio duration in milliseconds")
    timestamp: datetime = Field(..., description="Processing timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "transcription": "Bună ziua, aș vrea să mă programez pentru o consultație.",
                "confidence": 0.95,
                "language": "ro",
                "duration_ms": 3500,
                "timestamp": "2024-09-01T10:30:00"
            }
        }
    }


class VoiceConversationRequest(BaseModel):
    """Request for conversation processing"""
    text: str = Field(..., description="Input text to process")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="Previous conversation messages"
    )
    client_context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional client context"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Vreau să mă programez pentru o consultație generală marți la 14:00",
                "session_id": "sess_123",
                "conversation_history": [
                    {"role": "assistant", "content": "Bună ziua! Cu ce vă pot ajuta?"},
                    {"role": "user", "content": "Salut, vreau o programare"}
                ],
                "client_context": {
                    "caller_phone": "0721123456"
                }
            }
        }
    }


class VoiceConversationResponse(BaseModel):
    """Response from conversation processing"""
    success: bool = Field(..., description="Whether processing was successful")
    response: str = Field(..., description="Generated response text")
    action: Optional[str] = Field(None, description="Action to take (book_appointment, schedule_callback, etc.)")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Data for the action")
    conversation_state: str = Field(..., description="Current conversation state")
    confidence: float = Field(..., description="Response confidence (0.0-1.0)")
    timestamp: datetime = Field(..., description="Processing timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "response": "Perfect! Am înregistrat programarea pentru marți la 14:00. Vă voi trimite o confirmare SMS.",
                "action": "book_appointment",
                "action_data": {
                    "service": "Consultație generală",
                    "date": "2024-09-03",
                    "time": "14:00",
                    "client_name": "Ion Popescu",
                    "client_phone": "0721123456"
                },
                "conversation_state": "completed",
                "confidence": 0.92,
                "timestamp": "2024-09-01T10:30:15"
            }
        }
    }


class VoiceProcessingStatus(BaseModel):
    """Voice processing service status"""
    service_available: bool = Field(..., description="Whether voice service is available")
    openai_configured: bool = Field(..., description="Whether OpenAI is configured")
    agent_status: str = Field(..., description="Current agent status")
    active_sessions: int = Field(..., description="Number of active voice sessions")
    total_calls_today: int = Field(..., description="Total calls processed today")
    success_rate: float = Field(..., description="Success rate percentage")
    last_activity: Optional[str] = Field(None, description="Last activity timestamp")
    capabilities: Dict[str, bool] = Field(..., description="Available capabilities")
    models: Dict[str, str] = Field(default_factory=dict, description="AI models in use")
    timestamp: datetime = Field(..., description="Status timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "service_available": True,
                "openai_configured": True,
                "agent_status": "active",
                "active_sessions": 2,
                "total_calls_today": 15,
                "success_rate": 85.5,
                "last_activity": "2024-09-01T10:25:00",
                "capabilities": {
                    "transcription": True,
                    "conversation": True,
                    "text_to_speech": True,
                    "real_time_processing": True
                },
                "models": {
                    "realtime": "gpt-4o-realtime-preview",
                    "whisper": "whisper-1",
                    "tts": "tts-1"
                },
                "timestamp": "2024-09-01T10:30:00"
            }
        }
    }


class VoiceHealthCheck(BaseModel):
    """Voice service health check result"""
    healthy: bool = Field(..., description="Overall health status")
    services: Dict[str, bool] = Field(..., description="Individual service status")
    issues: List[str] = Field(default_factory=list, description="Current issues")
    last_check: datetime = Field(..., description="Last health check timestamp")
    uptime_minutes: int = Field(..., description="Service uptime in minutes")
    performance_metrics: Dict[str, float] = Field(
        ..., 
        description="Performance metrics"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "healthy": True,
                "services": {
                    "openai": True,
                    "agent_manager": True,
                    "transcription": True,
                    "conversation": True,
                    "text_to_speech": True
                },
                "issues": [],
                "last_check": "2024-09-01T10:30:00",
                "uptime_minutes": 120,
                "performance_metrics": {
                    "total_calls": 15.0,
                    "success_rate": 85.5,
                    "average_response_time": 1.2,
                    "concurrent_sessions": 2.0
                }
            }
        }
    }


class VoiceSessionRequest(BaseModel):
    """Request to start/manage voice session"""
    caller_info: str = Field(..., description="Caller identification")
    session_type: Optional[str] = Field("booking", description="Type of session")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "caller_info": "Ion Popescu - 0721123456",
                "session_type": "booking",
                "context": {
                    "callback_number": "0721123456",
                    "preferred_language": "ro"
                }
            }
        }
    }


class VoiceSessionResponse(BaseModel):
    """Response from voice session operation"""
    success: bool = Field(..., description="Whether operation was successful")
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Current session status")
    timestamp: str = Field(..., description="Operation timestamp")
    message: str = Field(..., description="Status message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "session_id": "sess_123456",
                "status": "active",
                "timestamp": "2024-09-01T10:30:00",
                "message": "Voice session started successfully"
            }
        }
    }


# Enum for conversation states
class ConversationState(str, Enum):
    """Voice conversation states"""
    STARTING = "starting"
    ACTIVE = "active"
    COLLECTING_INFO = "collecting_info"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Enum for voice actions
class VoiceAction(str, Enum):
    """Voice processing actions"""
    CONTINUE_CONVERSATION = "continue_conversation"
    BOOK_APPOINTMENT = "book_appointment"
    SCHEDULE_CALLBACK = "schedule_callback"
    REQUEST_INFORMATION = "request_information"
    CONFIRM_BOOKING = "confirm_booking"
    CANCEL_BOOKING = "cancel_booking"
    TRANSFER_TO_HUMAN = "transfer_to_human"