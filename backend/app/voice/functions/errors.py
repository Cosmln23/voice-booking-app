"""
Voice Error Handling
Romanian language error handling and responses for voice interactions
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class VoiceErrorType(str, Enum):
    """Voice-specific error types"""
    # Authentication errors
    AUTH_FAILED = "auth_failed"
    PERMISSION_DENIED = "permission_denied"
    SESSION_EXPIRED = "session_expired"
    
    # Data validation errors
    INVALID_PHONE = "invalid_phone"
    INVALID_DATE = "invalid_date"
    INVALID_TIME = "invalid_time"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    
    # Business logic errors
    PAST_DATE = "past_date"
    NON_WORKING_DAY = "non_working_day"
    TIME_SLOT_OCCUPIED = "time_slot_occupied"
    FULLY_BOOKED = "fully_booked"
    SERVICE_NOT_AVAILABLE = "service_not_available"
    
    # Client management errors
    CLIENT_NOT_FOUND = "client_not_found"
    MULTIPLE_CLIENTS_FOUND = "multiple_clients_found"
    CLIENT_INACTIVE = "client_inactive"
    
    # System errors
    DATABASE_ERROR = "database_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    SYSTEM_ERROR = "system_error"
    TIMEOUT_ERROR = "timeout_error"
    
    # Voice interaction errors
    SPEECH_NOT_UNDERSTOOD = "speech_not_understood"
    UNCLEAR_RESPONSE = "unclear_response"
    USER_CANCELLED = "user_cancelled"
    CALL_INTERRUPTED = "call_interrupted"


class VoiceError(Exception):
    """Base exception for voice-related errors"""
    
    def __init__(
        self, 
        message: str, 
        error_type: VoiceErrorType,
        voice_response: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.voice_response = voice_response or self._generate_default_voice_response()
        self.details = details or {}
        super().__init__(self.message)
    
    def _generate_default_voice_response(self) -> str:
        """Generate default Romanian voice response for error type"""
        return ROMANIAN_ERROR_MESSAGES.get(
            self.error_type, 
            "A apărut o problemă. Vă rog să încercați din nou."
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response"""
        return {
            "success": False,
            "message": self.message,
            "voice_response": self.voice_response,
            "error_type": self.error_type.value,
            "details": self.details,
            "timestamp": datetime.now().isoformat()
        }


# Romanian error messages for voice responses
ROMANIAN_ERROR_MESSAGES = {
    # Authentication errors
    VoiceErrorType.AUTH_FAILED: "Ne pare rău, nu pot procesa cererea în acest moment. Vă rog să ne sunați din nou.",
    VoiceErrorType.PERMISSION_DENIED: "Nu am autorizarea să efectuez această operațiune.",
    VoiceErrorType.SESSION_EXPIRED: "Sesiunea a expirat. Vă rog să sunați din nou pentru o programare nouă.",
    
    # Data validation errors
    VoiceErrorType.INVALID_PHONE: "Numărul de telefon nu pare să fie valid. Vă rog să îl repetați clar.",
    VoiceErrorType.INVALID_DATE: "Nu înțeleg data specificată. Vă rog să spuneți o dată clară, de exemplu 'mâine' sau 'joi'.",
    VoiceErrorType.INVALID_TIME: "Nu înțeleg ora specificată. Vă rog să spuneți o oră clară, de exemplu 'zece' sau 'două și jumătate'.",
    VoiceErrorType.MISSING_REQUIRED_FIELD: "Îmi lipsesc informații importante. Vă rog să repetați cererea.",
    
    # Business logic errors
    VoiceErrorType.PAST_DATE: "Nu pot programa în trecut. Vă rog să alegeți o dată din viitor.",
    VoiceErrorType.NON_WORKING_DAY: "Nu lucrăm în această zi. Programăm doar în zilele lucrătoare.",
    VoiceErrorType.TIME_SLOT_OCCUPIED: "Ora solicitată este ocupată. Vă pot propune o altă oră?",
    VoiceErrorType.FULLY_BOOKED: "În această zi nu mai avem locuri libere. Doriți să încercăm altă zi?",
    VoiceErrorType.SERVICE_NOT_AVAILABLE: "Nu am găsit serviciul cerut. Vă pot spune ce servicii avem disponibile?",
    
    # Client management errors
    VoiceErrorType.CLIENT_NOT_FOUND: "Nu am găsit acest client în sistemul nostru. Doriți să creez o programare nouă?",
    VoiceErrorType.MULTIPLE_CLIENTS_FOUND: "Am găsit mai mulți clienți cu date similare. Vă rog să specificați numărul de telefon.",
    VoiceErrorType.CLIENT_INACTIVE: "Acest client nu mai este activ în sistemul nostru.",
    
    # System errors
    VoiceErrorType.DATABASE_ERROR: "A apărut o problemă tehnică. Vă rog să încercați din nou în câteva minute.",
    VoiceErrorType.EXTERNAL_SERVICE_ERROR: "Nu pot accesa toate informațiile în acest moment. Vă rog să încercați din nou.",
    VoiceErrorType.SYSTEM_ERROR: "A apărut o eroare de sistem. Vă rog să ne sunați din nou.",
    VoiceErrorType.TIMEOUT_ERROR: "Procesarea durează prea mult. Vă rog să încercați din nou.",
    
    # Voice interaction errors
    VoiceErrorType.SPEECH_NOT_UNDERSTOOD: "Nu am înțeles ce ați spus. Vă rog să repetați mai clar.",
    VoiceErrorType.UNCLEAR_RESPONSE: "Răspunsul nu este clar. Vă rog să spuneți 'da' sau 'nu'.",
    VoiceErrorType.USER_CANCELLED: "În regulă, am anulat operațiunea. Cu ce vă mai pot ajuta?",
    VoiceErrorType.CALL_INTERRUPTED: "Apelul a fost întrerupt. Vă rog să sunați din nou dacă doriți să continuați."
}


# Contextual error responses with additional help
CONTEXTUAL_ERROR_RESPONSES = {
    # Date/time context
    VoiceErrorType.INVALID_DATE: {
        "response": "Nu înțeleg data specificată. Puteți spune de exemplu: 'mâine', 'joi', sau data completă ca '5 septembrie'.",
        "suggestions": ["Încercați să spuneți ziua săptămânii", "Sau spuneți 'mâine' pentru ziua următoare"]
    },
    
    VoiceErrorType.INVALID_TIME: {
        "response": "Nu înțeleg ora specificată. Puteți spune de exemplu: 'zece dimineața', 'două și jumătate', sau 'după-amiaza'.",
        "suggestions": ["Spuneți ora cu numere întregi", "Sau alegeți din intervalele: dimineața, prânz, după-amiaza"]
    },
    
    # Service context
    VoiceErrorType.SERVICE_NOT_AVAILABLE: {
        "response": "Nu am găsit serviciul cerut în lista noastră.",
        "suggestions": ["Avem servicii de tuns, bărbierit și styling", "Doriți să auziți lista completă?"]
    },
    
    # Availability context
    VoiceErrorType.TIME_SLOT_OCCUPIED: {
        "response": "Ora solicitată este deja ocupată.",
        "suggestions": ["Pot să verific ora anterioară sau următoare", "Sau puteți alege altă zi"]
    },
    
    VoiceErrorType.FULLY_BOOKED: {
        "response": "În această zi suntem complet rezervați.",
        "suggestions": ["Pot verifica disponibilitatea pentru mâine", "Sau pentru următoarea zi lucrătoare"]
    }
}


def handle_voice_error(error: VoiceError, function_name: str) -> Dict[str, Any]:
    """
    Handle voice error and generate appropriate response
    
    Args:
        error: VoiceError instance
        function_name: Name of the function where error occurred
        
    Returns:
        Dictionary with error response formatted for voice
    """
    logger.error(
        f"Voice error in {function_name}: {error.message}",
        extra={
            "error_type": error.error_type.value,
            "function": function_name,
            "details": error.details
        }
    )
    
    # Get contextual response if available
    contextual = CONTEXTUAL_ERROR_RESPONSES.get(error.error_type)
    
    response = error.to_dict()
    
    if contextual:
        response["voice_response"] = contextual["response"]
        response["suggestions"] = contextual["suggestions"]
        response["help_available"] = True
    
    response["function"] = function_name
    
    return response


def create_voice_error(
    error_type: VoiceErrorType,
    message: Optional[str] = None,
    voice_response: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    context: Optional[str] = None
) -> VoiceError:
    """
    Create a voice error with Romanian messaging
    
    Args:
        error_type: Type of error
        message: Technical error message (optional)
        voice_response: Custom voice response (optional)
        details: Additional error details (optional)
        context: Context where error occurred (optional)
        
    Returns:
        VoiceError instance
    """
    if not message:
        message = f"Voice error: {error_type.value}"
    
    if context:
        details = details or {}
        details["context"] = context
    
    return VoiceError(
        message=message,
        error_type=error_type,
        voice_response=voice_response,
        details=details
    )


def handle_system_exception(
    exception: Exception,
    function_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle unexpected system exceptions in voice functions
    
    Args:
        exception: The caught exception
        function_name: Name of the function where exception occurred
        context: Additional context information
        
    Returns:
        Dictionary with error response for voice
    """
    error_details = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception)
    }
    
    if context:
        error_details["context"] = context
    
    voice_error = create_voice_error(
        error_type=VoiceErrorType.SYSTEM_ERROR,
        message=f"System error in {function_name}: {str(exception)}",
        details=error_details,
        context=function_name
    )
    
    return handle_voice_error(voice_error, function_name)


# Helper functions for specific error scenarios

def create_validation_error(field_name: str, field_value: str) -> VoiceError:
    """Create validation error for specific field"""
    field_messages = {
        "phone": "Numărul de telefon nu este valid",
        "date": "Data nu este validă", 
        "time": "Ora nu este validă",
        "name": "Numele nu este valid",
        "service": "Serviciul nu este valid"
    }
    
    message = field_messages.get(field_name, f"Câmpul {field_name} nu este valid")
    
    return create_voice_error(
        error_type=VoiceErrorType.MISSING_REQUIRED_FIELD,
        message=message,
        details={"field": field_name, "value": field_value}
    )


def create_business_logic_error(
    error_type: VoiceErrorType,
    custom_message: Optional[str] = None,
    suggestions: Optional[List[str]] = None
) -> VoiceError:
    """Create business logic error with suggestions"""
    details = {}
    if suggestions:
        details["suggestions"] = suggestions
    
    return create_voice_error(
        error_type=error_type,
        voice_response=custom_message,
        details=details
    )


def create_user_interaction_error(response_type: str) -> VoiceError:
    """Create error for unclear user responses"""
    response_messages = {
        "confirmation": "Nu am înțeles răspunsul. Vă rog să spuneți 'da' pentru confirmare sau 'nu' pentru anulare.",
        "choice": "Nu am înțeles alegerea. Vă rog să specificați opțiunea dorită.",
        "repeat": "Nu am înțeles. Vă rog să repetați mai clar."
    }
    
    voice_response = response_messages.get(response_type, response_messages["repeat"])
    
    return create_voice_error(
        error_type=VoiceErrorType.UNCLEAR_RESPONSE,
        voice_response=voice_response,
        details={"response_type": response_type}
    )


# Success message helpers (Romanian)

def create_success_message(operation: str, details: Dict[str, Any]) -> str:
    """Create success message in Romanian for voice response"""
    
    success_templates = {
        "appointment_created": "Programarea a fost creată cu succes pentru {client} pe {date} la ora {time}.",
        "client_found": "Am găsit clientul {name} cu numărul {phone}.",
        "availability_found": "Avem locuri libere pe {date} la orele {times}.",
        "service_info": "Serviciul {service} durează {duration} și costă {price}."
    }
    
    template = success_templates.get(operation, "Operațiunea s-a finalizat cu succes.")
    
    try:
        return template.format(**details)
    except KeyError:
        return template
    except Exception:
        return "Operațiunea s-a finalizat cu succes."