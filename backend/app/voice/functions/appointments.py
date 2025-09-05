"""
Voice Tool Function: Appointment Management
Handles appointment creation and management for voice bookings
"""

from typing import Dict, Any, Optional
from datetime import datetime, date, time, timedelta
from dateutil.parser import parse as parse_date

from app.core.logging import get_logger
from app.database.user_crud_appointments import UserAppointmentCRUD
from app.database.user_crud_clients import UserClientCRUD
from app.models.appointment import (
    AppointmentCreate, AppointmentStatus, AppointmentType, 
    AppointmentPriority, Appointment
)
from app.models.client import ClientCreate, ClientStatus
from app.voice.functions.auth import get_voice_user_context
from app.voice.functions.errors import VoiceError, handle_voice_error
from app.voice.functions.availability import _parse_voice_date, _parse_voice_time, _date_to_voice, _time_to_voice
from app.voice.processing import (
    normalize_name_from_voice, normalize_phone_from_voice, 
    map_service_from_voice, parse_datetime_from_voice
)

logger = get_logger(__name__)


async def create_voice_appointment(
    client_name: str,
    phone: str,
    service_name: str,
    date_requested: str,
    time_requested: str,
    notes: Optional[str] = None,
    supabase_client = None
) -> Dict[str, Any]:
    """
    Voice Tool Function: Create Voice Appointment
    
    Creates a new appointment from voice interaction.
    Handles client creation if needed and validates all data.
    
    Args:
        client_name: Full name of the client
        phone: Phone number (will be normalized)
        service_name: Name of the requested service
        date_requested: Date in various formats
        time_requested: Time in various formats
        notes: Optional notes from voice conversation
        supabase_client: Supabase client instance
    
    Returns:
        Dictionary with appointment creation result for voice response
    """
    try:
        logger.info(f"Voice request: create_appointment, client={client_name}, phone={phone}, service={service_name}")
        
        # Get user context
        user_context = await get_voice_user_context(supabase_client)
        
        # Normalize and validate phone number using Romanian processing
        normalized_phone = normalize_phone_from_voice(phone)
        if not normalized_phone:
            return {
                "success": False,
                "message": f"Număr de telefon invalid: {phone}",
                "voice_response": "Numărul de telefon nu pare să fie valid. Vă rog să îl repetați.",
                "appointment": None,
                "error_type": "invalid_phone"
            }
        
        # Parse date and time using Romanian processing
        try:
            # Try Romanian datetime parser first
            datetime_result = parse_datetime_from_voice(f"{date_requested} {time_requested}")
            if datetime_result.get("success"):
                parsed_date = datetime_result["parsed_date"]
                parsed_time = datetime_result["parsed_time"]
            else:
                # Fallback to original parsers
                parsed_date = await _parse_voice_date(date_requested)
                parsed_time = await _parse_voice_time(time_requested)
        except ValueError as e:
            return {
                "success": False,
                "message": f"Dată sau oră invalidă: {str(e)}",
                "voice_response": "Nu înțeleg data sau ora specificată. Vă rog să repetați cu o dată și oră clare.",
                "appointment": None,
                "error_type": "invalid_datetime"
            }
        
        # Validate date is not in the past
        if parsed_date < date.today() or (parsed_date == date.today() and parsed_time < datetime.now().time()):
            return {
                "success": False,
                "message": "Nu se pot programa în trecut",
                "voice_response": "Nu pot programa în trecut. Vă rog să alegeți o dată și oră din viitor.",
                "appointment": None,
                "error_type": "past_datetime"
            }
        
        # Initialize CRUD instances
        appointment_crud = UserAppointmentCRUD(supabase_client, user_context["user_id"])
        client_crud = UserClientCRUD(supabase_client, user_context["user_id"])
        
        # Normalize client name using Romanian processing
        name_result = normalize_name_from_voice(client_name)
        normalized_name = name_result.get("normalized", client_name) if name_result.get("success") else client_name
        
        # Check for existing client or create new one
        existing_client = await _find_or_create_client(
            normalized_name, normalized_phone, client_crud
        )
        
        # Map service name using Romanian processing
        service_result = map_service_from_voice(service_name)
        if service_result.get("success"):
            canonical_service = service_result["canonical_name"]
            service_category = service_result["category"]
        else:
            canonical_service = service_name
            service_category = None
        
        # Estimate service duration (default to 30 min if service not found)
        duration_minutes = await _get_service_duration(canonical_service, supabase_client, user_context["user_id"])
        
        # Final availability check
        is_available = await _final_availability_check(
            parsed_date, parsed_time, duration_minutes,
            appointment_crud
        )
        
        if not is_available:
            return {
                "success": False,
                "message": "Intervalul nu mai este disponibil",
                "voice_response": f"Ne pare rău, dar intervalul de pe {_date_to_voice(parsed_date)} la ora {_time_to_voice(parsed_time)} nu mai este disponibil. Doriți să alegeți altă oră?",
                "appointment": None,
                "error_type": "slot_no_longer_available"
            }
        
        # Create appointment data
        appointment_data = AppointmentCreate(
            client_name=client_name.strip(),
            phone=normalized_phone,
            service=service_name.strip(),
            date=parsed_date,
            time=parsed_time,
            duration=f"{duration_minutes}min",
            status=AppointmentStatus.CONFIRMED,  # Voice appointments are confirmed immediately
            type=AppointmentType.VOICE,
            priority=AppointmentPriority.NORMAL,
            notes=notes.strip() if notes else None
        )
        
        # Create the appointment
        created_appointment = await appointment_crud.create_appointment(appointment_data)
        
        # Generate confirmation message
        confirmation_message = _generate_confirmation_message(
            created_appointment, client_name, parsed_date, parsed_time
        )
        
        logger.info(f"Voice appointment created: {created_appointment.id} for {client_name}")
        
        return {
            "success": True,
            "message": "Programare creată cu succes",
            "voice_response": confirmation_message,
            "appointment": {
                "id": created_appointment.id,
                "client_name": created_appointment.client_name,
                "phone": created_appointment.phone,
                "service": created_appointment.service,
                "date": created_appointment.date.isoformat(),
                "time": created_appointment.time.strftime("%H:%M"),
                "duration": created_appointment.duration,
                "status": created_appointment.status.value,
                "type": created_appointment.type.value,
                "created_at": created_appointment.created_at.isoformat()
            }
        }
        
    except VoiceError as ve:
        return handle_voice_error(ve, "create_voice_appointment")
    except Exception as e:
        logger.error(f"Error in create_voice_appointment: {e}", exc_info=True)
        return {
            "success": False,
            "message": "Eroare în crearea programării",
            "voice_response": "Ne pare rău, nu am putut crea programarea. Vă rog să încercați din nou sau să ne sunați direct.",
            "appointment": None,
            "error_type": "system_error"
        }


async def confirm_voice_appointment(
    appointment_details: Dict[str, Any],
    confirmation_response: str,  # "da", "nu", "modifică", etc.
    supabase_client = None
) -> Dict[str, Any]:
    """
    Voice Tool Function: Confirm Voice Appointment
    
    Handles final confirmation of appointment details before creation.
    
    Args:
        appointment_details: Dict with appointment info to confirm
        confirmation_response: User's confirmation ("da", "nu", etc.)
        supabase_client: Supabase client instance
    
    Returns:
        Dictionary with confirmation result for voice response
    """
    try:
        logger.info(f"Voice confirmation: {confirmation_response} for appointment")
        
        confirmation = confirmation_response.lower().strip()
        
        if confirmation in ["da", "yes", "confirm", "confirmă", "confirma", "ok", "bine"]:
            # User confirmed - create the appointment
            return await create_voice_appointment(
                client_name=appointment_details["client_name"],
                phone=appointment_details["phone"],
                service_name=appointment_details["service"],
                date_requested=appointment_details["date"],
                time_requested=appointment_details["time"],
                notes=appointment_details.get("notes"),
                supabase_client=supabase_client
            )
        
        elif confirmation in ["nu", "no", "anulează", "anuleaza", "stop"]:
            return {
                "success": False,
                "message": "Programare anulată de utilizator",
                "voice_response": "În regulă, am anulat programarea. Cu ce vă mai pot ajuta?",
                "appointment": None,
                "error_type": "user_cancelled"
            }
        
        elif confirmation in ["modifică", "modifica", "schimbă", "schimba", "altfel"]:
            return {
                "success": False,
                "message": "Utilizatorul dorește modificări",
                "voice_response": "Ce doriți să modificați? Data, ora sau serviciul?",
                "appointment": None,
                "error_type": "user_wants_changes",
                "action_needed": "request_changes"
            }
        
        else:
            return {
                "success": False,
                "message": f"Răspuns neclar: {confirmation_response}",
                "voice_response": "Nu am înțeles răspunsul. Vă rog să spuneți 'da' pentru confirmare sau 'nu' pentru anulare.",
                "appointment": None,
                "error_type": "unclear_response",
                "action_needed": "repeat_confirmation"
            }
            
    except Exception as e:
        logger.error(f"Error in confirm_voice_appointment: {e}", exc_info=True)
        return {
            "success": False,
            "message": "Eroare în confirmarea programării",
            "voice_response": "A apărut o problemă cu confirmarea. Vă rog să încercați din nou.",
            "appointment": None,
            "error_type": "system_error"
        }


def _normalize_phone_number(phone: str) -> str:
    """Normalize phone number to international format"""
    # Remove spaces, dashes, parentheses
    clean_phone = ''.join(char for char in phone if char.isdigit() or char == '+')
    
    # Handle Romanian numbers
    if clean_phone.startswith('07'):  # Romanian mobile format
        clean_phone = '+4' + clean_phone
    elif clean_phone.startswith('4007'):  # Already prefixed
        clean_phone = '+' + clean_phone
    elif not clean_phone.startswith('+'):
        # Try to add +40 for Romanian numbers
        if len(clean_phone) == 10 and clean_phone.startswith('07'):
            clean_phone = '+4' + clean_phone
        elif len(clean_phone) >= 10:
            clean_phone = '+' + clean_phone
    
    return clean_phone


def _is_valid_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone.startswith('+'):
        return False
    
    # Remove + and check if all remaining chars are digits
    digits_only = phone[1:]
    if not digits_only.isdigit():
        return False
    
    # Check length (international format should be 10-15 digits)
    return 10 <= len(digits_only) <= 15


async def _find_or_create_client(
    client_name: str, 
    phone: str, 
    client_crud: UserClientCRUD
) -> Optional[Dict]:
    """Find existing client by phone or create new one"""
    try:
        # Search for existing client by phone
        existing_clients, total = await client_crud.get_clients(
            search=phone,  # Search by phone
            limit=1,
            offset=0
        )
        
        if existing_clients:
            logger.info(f"Found existing client: {existing_clients[0].name}")
            return existing_clients[0]
        
        # Create new client
        client_data = ClientCreate(
            name=client_name.strip(),
            phone=phone,
            email=None,
            status=ClientStatus.ACTIVE,
            notes=f"Client creat prin apel vocal pe {datetime.now().strftime('%d.%m.%Y')}"
        )
        
        new_client = await client_crud.create_client(client_data)
        logger.info(f"Created new client: {new_client.name}")
        return new_client
        
    except Exception as e:
        logger.error(f"Error in _find_or_create_client: {e}")
        return None


async def _get_service_duration(
    service_name: str, 
    supabase_client, 
    user_id: str
) -> int:
    """Get service duration or return default"""
    try:
        from app.database.crud_services import ServiceCRUD
        
        service_crud = ServiceCRUD(supabase_client)
        services, _ = await service_crud.get_services(
            search=service_name,
            limit=1,
            offset=0,
            user_id=user_id
        )
        
        if services and services[0].duration:
            return services[0].duration
        
    except Exception as e:
        logger.error(f"Error getting service duration: {e}")
    
    # Default duration
    return 30


async def _final_availability_check(
    date_requested: date,
    time_requested: time,
    duration_minutes: int,
    appointment_crud: UserAppointmentCRUD
) -> bool:
    """Final check that the time slot is still available"""
    try:
        existing_appointments, _ = await appointment_crud.get_appointments(
            appointment_date=date_requested,
            status=None,
            limit=100,
            offset=0
        )
        
        requested_start = datetime.combine(date_requested, time_requested)
        requested_end = requested_start + timedelta(minutes=duration_minutes)
        
        for apt in existing_appointments:
            if apt.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS]:
                apt_start = datetime.combine(apt.date, apt.time)
                apt_duration = int(apt.duration.replace("min", "")) if "min" in apt.duration else 30
                apt_end = apt_start + timedelta(minutes=apt_duration)
                
                if (requested_start < apt_end and requested_end > apt_start):
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error in final availability check: {e}")
        return False


def _generate_confirmation_message(
    appointment: Appointment,
    client_name: str,
    appointment_date: date,
    appointment_time: time
) -> str:
    """Generate confirmation message for voice response"""
    
    date_voice = _date_to_voice(appointment_date)
    time_voice = _time_to_voice(appointment_time)
    
    confirmation = f"Perfect! Am programat pe {client_name} {date_voice} la ora {time_voice} pentru {appointment.service}."
    
    # Add duration if available
    if appointment.duration and "min" in appointment.duration:
        duration_min = appointment.duration.replace("min", "")
        confirmation += f" Serviciul durează aproximativ {duration_min} de minute."
    
    # Add final instructions
    confirmation += f" Vă așteptăm! Dacă aveți nevoie să modificați programarea, ne puteți suna oricând."
    
    return confirmation