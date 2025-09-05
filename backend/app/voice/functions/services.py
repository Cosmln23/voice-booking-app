"""
Voice Tool Function: Services Management
Handles service-related voice commands and queries
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.logging import get_logger
from app.database.crud_services import ServiceCRUD
from app.models.service import ServiceStatus
from app.voice.functions.auth import get_voice_user_context
from app.voice.functions.errors import VoiceError, handle_voice_error

logger = get_logger(__name__)


async def get_available_services(
    category: Optional[str] = None,
    supabase_client = None
) -> Dict[str, Any]:
    """
    Voice Tool Function: Get Available Services
    
    Retrieves all available services for voice booking.
    Used by OpenAI Realtime API as a tool function.
    
    Args:
        category: Optional service category filter ("tuns", "barba", "styling", etc.)
        supabase_client: Supabase client instance (injected by voice handler)
    
    Returns:
        Dictionary with services list formatted for voice response
    """
    try:
        logger.info(f"Voice request: get_available_services, category={category}")
        
        # Get user context for voice session (business owner context)
        user_context = await get_voice_user_context(supabase_client)
        
        # Initialize services CRUD
        service_crud = ServiceCRUD(supabase_client)
        
        # Fetch services (ServiceCRUD doesn't have user_id parameter)
        services_list, total = await service_crud.get_services(
            category=category,
            status=ServiceStatus.ACTIVE,
            limit=50,
            offset=0
        )
        
        if not services_list:
            return {
                "success": False,
                "message": "Nu avem servicii disponibile în acest moment.",
                "voice_response": "În acest moment nu avem servicii disponibile.",
                "services": [],
                "total": 0
            }
        
        # Format services for voice response
        voice_services = []
        voice_text_parts = []
        
        for service in services_list:
            service_info = {
                "name": service.name,
                "category": service.category,
                "duration": service.duration,
                "price": service.price,
                "description": service.description
            }
            voice_services.append(service_info)
            
            # Build voice-friendly description
            price_text = f"{service.price} lei" if service.price else "preț la cerere"
            duration_text = f"{service.duration} minute" if service.duration else "durată variabilă"
            voice_text_parts.append(
                f"{service.name} - {duration_text}, {price_text}"
            )
        
        # Create voice response text
        if len(voice_services) == 1:
            voice_response = f"Avem disponibil serviciul: {voice_text_parts[0]}."
        elif len(voice_services) <= 3:
            voice_response = f"Avem disponibile următoarele servicii: {', '.join(voice_text_parts[:-1])} și {voice_text_parts[-1]}."
        else:
            main_services = voice_text_parts[:3]
            voice_response = f"Avem disponibile servicii precum: {', '.join(main_services)} și încă {len(voice_services) - 3} servicii."
        
        logger.info(f"Voice response: found {total} services, returning {len(voice_services)}")
        
        return {
            "success": True,
            "message": f"Găsite {total} servicii disponibile",
            "voice_response": voice_response,
            "services": voice_services,
            "total": total,
            "category_filter": category
        }
        
    except VoiceError as ve:
        return handle_voice_error(ve, "get_available_services")
    except Exception as e:
        logger.error(f"Error in get_available_services: {e}", exc_info=True)
        return {
            "success": False,
            "message": "Eroare în preluarea serviciilor",
            "voice_response": "Ne pare rău, nu pot accesa lista serviciilor în acest moment. Vă rog să încercați din nou.",
            "services": [],
            "total": 0,
            "error_type": "system_error"
        }


async def get_service_details(
    service_name: str,
    supabase_client = None
) -> Dict[str, Any]:
    """
    Voice Tool Function: Get Service Details
    
    Gets detailed information about a specific service.
    
    Args:
        service_name: Name of the service to get details for
        supabase_client: Supabase client instance
    
    Returns:
        Dictionary with service details formatted for voice response
    """
    try:
        logger.info(f"Voice request: get_service_details, service={service_name}")
        
        # Get user context
        user_context = await get_voice_user_context(supabase_client)
        
        # Initialize services CRUD
        service_crud = ServiceCRUD(supabase_client)
        
        # Search for service by name
        services_list, total = await service_crud.get_services(
            # search=service_name,  # ServiceCRUD doesn't have search parameter
            status=ServiceStatus.ACTIVE,
            limit=50,  # Get all and filter manually
            offset=0
        )
        
        # Manual search filtering
        if service_name:
            services_list = [s for s in services_list if service_name.lower() in s.name.lower()]
            total = len(services_list)
            services_list = services_list[:1]  # Take first match
        
        if not services_list:
            return {
                "success": False,
                "message": f"Nu s-a găsit serviciul: {service_name}",
                "voice_response": f"Nu am găsit serviciul {service_name}. Doriți să vă spun ce servicii avem disponibile?",
                "service": None
            }
        
        service = services_list[0]
        
        # Format for voice response
        price_text = f"{service.price} lei" if service.price else "preț la cerere"
        duration_text = f"{service.duration} minute" if service.duration else "durată variabilă"
        
        voice_response = f"Serviciul {service.name} durează {duration_text} și costă {price_text}."
        if service.description:
            voice_response += f" {service.description}"
        
        return {
            "success": True,
            "message": f"Detalii pentru serviciul {service.name}",
            "voice_response": voice_response,
            "service": {
                "name": service.name,
                "category": service.category,
                "duration": service.duration,
                "price": service.price,
                "description": service.description,
                "status": service.status.value
            }
        }
        
    except VoiceError as ve:
        return handle_voice_error(ve, "get_service_details")
    except Exception as e:
        logger.error(f"Error in get_service_details: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Eroare în preluarea detaliilor serviciului {service_name}",
            "voice_response": "Nu pot accesa detaliile serviciului în acest moment.",
            "service": None,
            "error_type": "system_error"
        }