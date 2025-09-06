"""
Calendar Settings Models
Pydantic models for business calendar configuration
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime
import json


class GoogleCalendarCredentials(BaseModel):
    """Google Calendar Service Account Credentials"""
    
    type: str = "service_account"
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url: str
    
    @validator('private_key')
    def validate_private_key(cls, v):
        """Ensure private key has proper format"""
        if not v.startswith('-----BEGIN PRIVATE KEY-----'):
            raise ValueError('Invalid private key format')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for Google API"""
        return self.dict()


class CalendarSettings(BaseModel):
    """Calendar configuration for business"""
    
    google_calendar_enabled: bool = False
    google_calendar_id: Optional[str] = None
    google_calendar_name: Optional[str] = None
    google_calendar_credentials: Optional[GoogleCalendarCredentials] = None
    google_calendar_timezone: str = "Europe/Bucharest"
    auto_create_events: bool = True
    sync_bidirectional: bool = False
    
    # Calendar sharing settings
    calendar_shared_with: Optional[list] = []  # Email addresses with access
    calendar_permissions: str = "editor"  # reader, editor, owner
    
    # Advanced settings
    event_color_id: str = "2"  # Green for appointments
    reminder_minutes: list = [1440, 30]  # 1 day, 30 min before
    
    # Metadata
    calendar_created_at: Optional[datetime] = None
    calendar_last_sync: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def is_fully_configured(self) -> bool:
        """Check if calendar is fully configured"""
        return (
            self.google_calendar_enabled and 
            self.google_calendar_id and 
            self.google_calendar_credentials is not None
        )


class CalendarSetupRequest(BaseModel):
    """Request model for calendar setup"""
    
    calendar_name: str
    google_calendar_id: str
    google_calendar_credentials_json: str  # Base64 encoded or raw JSON
    timezone: str = "Europe/Bucharest"
    auto_create_events: bool = True
    
    @validator('google_calendar_credentials_json')
    def validate_credentials_json(cls, v):
        """Validate credentials JSON"""
        try:
            if v.startswith('eyJ'):  # Base64 encoded
                import base64
                decoded = base64.b64decode(v).decode('utf-8')
                json.loads(decoded)
            else:  # Raw JSON
                json.loads(v)
            return v
        except (json.JSONDecodeError, Exception):
            raise ValueError('Invalid JSON credentials format')


class CalendarSyncStatus(BaseModel):
    """Calendar synchronization status"""
    
    business_id: str
    calendar_id: str
    is_enabled: bool
    last_sync: Optional[datetime] = None
    sync_status: str = "never"  # never, success, error, in_progress
    events_synced: int = 0
    last_error: Optional[str] = None
    
    # Statistics
    total_appointments: int = 0
    calendar_events_created: int = 0
    sync_conflicts: int = 0