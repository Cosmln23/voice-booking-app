"""
Base Voice Handler Classes
Provides foundation for all voice processing handlers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.core.logging import get_logger
from app.database.user_crud_appointments import UserAppointmentCRUD
from app.database.user_crud_clients import UserClientCRUD
from app.database.crud_services import ServiceCRUD

logger = get_logger(__name__)


class VoiceHandlerResult(str, Enum):
    """Voice handler result types"""
    SUCCESS = "success"
    ERROR = "error" 
    NEEDS_MORE_INFO = "needs_more_info"
    VALIDATION_ERROR = "validation_error"
    AUTH_ERROR = "auth_error"


class VoiceContext:
    """Voice conversation context"""
    
    def __init__(self, session_id: str, phone_number: str = None, user_crud: UserAppointmentCRUD = None):
        self.session_id = session_id
        self.phone_number = phone_number
        self.user_crud = user_crud
        self.client_crud: Optional[UserClientCRUD] = None
        self.service_crud: Optional[ServiceCRUD] = None
        
        # Conversation state
        self.current_step = "initial"
        self.collected_data: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.last_response: Optional[str] = None
        self.created_at = datetime.now()
        
        # Authentication info
        self.is_authenticated = False
        self.user_info: Optional[Dict[str, Any]] = None

    def add_to_history(self, user_input: str, system_response: str, action: str = None):
        """Add exchange to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "system_response": system_response,
            "action": action,
            "step": self.current_step
        })

    def set_data(self, key: str, value: Any):
        """Set collected data"""
        self.collected_data[key] = value
        logger.debug(f"Voice context data updated: {key} = {value}")

    def get_data(self, key: str, default=None):
        """Get collected data"""
        return self.collected_data.get(key, default)

    def has_required_data(self, required_fields: List[str]) -> tuple[bool, List[str]]:
        """Check if all required fields are collected"""
        missing = [field for field in required_fields if field not in self.collected_data]
        return len(missing) == 0, missing

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transport"""
        return {
            "session_id": self.session_id,
            "phone_number": self.phone_number,
            "current_step": self.current_step,
            "collected_data": self.collected_data,
            "conversation_history": self.conversation_history,
            "is_authenticated": self.is_authenticated,
            "created_at": self.created_at.isoformat()
        }


class VoiceHandlerResponse:
    """Voice handler response"""
    
    def __init__(
        self,
        result: VoiceHandlerResult,
        message_ro: str,
        next_step: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        suggested_response: Optional[str] = None,
        needs_confirmation: bool = False
    ):
        self.result = result
        self.message_ro = message_ro  # Romanian message for TTS
        self.next_step = next_step
        self.data = data or {}
        self.suggested_response = suggested_response
        self.needs_confirmation = needs_confirmation
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "result": self.result.value,
            "message": self.message_ro,
            "next_step": self.next_step,
            "data": self.data,
            "suggested_response": self.suggested_response,
            "needs_confirmation": self.needs_confirmation,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def success(
        cls, 
        message_ro: str, 
        data: Dict[str, Any] = None,
        next_step: str = None
    ) -> 'VoiceHandlerResponse':
        """Create success response"""
        return cls(VoiceHandlerResult.SUCCESS, message_ro, next_step, data)

    @classmethod
    def error(cls, message_ro: str, data: Dict[str, Any] = None) -> 'VoiceHandlerResponse':
        """Create error response"""
        return cls(VoiceHandlerResult.ERROR, message_ro, data=data)

    @classmethod
    def needs_more_info(
        cls, 
        message_ro: str, 
        next_step: str,
        suggested_response: str = None
    ) -> 'VoiceHandlerResponse':
        """Create needs more info response"""
        return cls(
            VoiceHandlerResult.NEEDS_MORE_INFO, 
            message_ro, 
            next_step=next_step,
            suggested_response=suggested_response
        )

    @classmethod
    def validation_error(cls, message_ro: str, data: Dict[str, Any] = None) -> 'VoiceHandlerResponse':
        """Create validation error response"""
        return cls(VoiceHandlerResult.VALIDATION_ERROR, message_ro, data=data)


class BaseVoiceHandler(ABC):
    """Base class for all voice handlers"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.required_fields: List[str] = []
        self.handler_name = self.__class__.__name__

    @abstractmethod
    async def process(self, user_input: str, context: VoiceContext) -> VoiceHandlerResponse:
        """Process user input and return response"""
        pass

    @abstractmethod
    def can_handle(self, user_input: str, context: VoiceContext) -> bool:
        """Determine if this handler can process the input"""
        pass

    async def validate_input(self, user_input: str, context: VoiceContext) -> tuple[bool, Optional[str]]:
        """Validate user input for this handler"""
        if not user_input or not user_input.strip():
            return False, "Input-ul nu poate fi gol"
        
        return True, None

    async def extract_data(self, user_input: str, context: VoiceContext) -> Dict[str, Any]:
        """Extract structured data from user input"""
        return {}

    def log_activity(self, activity: str, context: VoiceContext, extra_data: Dict[str, Any] = None):
        """Log handler activity"""
        log_data = {
            "handler": self.handler_name,
            "session_id": context.session_id,
            "step": context.current_step,
            "activity": activity
        }
        
        if extra_data:
            log_data.update(extra_data)
            
        self.logger.info(f"Voice Handler Activity: {activity}", extra=log_data)


class VoiceFlowManager:
    """Manages voice conversation flow between handlers"""
    
    def __init__(self):
        self.handlers: Dict[str, BaseVoiceHandler] = {}
        self.logger = get_logger(__name__)
        
    def register_handler(self, step_name: str, handler: BaseVoiceHandler):
        """Register a handler for a specific step"""
        self.handlers[step_name] = handler
        self.logger.debug(f"Registered voice handler: {step_name}")
        
    async def process_input(self, user_input: str, context: VoiceContext) -> VoiceHandlerResponse:
        """Process user input through appropriate handler"""
        try:
            # Find appropriate handler
            handler = None
            
            # First try current step handler
            if context.current_step in self.handlers:
                current_handler = self.handlers[context.current_step]
                if current_handler.can_handle(user_input, context):
                    handler = current_handler
            
            # If no current step handler, find any handler that can process
            if not handler:
                for step_name, step_handler in self.handlers.items():
                    if step_handler.can_handle(user_input, context):
                        handler = step_handler
                        context.current_step = step_name
                        break
            
            if not handler:
                return VoiceHandlerResponse.error(
                    "Ne pare rău, nu am înțeles cererea dumneavoastră. Puteți să reformulați?"
                )
            
            # Process with selected handler
            response = await handler.process(user_input, context)
            
            # Update context
            if response.next_step:
                context.current_step = response.next_step
            
            context.last_response = response.message_ro
            context.add_to_history(user_input, response.message_ro, response.result.value)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing voice input: {e}", exc_info=True)
            return VoiceHandlerResponse.error(
                "A apărut o problemă tehnică. Vă rugăm să încercați din nou."
            )