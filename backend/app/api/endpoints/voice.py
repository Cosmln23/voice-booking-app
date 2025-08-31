"""
Voice Processing API Endpoints
Handles voice-related operations, transcription, and conversation processing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

from app.core.logging import get_logger
from app.services.openai_client import get_openai_voice_client
from app.services.agent_status_manager import get_agent_status_manager
from app.services.voice_guardrails import get_voice_guardrails_manager
from app.models.voice import (
    VoiceTranscriptionRequest, VoiceTranscriptionResponse,
    VoiceConversationRequest, VoiceConversationResponse,
    VoiceProcessingStatus, VoiceHealthCheck
)

logger = get_logger(__name__)
router = APIRouter()

@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file to transcribe (wav, mp3, m4a)")
):
    """
    Transcribe audio file to text using OpenAI Whisper
    """
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file (wav, mp3, m4a)"
            )
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Audio file is empty"
            )
        
        if len(audio_data) > 25 * 1024 * 1024:  # 25MB limit
            raise HTTPException(
                status_code=400,
                detail="Audio file too large (max 25MB)"
            )
        
        # Get OpenAI client and transcribe
        openai_client = get_openai_voice_client()
        transcription = await openai_client.transcribe_audio(audio_data)
        
        if transcription is None:
            raise HTTPException(
                status_code=503,
                detail="Voice transcription service unavailable"
            )
        
        logger.info(f"Audio transcription completed: {len(audio_data)} bytes -> {len(transcription)} chars")
        
        return VoiceTranscriptionResponse(
            success=True,
            transcription=transcription,
            confidence=0.95,  # Mock confidence score
            language="ro",
            duration_ms=len(audio_data) // 16,  # Mock duration calculation
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice transcription error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/conversation", response_model=VoiceConversationResponse)
async def process_conversation(request: VoiceConversationRequest):
    """
    Process conversation text and generate intelligent response for booking
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text input is required"
            )
        
        # Get services
        openai_client = get_openai_voice_client()
        agent_manager = get_agent_status_manager()
        guardrails_manager = get_voice_guardrails_manager()
        
        # Validate input with guardrails
        validation_result = await guardrails_manager.validate_input(
            text=request.text,
            session_id=request.session_id or "anonymous",
            user_context=request.client_context
        )
        
        if not validation_result["valid"]:
            logger.warning(f"Input validation failed: {validation_result['violations']}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Input validation failed",
                    "violations": validation_result["violations"],
                    "risk_score": validation_result["risk_score"]
                }
            )
        
        # Use sanitized text for processing
        sanitized_text = validation_result["sanitized_text"]
        
        # Process the conversation
        result = await openai_client.process_conversation(
            text=sanitized_text,
            conversation_history=request.conversation_history or []
        )
        
        # Validate response with guardrails
        response_validation = await guardrails_manager.validate_conversation_response(
            response_text=result["response"],
            context={"session_id": request.session_id}
        )
        
        if not response_validation["valid"]:
            logger.error(f"Response validation failed: {response_validation['violations']}")
            return VoiceConversationResponse(
                success=False,
                response="Ne pare rău, nu pot procesa această solicitare în siguranță.",
                action=None,
                action_data=None,
                conversation_state="error",
                confidence=0.0,
                timestamp=datetime.now()
            )
        
        # Use sanitized response
        final_response = response_validation["sanitized_response"] or result["response"]
        
        # Log conversation activity
        await agent_manager.log_activity(
            activity_type="VOICE_PROCESSING",
            message=f"Conversație procesată: {request.text[:50]}...",
            client_info=request.session_id,
            details={
                "input_text": request.text,
                "response_action": result.get("action"),
                "session_id": request.session_id
            }
        )
        
        # If this is a booking action, handle it
        if result.get("action") == "book_appointment" and result.get("data"):
            booking_data = result["data"]
            logger.info(f"Booking request detected: {booking_data}")
            
            # In production, this would create the actual appointment
            # For now, just log it
            await agent_manager.log_activity(
                activity_type="BOOKING_SUCCESS",
                message=f"Programare vocală: {booking_data.get('service', 'N/A')}",
                client_info=booking_data.get('client_name'),
                details=booking_data
            )
        
        return VoiceConversationResponse(
            success=True,
            response=final_response,
            action=result.get("action"),
            action_data=result.get("data"),
            conversation_state="active" if not result.get("action") else "completed",
            confidence=0.9 if response_validation["valid"] else 0.7,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Conversation processing failed: {str(e)}"
        )


@router.post("/text-to-speech")
async def generate_speech(
    text: str,
    voice: Optional[str] = "alloy",
    speed: Optional[float] = 1.0
):
    """
    Convert text to speech using OpenAI TTS
    """
    try:
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text input is required"
            )
        
        if len(text) > 4096:
            raise HTTPException(
                status_code=400,
                detail="Text too long (max 4096 characters)"
            )
        
        # Validate voice parameter
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if voice not in valid_voices:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid voice. Must be one of: {', '.join(valid_voices)}"
            )
        
        # Get OpenAI client and generate speech
        openai_client = get_openai_voice_client()
        audio_data = await openai_client.text_to_speech(text)
        
        if audio_data is None:
            raise HTTPException(
                status_code=503,
                detail="Text-to-speech service unavailable"
            )
        
        logger.info(f"TTS generation completed: {len(text)} chars -> {len(audio_data)} bytes")
        
        from fastapi.responses import Response
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Speech generation failed: {str(e)}"
        )


@router.get("/status", response_model=VoiceProcessingStatus)
async def get_voice_status():
    """
    Get voice processing service status and configuration
    """
    try:
        openai_client = get_openai_voice_client()
        agent_manager = get_agent_status_manager()
        
        # Get service status
        openai_status = openai_client.get_service_status()
        agent_status = agent_manager.get_status_info()
        
        return VoiceProcessingStatus(
            service_available=openai_status["available"],
            openai_configured=openai_status["available"],
            agent_status=agent_status["status"],
            active_sessions=agent_status["active_sessions"],
            total_calls_today=agent_status["total_calls"],
            success_rate=agent_status["success_rate"],
            last_activity=agent_status["last_activity"],
            capabilities={
                "transcription": openai_status["available"],
                "conversation": openai_status["available"],
                "text_to_speech": openai_status["available"],
                "real_time_processing": True
            },
            models=openai_status.get("models", {}),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Voice status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get voice status: {str(e)}"
        )


@router.get("/health", response_model=VoiceHealthCheck)
async def voice_health_check():
    """
    Perform comprehensive health check of voice processing services
    """
    try:
        openai_client = get_openai_voice_client()
        agent_manager = get_agent_status_manager()
        
        # Perform health checks
        openai_health = await openai_client.health_check()
        agent_health = await agent_manager.health_check()
        
        # Determine overall health
        overall_healthy = openai_health["healthy"] and agent_health["healthy"]
        
        # Collect all issues
        issues = openai_health.get("issues", []) + agent_health.get("issues", [])
        
        return VoiceHealthCheck(
            healthy=overall_healthy,
            services={
                "openai": openai_health["healthy"],
                "agent_manager": agent_health["healthy"],
                "transcription": openai_health.get("services", {}).get("transcription", False),
                "conversation": openai_health.get("services", {}).get("conversation", False),
                "text_to_speech": openai_health.get("services", {}).get("text_to_speech", False)
            },
            issues=issues,
            last_check=datetime.now(),
            uptime_minutes=agent_health.get("uptime_minutes", 0),
            performance_metrics={
                "total_calls": agent_health.get("total_calls", 0),
                "success_rate": agent_health.get("success_rate", 0.0),
                "average_response_time": 1.2,  # Mock metric
                "concurrent_sessions": agent_health.get("active_sessions", 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Voice health check error: {e}", exc_info=True)
        return VoiceHealthCheck(
            healthy=False,
            services={
                "openai": False,
                "agent_manager": False,
                "transcription": False,
                "conversation": False,
                "text_to_speech": False
            },
            issues=[f"Health check failed: {str(e)}"],
            last_check=datetime.now(),
            uptime_minutes=0,
            performance_metrics={
                "total_calls": 0,
                "success_rate": 0.0,
                "average_response_time": 0.0,
                "concurrent_sessions": 0
            }
        )


@router.post("/session/start")
async def start_voice_session(
    caller_info: str,
    session_id: Optional[str] = None
):
    """
    Start a new voice processing session
    """
    try:
        if not caller_info:
            raise HTTPException(
                status_code=400,
                detail="Caller information is required"
            )
        
        # Generate session ID if not provided
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        # Get agent manager and start session
        agent_manager = get_agent_status_manager()
        success = await agent_manager.start_call(caller_info, session_id)
        
        if not success:
            raise HTTPException(
                status_code=503,
                detail="Voice agent not available to start session"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "message": "Voice session started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start voice session error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start voice session: {str(e)}"
        )


@router.post("/session/end")
async def end_voice_session(
    session_id: str,
    success: bool = True,
    booking_data: Optional[Dict[str, Any]] = None
):
    """
    End a voice processing session
    """
    try:
        if not session_id:
            raise HTTPException(
                status_code=400,
                detail="Session ID is required"
            )
        
        # Get agent manager and end session
        agent_manager = get_agent_status_manager()
        result = await agent_manager.end_call(session_id, success, booking_data)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Session not found or already ended"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "ended",
            "timestamp": datetime.now().isoformat(),
            "message": "Voice session ended successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"End voice session error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end voice session: {str(e)}"
        )