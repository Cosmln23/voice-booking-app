"""
Twilio Voice Endpoints
Handles Twilio webhooks for voice calls and integrates with OpenAI Realtime API
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
from typing import Optional
import xml.etree.ElementTree as ET
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)
router = APIRouter()


def create_twiml_response(content: str) -> str:
    """Create TwiML XML response"""
    response = ET.Element("Response")
    say = ET.SubElement(response, "Say", voice="alice", language="ro-RO")
    say.text = content
    return ET.tostring(response, encoding="unicode")


def create_connect_stream_twiml(stream_url: str, call_sid: str, from_number: str, to_number: str) -> str:
    """Create TwiML to connect to Media Stream"""
    response = ET.Element("Response")
    
    # Initial greeting
    say = ET.SubElement(response, "Say", voice="alice", language="ro-RO")
    say.text = "Bună ziua! Salon Voice Booking. Un moment să vă conectez cu asistentul nostru vocal."
    
    # Connect to WebSocket stream
    connect = ET.SubElement(response, "Connect")
    stream = ET.SubElement(connect, "Stream", url=stream_url)
    
    # Add call parameters
    parameter_elements = [
        ("CallSid", call_sid),
        ("From", from_number),
        ("To", to_number)
    ]
    
    for name, value in parameter_elements:
        param = ET.SubElement(stream, "Parameter", name=name, value=value)
    
    return ET.tostring(response, encoding="unicode")


@router.post("/twilio/voice")
async def handle_incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...),
    Direction: str = Form(...),
    AccountSid: Optional[str] = Form(None),
    FromCity: Optional[str] = Form(None),
    FromCountry: Optional[str] = Form(None)
):
    """
    Handle incoming Twilio voice call
    Sets up Media Stream connection to OpenAI Realtime API
    """
    try:
        logger.info(f"Incoming call: {CallSid} from {From} to {To}, status: {CallStatus}")
        
        # Validate call is incoming and answered
        if Direction != "inbound":
            logger.warning(f"Ignoring non-inbound call: {Direction}")
            twiml = create_twiml_response("Ne pare rău, nu putem procesa acest apel.")
            return Response(content=twiml, media_type="application/xml")
        
        # Determine bridge WebSocket URL
        # In production, this should be your Railway deployment URL
        bridge_url = f"wss://{request.headers.get('host', 'localhost:8080')}/twilio/stream"
        
        # For Railway deployment, construct proper URL
        if "railway.app" in str(request.base_url):
            bridge_url = f"wss://{request.headers.get('host')}/twilio/stream"
        else:
            # Local development
            bridge_url = f"ws://localhost:8080/twilio/stream"
        
        # Create TwiML response to connect to Media Stream
        twiml = create_connect_stream_twiml(
            stream_url=bridge_url,
            call_sid=CallSid,
            from_number=From,
            to_number=To
        )
        
        logger.info(f"Connecting call {CallSid} to stream: {bridge_url}")
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}", exc_info=True)
        
        # Return error TwiML
        error_twiml = create_twiml_response(
            "Ne pare rău, a apărut o problemă tehnică. Vă rugăm să încercați din nou."
        )
        return Response(content=error_twiml, media_type="application/xml")


@router.post("/twilio/status")
async def handle_call_status(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: Optional[str] = Form(None),
    To: Optional[str] = Form(None),
    Direction: Optional[str] = Form(None),
    Timestamp: Optional[str] = Form(None),
    CallDuration: Optional[str] = Form(None)
):
    """
    Handle Twilio call status updates
    Tracks call progress and completion
    """
    try:
        logger.info(f"Call status update: {CallSid} status={CallStatus} duration={CallDuration}")
        
        # Log important status changes
        if CallStatus in ["completed", "busy", "no-answer", "failed", "canceled"]:
            logger.info(f"Call {CallSid} ended with status {CallStatus}, duration: {CallDuration}s")
            
            # TODO: Update voice session in database
            # await update_voice_session_status(CallSid, CallStatus, CallDuration)
        
        elif CallStatus == "in-progress":
            logger.info(f"Call {CallSid} is now in progress")
        
        # Return empty response (Twilio doesn't need response content)
        return Response(status_code=200)
        
    except Exception as e:
        logger.error(f"Error handling call status: {e}", exc_info=True)
        return Response(status_code=200)  # Still return 200 to avoid Twilio retries


@router.get("/twilio/test")
async def test_twilio_integration():
    """
    Test endpoint to verify Twilio integration setup
    """
    return {
        "success": True,
        "message": "Twilio voice integration is ready",
        "endpoints": {
            "voice_webhook": "/api/twilio/voice",
            "status_webhook": "/api/twilio/status",
            "test_endpoint": "/api/twilio/test"
        },
        "instructions": {
            "voice_webhook_url": "Configure this in your Twilio phone number settings",
            "status_webhook_url": "Optional: Set this for call status tracking",
            "media_stream_url": "ws://your-domain/twilio/stream"
        }
    }


@router.post("/twilio/test-call")
async def test_voice_call():
    """
    Test endpoint that simulates Twilio call webhook
    Useful for development and testing
    """
    try:
        # Simulate incoming call parameters
        test_call_sid = "TEST_CALL_" + str(int(datetime.now().timestamp()))
        test_from = "+40721123456"  # Test Romanian number
        test_to = "+40720000000"    # Your business number
        
        # Create test TwiML response
        bridge_url = "ws://localhost:8080/twilio/stream"
        
        twiml = create_connect_stream_twiml(
            stream_url=bridge_url,
            call_sid=test_call_sid,
            from_number=test_from,
            to_number=test_to
        )
        
        return {
            "success": True,
            "message": "Test call TwiML generated",
            "call_sid": test_call_sid,
            "twiml": twiml,
            "bridge_url": bridge_url
        }
        
    except Exception as e:
        logger.error(f"Error generating test call: {e}")
        return {
            "success": False,
            "error": str(e)
        }