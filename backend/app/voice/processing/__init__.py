"""
Romanian Language Processing Package
Advanced Romanian language utilities for voice booking system
"""

# Import all processing functions for easy access
from .name_utils import (
    normalize_name_from_voice,
    validate_name_format,
    format_name_for_voice,
    get_name_suggestions
)

from .phone_utils import (
    normalize_phone_from_voice,
    validate_romanian_phone,
    get_phone_info,
    format_for_voice
)

from .service_mapper import (
    map_service_from_voice,
    get_all_services,
    format_service_for_voice
)

from .datetime_parser import (
    parse_datetime_from_voice,
    format_datetime_for_voice,
    get_available_time_slots
)

from .vocabulary import (
    classify_user_intent,
    generate_contextual_response,
    extract_salon_entities
)

__all__ = [
    # Name processing
    "normalize_name_from_voice",
    "validate_name_format", 
    "format_name_for_voice",
    "get_name_suggestions",
    
    # Phone processing
    "normalize_phone_from_voice",
    "validate_romanian_phone",
    "get_phone_info",
    "format_for_voice",
    
    # Service mapping
    "map_service_from_voice",
    "get_all_services",
    "format_service_for_voice",
    
    # DateTime parsing
    "parse_datetime_from_voice",
    "format_datetime_for_voice",
    "get_available_time_slots",
    
    # Vocabulary and intent
    "classify_user_intent",
    "generate_contextual_response",
    "extract_salon_entities"
]