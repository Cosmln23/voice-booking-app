"""
Voice Functions Registry
Central registry for all OpenAI Realtime API tool functions
"""

from typing import Dict, Any, Callable, List
from app.voice.functions.services import get_available_services, get_service_details
from app.voice.functions.availability import check_appointment_availability
from app.voice.functions.appointments import create_voice_appointment, confirm_voice_appointment
from app.voice.functions.clients import find_existing_client, get_client_appointment_history
from app.voice.functions.auth import authenticate_voice_session, validate_voice_operation_permissions
from app.voice.processing import (
    normalize_name_from_voice, validate_name_format, format_name_for_voice,
    normalize_phone_from_voice, validate_romanian_phone, format_for_voice,
    map_service_from_voice, format_service_for_voice,
    parse_datetime_from_voice, format_datetime_for_voice,
    classify_user_intent, generate_contextual_response
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# OpenAI Tool Function Definitions
OPENAI_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_available_services",
            "description": "Get all available services for booking. Use this when customer asks about services or what can be booked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional service category filter (e.g., 'tuns', 'barba', 'styling')",
                        "enum": ["tuns", "barba", "styling", "spalat", "coafat"]
                    }
                }
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "check_appointment_availability",
            "description": "Check if a specific date/time is available for booking. Use when customer specifies a preferred date/time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_requested": {
                        "type": "string",
                        "description": "Date in various formats (e.g., '2024-09-05', 'mâine', 'joi')"
                    },
                    "time_requested": {
                        "type": "string", 
                        "description": "Time in various formats (e.g., '10:00', 'dimineața')"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Service duration in minutes (default 30)"
                    }
                },
                "required": ["date_requested"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_existing_client", 
            "description": "Search for existing client by phone or name. Use before creating appointments to check client history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {
                        "type": "string",
                        "description": "Client phone number (primary search method)"
                    },
                    "client_name": {
                        "type": "string",
                        "description": "Client name (secondary search method)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_voice_appointment",
            "description": "Create a new appointment from voice conversation. Use after confirming all details with customer.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "client_name": {
                        "type": "string",
                        "description": "Full name of the client"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Client phone number"
                    },
                    "service_name": {
                        "type": "string", 
                        "description": "Name of the requested service"
                    },
                    "date_requested": {
                        "type": "string",
                        "description": "Appointment date"
                    },
                    "time_requested": {
                        "type": "string",
                        "description": "Appointment time"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes from conversation"
                    }
                },
                "required": ["client_name", "phone", "service_name", "date_requested", "time_requested"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_voice_appointment",
            "description": "Handle appointment confirmation after presenting details to customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_details": {
                        "type": "object",
                        "description": "Appointment details to confirm"
                    },
                    "confirmation_response": {
                        "type": "string",
                        "description": "Customer confirmation response ('da', 'nu', 'modifică')"
                    }
                },
                "required": ["appointment_details", "confirmation_response"]
            }
        }
    }
]

# Function Registry Mapping
VOICE_FUNCTION_REGISTRY: Dict[str, Callable] = {
    "get_available_services": get_available_services,
    "check_appointment_availability": check_appointment_availability,
    "find_existing_client": find_existing_client,
    "create_voice_appointment": create_voice_appointment,
    "confirm_voice_appointment": confirm_voice_appointment,
    "get_service_details": get_service_details,
    "get_client_appointment_history": get_client_appointment_history
}

# Romanian Language Processing Functions
ROMANIAN_PROCESSING_FUNCTIONS = {
    "normalize_name": normalize_name_from_voice,
    "validate_name": validate_name_format,
    "format_name": format_name_for_voice,
    "normalize_phone": normalize_phone_from_voice,
    "validate_phone": validate_romanian_phone,
    "format_phone": format_for_voice,
    "map_service": map_service_from_voice,
    "format_service": format_service_for_voice,
    "parse_datetime": parse_datetime_from_voice,
    "format_datetime": format_datetime_for_voice,
    "classify_intent": classify_user_intent,
    "generate_response": generate_contextual_response
}


async def execute_voice_function(
    function_name: str,
    function_args: Dict[str, Any],
    supabase_client,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a voice function with proper error handling and logging
    
    Args:
        function_name: Name of the function to execute
        function_args: Arguments to pass to the function
        supabase_client: Supabase client instance
        user_context: Voice user context for authentication
        
    Returns:
        Dictionary with function result
    """
    try:
        logger.info(f"Executing voice function: {function_name}", extra={"args": function_args})
        
        # Validate function exists
        if function_name not in VOICE_FUNCTION_REGISTRY:
            return {
                "success": False,
                "message": f"Function not found: {function_name}",
                "voice_response": "Ne pare rău, nu pot procesa această cerere în acest moment.",
                "error_type": "function_not_found"
            }
        
        # Validate permissions
        has_permission = await validate_voice_operation_permissions(
            function_name, user_context
        )
        
        if not has_permission:
            return {
                "success": False,
                "message": f"Permission denied for function: {function_name}",
                "voice_response": "Nu am autorizarea să efectuez această operațiune.",
                "error_type": "permission_denied"
            }
        
        # Get function and add supabase_client to args
        function = VOICE_FUNCTION_REGISTRY[function_name]
        function_args["supabase_client"] = supabase_client
        
        # Execute function
        result = await function(**function_args)
        
        logger.info(f"Voice function {function_name} completed", 
                   extra={"success": result.get("success", False)})
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing voice function {function_name}: {e}", 
                    exc_info=True, extra={"args": function_args})
        
        return {
            "success": False,
            "message": f"Error in {function_name}: {str(e)}",
            "voice_response": "A apărut o problemă tehnică. Vă rog să încercați din nou.",
            "error_type": "execution_error",
            "function": function_name
        }


def process_voice_input(voice_input: str, processing_type: str) -> Dict[str, Any]:
    """
    Process voice input using Romanian language processing functions
    
    Args:
        voice_input: Raw voice input string
        processing_type: Type of processing to apply
        
    Returns:
        Dictionary with processing results
    """
    try:
        if processing_type not in ROMANIAN_PROCESSING_FUNCTIONS:
            return {
                "success": False,
                "message": f"Processing type not found: {processing_type}"
            }
        
        processor = ROMANIAN_PROCESSING_FUNCTIONS[processing_type]
        result = processor(voice_input)
        
        return {
            "success": True,
            "processing_type": processing_type,
            "original_input": voice_input,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing voice input: {e}")
        return {
            "success": False,
            "message": f"Processing error: {str(e)}",
            "processing_type": processing_type,
            "original_input": voice_input
        }


def get_openai_tools_definition() -> List[Dict[str, Any]]:
    """
    Get OpenAI Realtime API tools definition
    
    Returns:
        List of tool definitions for OpenAI API
    """
    return OPENAI_TOOL_DEFINITIONS


def get_available_functions() -> List[str]:
    """
    Get list of available voice function names
    
    Returns:
        List of function names
    """
    return list(VOICE_FUNCTION_REGISTRY.keys())


def validate_function_args(function_name: str, args: Dict[str, Any]) -> bool:
    """
    Validate function arguments against OpenAI tool definition
    
    Args:
        function_name: Name of the function
        args: Arguments to validate
        
    Returns:
        bool: True if arguments are valid
    """
    try:
        # Find tool definition
        tool_def = None
        for tool in OPENAI_TOOL_DEFINITIONS:
            if tool["function"]["name"] == function_name:
                tool_def = tool
                break
        
        if not tool_def:
            return False
        
        # Check required parameters
        required_params = tool_def["function"]["parameters"].get("required", [])
        for param in required_params:
            if param not in args:
                logger.warning(f"Missing required parameter {param} for {function_name}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating function args: {e}")
        return False