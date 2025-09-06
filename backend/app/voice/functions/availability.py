"""
Voice Tool Function: Appointment Availability
Handles availability checking and time slot management for voice bookings
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, time, timedelta
from dateutil.parser import parse as parse_date

from app.core.logging import get_logger
from app.database.user_crud_appointments import UserAppointmentCRUD
from app.database.crud_business_settings import BusinessSettingsCRUD
from app.models.appointment import AppointmentStatus
from app.voice.functions.auth import get_voice_user_context
from app.voice.functions.errors import VoiceError, handle_voice_error
from app.services.calendar_service import check_calendar_availability

logger = get_logger(__name__)


async def check_appointment_availability(
    date_requested: str,  # "2024-09-05" or "mâine" or "joi"
    time_requested: Optional[str] = None,  # "10:00" or "dimineața"
    duration_minutes: Optional[int] = None,  # Duration in minutes
    supabase_client = None
) -> Dict[str, Any]:
    """
    Voice Tool Function: Check Appointment Availability
    
    Checks if a specific date/time is available for booking.
    Handles natural language date/time input from voice.
    
    Args:
        date_requested: Date in various formats ("2024-09-05", "mâine", "joi")
        time_requested: Time in various formats ("10:00", "dimineața") 
        duration_minutes: Service duration in minutes
        supabase_client: Supabase client instance
    
    Returns:
        Dictionary with availability info formatted for voice response
    """
    try:
        logger.info(f"Voice request: check_availability, date={date_requested}, time={time_requested}, duration={duration_minutes}")
        
        # Get user context
        user_context = await get_voice_user_context(supabase_client)
        
        # Parse the requested date
        try:
            parsed_date = await _parse_voice_date(date_requested)
        except ValueError as e:
            return {
                "success": False,
                "message": f"Nu înțeleg data: {date_requested}",
                "voice_response": f"Nu înțeleg ce dată doriți. Vă rog să specificați o dată validă.",
                "available": False,
                "error_type": "invalid_date"
            }
        
        # Check if date is in the past
        if parsed_date < date.today():
            return {
                "success": False,
                "message": "Data solicitată este în trecut",
                "voice_response": "Nu pot programa în trecut. Vă rog să alegeți o dată din viitor.",
                "available": False,
                "error_type": "past_date"
            }
        
        # Get business working hours
        business_crud = BusinessSettingsCRUD(supabase_client)
        working_hours = await business_crud.get_working_hours()
        
        # Check if date falls on a working day
        weekday = parsed_date.weekday()  # Monday=0, Sunday=6
        if not _is_working_day(weekday, working_hours):
            weekday_names = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
            day_name = weekday_names[weekday]
            return {
                "success": False,
                "message": f"Nu lucrăm în ziua de {day_name}",
                "voice_response": f"Ne pare rău, nu lucrăm în ziua de {day_name}. Programăm doar în zilele lucrătoare.",
                "available": False,
                "error_type": "non_working_day",
                "requested_date": parsed_date.isoformat()
            }
        
        # Initialize appointments CRUD
        appointment_crud = UserAppointmentCRUD(supabase_client, user_context["user_id"])
        
        # If specific time requested, check that slot
        if time_requested:
            try:
                parsed_time = await _parse_voice_time(time_requested)
                is_available = await _check_specific_slot(
                    parsed_date, parsed_time, duration_minutes or 30,
                    appointment_crud, working_hours, weekday,
                    user_context["user_id"]
                )
                
                if is_available:
                    time_str = parsed_time.strftime("%H:%M")
                    return {
                        "success": True,
                        "message": f"Disponibil pe {parsed_date.strftime('%d.%m.%Y')} la {time_str}",
                        "voice_response": f"Da, avem liber pe {_date_to_voice(parsed_date)} la ora {_time_to_voice(parsed_time)}.",
                        "available": True,
                        "date": parsed_date.isoformat(),
                        "time": time_str,
                        "duration_minutes": duration_minutes
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Ocupat pe {parsed_date.strftime('%d.%m.%Y')} la {parsed_time.strftime('%H:%M')}",
                        "voice_response": f"Ne pare rău, la ora {_time_to_voice(parsed_time)} este ocupat. Vă pot propune o altă oră?",
                        "available": False,
                        "date": parsed_date.isoformat(),
                        "time": parsed_time.strftime("%H:%M"),
                        "error_type": "time_occupied"
                    }
                    
            except ValueError:
                # Invalid time format - suggest available slots instead
                available_slots = await _get_available_slots(
                    parsed_date, appointment_crud, working_hours, weekday, duration_minutes or 30,
                    user_context["user_id"]
                )
                return {
                    "success": True,
                    "message": f"Orele disponibile pentru {parsed_date.strftime('%d.%m.%Y')}",
                    "voice_response": _format_available_slots_voice(available_slots, parsed_date),
                    "available": True,
                    "date": parsed_date.isoformat(),
                    "available_slots": [slot.strftime("%H:%M") for slot in available_slots],
                    "total_slots": len(available_slots)
                }
        else:
            # No specific time - return available slots for the day
            available_slots = await _get_available_slots(
                parsed_date, appointment_crud, working_hours, weekday, duration_minutes or 30,
                user_context["user_id"]
            )
            
            if not available_slots:
                return {
                    "success": False,
                    "message": f"Nu avem locuri libere pe {parsed_date.strftime('%d.%m.%Y')}",
                    "voice_response": f"Ne pare rău, pe {_date_to_voice(parsed_date)} nu mai avem locuri libere. Doriți să încercăm o altă zi?",
                    "available": False,
                    "date": parsed_date.isoformat(),
                    "error_type": "fully_booked"
                }
            
            return {
                "success": True,
                "message": f"Găsite {len(available_slots)} intervale libere",
                "voice_response": _format_available_slots_voice(available_slots, parsed_date),
                "available": True,
                "date": parsed_date.isoformat(),
                "available_slots": [slot.strftime("%H:%M") for slot in available_slots],
                "total_slots": len(available_slots)
            }
        
    except VoiceError as ve:
        return handle_voice_error(ve, "check_appointment_availability")
    except Exception as e:
        logger.error(f"Error in check_appointment_availability: {e}", exc_info=True)
        return {
            "success": False,
            "message": "Eroare în verificarea disponibilității",
            "voice_response": "Nu pot verifica disponibilitatea în acest moment. Vă rog să încercați din nou.",
            "available": False,
            "error_type": "system_error"
        }


async def _parse_voice_date(date_str: str) -> date:
    """Parse various date formats from voice input"""
    date_str = date_str.lower().strip()
    today = date.today()
    
    # Natural language dates
    if date_str in ["astăzi", "azi"]:
        return today
    elif date_str in ["mâine", "maine"]:
        return today + timedelta(days=1)
    elif date_str in ["poimâine", "poimaine"]:
        return today + timedelta(days=2)
    
    # Weekday names
    weekdays = {
        "luni": 0, "marți": 1, "marti": 1, "miercuri": 2, 
        "joi": 3, "vineri": 4, "sâmbătă": 5, "sambata": 5, "duminică": 6, "duminica": 6
    }
    
    if date_str in weekdays:
        target_weekday = weekdays[date_str]
        current_weekday = today.weekday()
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    # Try to parse standard date formats
    try:
        if "-" in date_str:  # YYYY-MM-DD
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        elif "." in date_str:  # DD.MM.YYYY or DD.MM
            parts = date_str.split(".")
            if len(parts) == 2:  # DD.MM (assume current year)
                return datetime.strptime(f"{date_str}.{today.year}", "%d.%m.%Y").date()
            else:  # DD.MM.YYYY
                return datetime.strptime(date_str, "%d.%m.%Y").date()
        elif "/" in date_str:  # DD/MM/YYYY or MM/DD/YYYY
            return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        pass
    
    raise ValueError(f"Cannot parse date: {date_str}")


async def _parse_voice_time(time_str: str) -> time:
    """Parse various time formats from voice input"""
    time_str = time_str.lower().strip()
    
    # Natural language times
    if time_str in ["dimineața", "dimineata", "dimineață"]:
        return time(9, 0)  # Default morning time
    elif time_str in ["prânz", "prinz", "amiaza"]:
        return time(12, 0)
    elif time_str in ["după-amiaza", "dupa-amiaza", "seara"]:
        return time(15, 0)
    
    # Try to parse standard time formats
    try:
        if ":" in time_str:  # HH:MM
            return datetime.strptime(time_str, "%H:%M").time()
        elif len(time_str) <= 2:  # Just hour (HH)
            hour = int(time_str)
            if hour < 24:
                return time(hour, 0)
    except ValueError:
        pass
    
    raise ValueError(f"Cannot parse time: {time_str}")


def _is_working_day(weekday: int, working_hours) -> bool:
    """Check if a weekday is a working day"""
    # working_hours is now a List[WorkingHours] Pydantic models
    for hours in working_hours:
        if hours.day_of_week == weekday and not hours.is_closed:
            return True
    return False


async def _check_specific_slot(
    date_requested: date,
    time_requested: time,
    duration_minutes: int,
    appointment_crud: UserAppointmentCRUD,
    working_hours: List[Dict],
    weekday: int,
    user_id: Optional[str] = None
) -> bool:
    """Check if a specific time slot is available"""
    
    # Check if time falls within working hours
    working_day = next((h for h in working_hours if h.day_of_week == weekday), None)
    if not working_day or working_day.is_closed:
        return False
    
    start_time = working_day.start_time
    end_time = working_day.end_time
    
    if time_requested < start_time or time_requested >= end_time:
        return False
    
    # Check for existing appointments
    existing_appointments, _ = await appointment_crud.get_appointments(
        appointment_date=date_requested,
        status=None,  # Check all active statuses
        limit=100,
        offset=0
    )
    
    # Check for time conflicts with database appointments
    requested_start = datetime.combine(date_requested, time_requested)
    requested_end = requested_start + timedelta(minutes=duration_minutes)
    
    for apt in existing_appointments:
        if apt.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS]:
            apt_start = datetime.combine(apt.date, apt.time)
            apt_duration = int(apt.duration.replace("min", "")) if "min" in apt.duration else 30
            apt_end = apt_start + timedelta(minutes=apt_duration)
            
            # Check overlap
            if (requested_start < apt_end and requested_end > apt_start):
                return False
    
    # CRITICAL: Check Google Calendar availability with user isolation
    try:
        calendar_available = await check_calendar_availability(
            requested_start, 
            duration_minutes,
            user_id=user_id
        )
    except Exception as e:
        logger.warning(f"Could not check calendar availability: {e}")
        calendar_available = True  # Don't block booking if calendar check fails
    
    if not calendar_available:
        logger.info(f"Time slot {requested_start} blocked by Google Calendar event")
        return False
    
    return True


async def _get_available_slots(
    date_requested: date,
    appointment_crud: UserAppointmentCRUD,
    working_hours: List[Dict],
    weekday: int,
    duration_minutes: int,
    user_id: Optional[str] = None,
    slot_interval: int = 30  # 30-minute intervals
) -> List[time]:
    """Get all available time slots for a given date"""
    
    # Get working hours for the day
    working_day = next((h for h in working_hours if h.day_of_week == weekday), None)
    if not working_day or working_day.is_closed:
        return []
    
    start_time = working_day.start_time
    end_time = working_day.end_time
    
    # Get existing appointments
    existing_appointments, _ = await appointment_crud.get_appointments(
        appointment_date=date_requested,
        status=None,
        limit=100,
        offset=0
    )
    
    # Generate potential slots
    available_slots = []
    current_time = datetime.combine(date_requested, start_time)
    end_datetime = datetime.combine(date_requested, end_time)
    
    while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=duration_minutes)
        
        # Check if slot conflicts with existing appointments
        is_free = True
        for apt in existing_appointments:
            if apt.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS]:
                apt_start = datetime.combine(apt.date, apt.time)
                apt_duration = int(apt.duration.replace("min", "")) if "min" in apt.duration else 30
                apt_end = apt_start + timedelta(minutes=apt_duration)
                
                if (slot_start < apt_end and slot_end > apt_start):
                    is_free = False
                    break
        
        # Check calendar availability if business has calendar integration
        if is_free and user_id:
            try:
                calendar_available = await check_calendar_availability(
                    slot_start, 
                    duration_minutes,
                    user_id=user_id
                )
                if not calendar_available:
                    is_free = False
            except Exception as e:
                logger.warning(f"Could not check calendar availability for slot {slot_start}: {e}")
                # Don't block slot if calendar check fails
        
        if is_free:
            available_slots.append(current_time.time())
        
        current_time += timedelta(minutes=slot_interval)
    
    return available_slots


def _date_to_voice(date_obj: date) -> str:
    """Convert date to voice-friendly Romanian format"""
    weekdays = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
    months = [
        "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
        "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"
    ]
    
    weekday_name = weekdays[date_obj.weekday()]
    month_name = months[date_obj.month - 1]
    
    today = date.today()
    if date_obj == today:
        return "astăzi"
    elif date_obj == today + timedelta(days=1):
        return "mâine"
    else:
        return f"{weekday_name}, {date_obj.day} {month_name}"


def _time_to_voice(time_obj: time) -> str:
    """Convert time to voice-friendly Romanian format"""
    hour = time_obj.hour
    minute = time_obj.minute
    
    if minute == 0:
        return f"{hour}"
    elif minute == 30:
        return f"{hour} și jumătate"
    else:
        return f"{hour}:{minute:02d}"


def _format_available_slots_voice(slots: List[time], date_obj: date) -> str:
    """Format available slots for voice response"""
    if not slots:
        return f"Nu avem locuri libere pe {_date_to_voice(date_obj)}."
    
    date_voice = _date_to_voice(date_obj)
    
    if len(slots) == 1:
        return f"Pe {date_voice} avem liber la ora {_time_to_voice(slots[0])}."
    elif len(slots) <= 3:
        slot_times = [_time_to_voice(slot) for slot in slots]
        return f"Pe {date_voice} avem liber la orele: {', '.join(slot_times[:-1])} și {slot_times[-1]}."
    else:
        first_slots = [_time_to_voice(slot) for slot in slots[:3]]
        return f"Pe {date_voice} avem multe ore libere, inclusiv: {', '.join(first_slots)} și alte {len(slots) - 3} intervale."