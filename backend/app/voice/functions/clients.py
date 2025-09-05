"""
Voice Tool Function: Client Management
Handles client search and information retrieval for voice interactions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date

from app.core.logging import get_logger
from app.database.user_crud_clients import UserClientCRUD
from app.database.user_crud_appointments import UserAppointmentCRUD
from app.models.client import Client, ClientStatus
from app.models.appointment import AppointmentStatus
from app.voice.functions.auth import get_voice_user_context
from app.voice.functions.errors import VoiceError, handle_voice_error
from app.voice.processing import normalize_phone_from_voice, normalize_name_from_voice

logger = get_logger(__name__)


async def find_existing_client(
    phone: Optional[str] = None,
    client_name: Optional[str] = None,
    supabase_client = None
) -> Dict[str, Any]:
    """
    Voice Tool Function: Find Existing Client
    
    Searches for existing clients by phone number or name.
    Used to retrieve client history before creating appointments.
    
    Args:
        phone: Phone number to search for (primary search method)
        client_name: Client name to search for (secondary method)
        supabase_client: Supabase client instance
    
    Returns:
        Dictionary with client information formatted for voice response
    """
    try:
        logger.info(f"Voice request: find_client, phone={phone}, name={client_name}")
        
        if not phone and not client_name:
            return {
                "success": False,
                "message": "Nu s-au furnizat criterii de căutare",
                "voice_response": "Pentru a căuta un client, am nevoie de numărul de telefon sau numele.",
                "client": None,
                "error_type": "missing_search_criteria"
            }
        
        # Get user context
        user_context = await get_voice_user_context(supabase_client)
        
        # Initialize client CRUD with proper auth format
        # UserClientCRUD expects user_info in dict format
        user_info_dict = {"user_id": user_context["user_id"]}
        client_crud = UserClientCRUD(supabase_client, user_info_dict)
        
        # Search by phone first (most accurate)
        if phone:
            # Use Romanian phone processing
            normalized_phone = normalize_phone_from_voice(phone)
            if not normalized_phone:
                normalized_phone = _normalize_phone_number(phone)  # Fallback
            client_found = await _search_client_by_phone(normalized_phone, client_crud)
            
            if client_found:
                # Get client appointment history
                client_history = await _get_client_history(
                    client_found.id, supabase_client, user_context["user_id"]
                )
                
                voice_response = _format_client_info_voice(client_found, client_history)
                
                return {
                    "success": True,
                    "message": f"Client găsit: {client_found.name}",
                    "voice_response": voice_response,
                    "client": {
                        "id": str(client_found.id),
                        "name": client_found.name,
                        "phone": client_found.phone,
                        "email": client_found.email,
                        "status": client_found.status.value,
                        "total_appointments": client_found.total_appointments,
                        "last_appointment": client_found.last_appointment.isoformat() if client_found.last_appointment else None,
                        "notes": client_found.notes
                    },
                    "history": client_history
                }
        
        # Search by name if phone not provided or not found
        if client_name:
            # Use Romanian name processing
            name_result = normalize_name_from_voice(client_name)
            search_name = name_result.get("normalized", client_name) if name_result.get("success") else client_name
            clients_found = await _search_clients_by_name(search_name, client_crud)
            
            if not clients_found:
                return {
                    "success": False,
                    "message": f"Nu s-a găsit niciun client cu numele {client_name}",
                    "voice_response": f"Nu am găsit niciun client cu numele {client_name}. Doriți să creez o programare nouă?",
                    "client": None,
                    "error_type": "client_not_found"
                }
            
            if len(clients_found) == 1:
                # Single match found
                client = clients_found[0]
                client_history = await _get_client_history(
                    client.id, supabase_client, user_context["user_id"]
                )
                
                voice_response = _format_client_info_voice(client, client_history)
                
                return {
                    "success": True,
                    "message": f"Client găsit: {client.name}",
                    "voice_response": voice_response,
                    "client": {
                        "id": str(client.id),
                        "name": client.name,
                        "phone": client.phone,
                        "email": client.email,
                        "status": client.status.value,
                        "total_appointments": client.total_appointments,
                        "last_appointment": client.last_appointment.isoformat() if client.last_appointment else None,
                        "notes": client.notes
                    },
                    "history": client_history
                }
            
            else:
                # Multiple matches - return options
                voice_response = _format_multiple_clients_voice(clients_found)
                
                return {
                    "success": True,
                    "message": f"Găsiți {len(clients_found)} clienți cu numele similar",
                    "voice_response": voice_response,
                    "client": None,
                    "multiple_matches": [
                        {
                            "id": str(client.id),
                            "name": client.name,
                            "phone": client.phone,
                            "last_appointment": client.last_appointment.isoformat() if client.last_appointment else None
                        }
                        for client in clients_found
                    ],
                    "action_needed": "choose_client"
                }
        
        # No results found
        return {
            "success": False,
            "message": "Client negăsit",
            "voice_response": "Nu am găsit acest client în sistemul nostru. Doriți să creez o programare nouă?",
            "client": None,
            "error_type": "client_not_found"
        }
        
    except VoiceError as ve:
        return handle_voice_error(ve, "find_existing_client")
    except Exception as e:
        logger.error(f"Error in find_existing_client: {e}", exc_info=True)
        return {
            "success": False,
            "message": "Eroare în căutarea clientului",
            "voice_response": "Nu pot căuta clientul în acest moment. Vă rog să îmi spuneți numele și numărul de telefon pentru o programare nouă.",
            "client": None,
            "error_type": "system_error"
        }


async def get_client_appointment_history(
    client_id: str,
    limit: int = 5,
    supabase_client = None
) -> Dict[str, Any]:
    """
    Voice Tool Function: Get Client Appointment History
    
    Retrieves recent appointment history for a specific client.
    
    Args:
        client_id: ID of the client
        limit: Number of recent appointments to retrieve
        supabase_client: Supabase client instance
    
    Returns:
        Dictionary with appointment history formatted for voice response
    """
    try:
        logger.info(f"Voice request: get_client_history, client_id={client_id}")
        
        # Get user context
        user_context = await get_voice_user_context(supabase_client)
        
        # Get appointment history
        history = await _get_client_history(client_id, supabase_client, user_context["user_id"], limit)
        
        if not history:
            return {
                "success": True,
                "message": "Client fără istoric de programări",
                "voice_response": "Acest client nu are încă programări în istoric.",
                "history": []
            }
        
        voice_response = _format_history_voice(history)
        
        return {
            "success": True,
            "message": f"Găsit istoric cu {len(history)} programări",
            "voice_response": voice_response,
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Error in get_client_appointment_history: {e}", exc_info=True)
        return {
            "success": False,
            "message": "Eroare în preluarea istoricului",
            "voice_response": "Nu pot accesa istoricul clientului în acest moment.",
            "history": [],
            "error_type": "system_error"
        }


def _normalize_phone_number(phone: str) -> str:
    """Normalize phone number for search"""
    # Remove all non-digit characters except +
    clean_phone = ''.join(char for char in phone if char.isdigit() or char == '+')
    
    # Handle Romanian numbers
    if clean_phone.startswith('07'):
        clean_phone = '+4' + clean_phone
    elif clean_phone.startswith('4007'):
        clean_phone = '+' + clean_phone
    elif not clean_phone.startswith('+'):
        if len(clean_phone) == 10 and clean_phone.startswith('07'):
            clean_phone = '+4' + clean_phone
        elif len(clean_phone) >= 10:
            clean_phone = '+' + clean_phone
    
    return clean_phone


async def _search_client_by_phone(
    phone: str, 
    client_crud: UserClientCRUD
) -> Optional[Client]:
    """Search for client by exact phone match"""
    try:
        clients, total = await client_crud.get_clients(
            search=phone,
            status=None,  # Search active and inactive
            limit=1,
            offset=0
        )
        
        # Look for exact phone match
        for client in clients:
            if client.phone == phone:
                return client
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching client by phone: {e}")
        return None


async def _search_clients_by_name(
    name: str, 
    client_crud: UserClientCRUD
) -> List[Client]:
    """Search for clients by name (partial match allowed)"""
    try:
        clients, total = await client_crud.get_clients(
            search=name,
            status=ClientStatus.ACTIVE,  # Only active clients for name search
            limit=10,  # Allow multiple matches
            offset=0
        )
        
        # Filter clients that actually match the name
        name_lower = name.lower()
        matching_clients = []
        
        for client in clients:
            if name_lower in client.name.lower():
                matching_clients.append(client)
        
        return matching_clients
        
    except Exception as e:
        logger.error(f"Error searching clients by name: {e}")
        return []


async def _get_client_history(
    client_id: str,
    supabase_client,
    user_id: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Get appointment history for a client"""
    try:
        appointment_crud = UserAppointmentCRUD(supabase_client, user_id)
        
        # Get recent appointments for this client
        # Note: This would require a filter by client_id in the CRUD method
        # For now, we'll get all appointments and filter
        appointments, _ = await appointment_crud.get_appointments(
            appointment_date=None,
            status=None,
            limit=50,  # Get more to filter by client
            offset=0
        )
        
        # Filter by client phone (since we don't have client_id foreign key yet)
        client_appointments = []
        for apt in appointments:
            if hasattr(apt, 'client_id') and str(apt.client_id) == client_id:
                client_appointments.append({
                    "date": apt.date.isoformat(),
                    "time": apt.time.strftime("%H:%M"),
                    "service": apt.service,
                    "status": apt.status.value,
                    "duration": apt.duration,
                    "notes": apt.notes
                })
        
        # Sort by date (newest first) and limit
        client_appointments.sort(key=lambda x: x["date"], reverse=True)
        return client_appointments[:limit]
        
    except Exception as e:
        logger.error(f"Error getting client history: {e}")
        return []


def _format_client_info_voice(client: Client, history: List[Dict]) -> str:
    """Format client information for voice response"""
    
    response = f"Am găsit clientul {client.name}"
    
    if client.phone:
        response += f" cu numărul {client.phone}"
    
    if client.total_appointments:
        if client.total_appointments == 1:
            response += f". Are o programare în istoric"
        else:
            response += f". Are {client.total_appointments} programări în istoric"
    
    if client.last_appointment:
        last_date = client.last_appointment
        if isinstance(last_date, str):
            try:
                last_date = datetime.fromisoformat(last_date).date()
            except:
                last_date = None
        
        if last_date:
            if last_date == date.today():
                response += ", ultima astăzi"
            elif (date.today() - last_date).days == 1:
                response += ", ultima ieri"
            elif (date.today() - last_date).days <= 7:
                response += f", ultima acum {(date.today() - last_date).days} zile"
            else:
                response += f", ultima pe {last_date.strftime('%d.%m.%Y')}"
    
    if client.notes:
        response += f". Note: {client.notes}"
    
    response += ". Doriți să fac o programare nouă pentru acest client?"
    
    return response


def _format_multiple_clients_voice(clients: List[Client]) -> str:
    """Format multiple client matches for voice response"""
    
    if len(clients) == 2:
        response = f"Am găsit doi clienți cu nume similar: {clients[0].name}"
        if clients[0].phone:
            response += f" cu numărul {clients[0].phone}"
        
        response += f" și {clients[1].name}"
        if clients[1].phone:
            response += f" cu numărul {clients[1].phone}"
        
        response += ". Pentru care doriți să fac programarea?"
        
    else:
        response = f"Am găsit {len(clients)} clienți cu nume similar: "
        client_descriptions = []
        
        for client in clients[:3]:  # Limit to first 3 for voice clarity
            desc = client.name
            if client.phone:
                desc += f" ({client.phone})"
            client_descriptions.append(desc)
        
        response += ", ".join(client_descriptions)
        
        if len(clients) > 3:
            response += f" și încă {len(clients) - 3} clienți"
        
        response += ". Vă rog să specificați numărul de telefon pentru identificare precisă."
    
    return response


def _format_history_voice(history: List[Dict]) -> str:
    """Format appointment history for voice response"""
    
    if not history:
        return "Nu am găsit istoric de programări."
    
    if len(history) == 1:
        apt = history[0]
        return f"Ultima programare a fost pe {apt['date']} la {apt['time']} pentru {apt['service']}."
    
    response = f"Ultimele {len(history)} programări: "
    descriptions = []
    
    for apt in history[:3]:  # Limit for voice clarity
        desc = f"{apt['service']} pe {apt['date']}"
        descriptions.append(desc)
    
    response += ", ".join(descriptions)
    
    if len(history) > 3:
        response += f" și încă {len(history) - 3} programări"
    
    return response