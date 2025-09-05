"""
Romanian Error Messages and Voice-Friendly Responses
Provides localized error handling for voice interactions
"""

from typing import Dict, Optional
from enum import Enum

class VoiceErrorType(str, Enum):
    """Types of voice errors"""
    VALIDATION_ERROR = "validation_error"
    AUTH_ERROR = "auth_error"
    BOOKING_CONFLICT = "booking_conflict"
    SYSTEM_ERROR = "system_error"
    INPUT_NOT_UNDERSTOOD = "input_not_understood"
    MISSING_REQUIRED_INFO = "missing_required_info"
    INVALID_DATE_TIME = "invalid_date_time"
    SERVICE_NOT_AVAILABLE = "service_not_available"
    NO_AVAILABLE_SLOTS = "no_available_slots"
    PHONE_VALIDATION_ERROR = "phone_validation_error"
    DUPLICATE_BOOKING = "duplicate_booking"


class RomanianVoiceErrors:
    """Romanian error messages optimized for voice interaction"""
    
    # Base error messages - friendly and conversational
    ERROR_MESSAGES: Dict[VoiceErrorType, str] = {
        VoiceErrorType.VALIDATION_ERROR: (
            "Ne pare rău, informațiile furnizate nu sunt complete sau corecte. "
            "Vă rugăm să verificați și să încercați din nou."
        ),
        
        VoiceErrorType.AUTH_ERROR: (
            "Din motive de securitate, nu putem procesa această cerere în acest moment. "
            "Vă rugăm să ne contactați direct la salon."
        ),
        
        VoiceErrorType.BOOKING_CONFLICT: (
            "Din păcate, intervalul orar dorit nu mai este disponibil. "
            "Vă pot propune alte opțiuni de programare."
        ),
        
        VoiceErrorType.SYSTEM_ERROR: (
            "A apărut o problemă tehnică temporară. "
            "Vă rugăm să încercați din nou sau să ne contactați direct."
        ),
        
        VoiceErrorType.INPUT_NOT_UNDERSTOOD: (
            "Ne pare rău, nu am înțeles exact ce doriți. "
            "Puteți să reformulați cererea dumneavoastră?"
        ),
        
        VoiceErrorType.MISSING_REQUIRED_INFO: (
            "Pentru a continua cu programarea, mai am nevoie de câteva informații. "
            "Vă voi ghida pas cu pas."
        ),
        
        VoiceErrorType.INVALID_DATE_TIME: (
            "Data sau ora specificată nu este validă. "
            "Vă rugăm să menționați o dată din viitor și o oră din intervalul nostru de lucru."
        ),
        
        VoiceErrorType.SERVICE_NOT_AVAILABLE: (
            "Din păcate, serviciul solicitat nu este disponibil în acest moment. "
            "Vă pot oferi alternative similare."
        ),
        
        VoiceErrorType.NO_AVAILABLE_SLOTS: (
            "Nu am găsit intervale libere pentru data dorită. "
            "Vă pot propune alte date disponibile."
        ),
        
        VoiceErrorType.PHONE_VALIDATION_ERROR: (
            "Numărul de telefon furnizat nu pare a fi corect. "
            "Vă rugăm să-l repetați sau să furnizați un alt număr."
        ),
        
        VoiceErrorType.DUPLICATE_BOOKING: (
            "Se pare că aveți deja o programare pentru această dată. "
            "Doriți să modificați programarea existentă?"
        )
    }

    # Contextual error messages for specific situations
    CONTEXTUAL_MESSAGES: Dict[str, Dict[str, str]] = {
        "appointment_booking": {
            "missing_client_name": (
                "Pentru a vă face programarea, vă rog să-mi spuneți numele dumneavoastră complet."
            ),
            "missing_phone": (
                "Am nevoie și de numărul dumneavoastră de telefon pentru confirmarea programării."
            ),
            "missing_service": (
                "Ce serviciu doriți să programați? Putem face tuns, vopsit, coafat și multe altele."
            ),
            "missing_date": (
                "Pentru ce dată doriți programarea? Puteți spune ziua și luna sau data completă."
            ),
            "missing_time": (
                "La ce oră v-ar conveni? Programul nostru este de luni până vineri, de la 9 la 18."
            )
        },
        
        "client_info": {
            "invalid_name_format": (
                "Vă rog să-mi spuneți prenumele și numele, de exemplu 'Maria Popescu'."
            ),
            "phone_too_short": (
                "Numărul de telefon pare incomplet. Un număr valid are cel puțin 10 cifre."
            ),
            "phone_invalid_format": (
                "Vă rog să spuneți numărul de telefon cifră cu cifră, sau cu prefixul pentru România."
            )
        },
        
        "service_selection": {
            "service_not_found": (
                "Nu am găsit serviciul menționat în lista noastră. "
                "Avem disponibile: tuns, vopsit, coafat, manichiură, pedichiură și tratamente faciale."
            ),
            "service_needs_consultation": (
                "Pentru acest serviciu recomand o consultație preliminară. "
                "Putem programa mai întâi o scurtă întrevedere?"
            )
        },
        
        "time_scheduling": {
            "time_in_past": (
                "Data și ora specificate sunt în trecut. "
                "Vă rog să alegeți o dată din viitor pentru programare."
            ),
            "time_outside_hours": (
                "Din păcate, nu lucram la ora specificată. "
                "Programul nostru este de luni până vineri, între 9 și 18."
            ),
            "weekend_closed": (
                "Weekend-ul suntem închisi. Putem programa pentru zilele de luni până vineri."
            ),
            "holiday_closed": (
                "În zilele de sărbătoare nu lucram. "
                "Vă pot propune alte date disponibile."
            )
        }
    }

    # Helpful suggestions for common errors
    SUGGESTIONS: Dict[VoiceErrorType, str] = {
        VoiceErrorType.INPUT_NOT_UNDERSTOOD: (
            "Încercați să spuneți mai clar sau mai simplu ce doriți să programați."
        ),
        VoiceErrorType.INVALID_DATE_TIME: (
            "Spuneți data în formatul 'mâine', 'luni viitoare', sau '15 martie'."
        ),
        VoiceErrorType.PHONE_VALIDATION_ERROR: (
            "Spuneți numărul cifră cu cifră, de exemplu: 'zero șapte trei, unu doi trei, patru cinci șase'."
        ),
        VoiceErrorType.SERVICE_NOT_AVAILABLE: (
            "Întrebați despre serviciile noastre principale: tuns, vopsit sau coafat."
        )
    }

    @classmethod
    def get_error_message(
        cls, 
        error_type: VoiceErrorType, 
        context: Optional[str] = None,
        specific_field: Optional[str] = None
    ) -> str:
        """Get localized error message"""
        
        # Try contextual message first
        if context and specific_field:
            contextual = cls.CONTEXTUAL_MESSAGES.get(context, {})
            if specific_field in contextual:
                return contextual[specific_field]
        
        # Fall back to base error message
        return cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES[VoiceErrorType.SYSTEM_ERROR])

    @classmethod
    def get_error_with_suggestion(cls, error_type: VoiceErrorType) -> str:
        """Get error message with helpful suggestion"""
        message = cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES[VoiceErrorType.SYSTEM_ERROR])
        suggestion = cls.SUGGESTIONS.get(error_type)
        
        if suggestion:
            return f"{message} {suggestion}"
        
        return message

    @classmethod
    def format_validation_error(cls, field_name: str, error_details: str) -> str:
        """Format field validation error"""
        field_translations = {
            "client_name": "numele clientului",
            "phone": "numărul de telefon", 
            "service": "serviciul dorit",
            "date": "data programării",
            "time": "ora programării",
            "duration": "durata serviciului"
        }
        
        field_ro = field_translations.get(field_name, field_name)
        return f"Există o problemă cu {field_ro}: {error_details}"

    @classmethod
    def get_retry_message(cls, attempt_count: int) -> str:
        """Get retry message based on attempt count"""
        if attempt_count == 1:
            return "Să încercăm din nou."
        elif attempt_count == 2:
            return "Să mai încercăm o dată, cu răbdare."
        elif attempt_count >= 3:
            return (
                "Pentru a evita confuziile, vă sugerez să ne contactați direct la salon "
                "pentru a face programarea."
            )
        
        return "Vă rugăm să încercați din nou."

    @classmethod
    def get_confirmation_request(cls, data_to_confirm: Dict[str, str]) -> str:
        """Get confirmation message for collected data"""
        confirmations = []
        
        if "client_name" in data_to_confirm:
            confirmations.append(f"numele {data_to_confirm['client_name']}")
        
        if "service" in data_to_confirm:
            confirmations.append(f"serviciul {data_to_confirm['service']}")
            
        if "date" in data_to_confirm and "time" in data_to_confirm:
            confirmations.append(f"data {data_to_confirm['date']} la ora {data_to_confirm['time']}")
        elif "date" in data_to_confirm:
            confirmations.append(f"data {data_to_confirm['date']}")
        elif "time" in data_to_confirm:
            confirmations.append(f"ora {data_to_confirm['time']}")
            
        if "phone" in data_to_confirm:
            confirmations.append(f"telefonul {data_to_confirm['phone']}")
        
        if not confirmations:
            return "Să confirmăm datele pentru programare."
        
        confirmation_text = ", ".join(confirmations)
        return f"Să confirm: {confirmation_text}. Este corect?"

    @classmethod
    def get_success_message(cls, booking_type: str = "appointment") -> str:
        """Get success message for completed actions"""
        messages = {
            "appointment": (
                "Perfect! Programarea dumneavoastră a fost înregistrată cu succes. "
                "Veți primi o confirmare prin SMS."
            ),
            "reschedule": (
                "Programarea a fost reprogramată cu succes. "
                "Veți primi detaliile actualizate prin SMS."
            ),
            "cancellation": (
                "Programarea a fost anulată conform cererii dumneavoastră. "
                "Vă așteptăm cu drag într-o altă ocazie."
            )
        }
        
        return messages.get(booking_type, messages["appointment"])