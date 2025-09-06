"""
Calendar Settings CRUD Operations
Manages business-specific calendar configurations in database
"""

import json
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from supabase import Client
from cryptography.fernet import Fernet

from app.models.calendar_settings import CalendarSettings, GoogleCalendarCredentials, CalendarSyncStatus
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CalendarSettingsCRUD:
    """CRUD operations for business calendar settings"""
    
    def __init__(self, client: Client):
        self.client = client
        self.table = "business_calendar_settings"
        
        # Initialize encryption for credentials
        # In production, use a proper key management system
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key) if self.encryption_key else None
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Get encryption key for credentials"""
        try:
            # Use a key from environment or generate one
            # In production, use proper key management
            key_str = getattr(settings, 'calendar_encryption_key', None)
            if key_str:
                return key_str.encode()
            else:
                # Generate a key for development (not recommended for production)
                return Fernet.generate_key()
        except Exception as e:
            logger.warning(f"Could not setup encryption: {e}")
            return None
    
    def _encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Encrypt calendar credentials"""
        try:
            if self.cipher_suite:
                credentials_json = json.dumps(credentials)
                encrypted = self.cipher_suite.encrypt(credentials_json.encode())
                return base64.b64encode(encrypted).decode()
            else:
                # Fallback: Base64 encoding (not secure, for development only)
                credentials_json = json.dumps(credentials)
                return base64.b64encode(credentials_json.encode()).decode()
        except Exception as e:
            logger.error(f"Error encrypting credentials: {e}")
            raise
    
    def _decrypt_credentials(self, encrypted_credentials: str) -> Dict[str, Any]:
        """Decrypt calendar credentials"""
        try:
            if self.cipher_suite:
                encrypted_data = base64.b64decode(encrypted_credentials.encode())
                decrypted = self.cipher_suite.decrypt(encrypted_data)
                return json.loads(decrypted.decode())
            else:
                # Fallback: Base64 decoding
                decoded = base64.b64decode(encrypted_credentials.encode())
                return json.loads(decoded.decode())
        except Exception as e:
            logger.error(f"Error decrypting credentials: {e}")
            raise
    
    async def get_calendar_settings(self, user_id: str) -> Optional[CalendarSettings]:
        """Get calendar settings for business"""
        try:
            response = self.client.table(self.table)\
                .select("*")\
                .eq("user_id", user_id)\
                .limit(1)\
                .execute()
            
            if not response.data:
                return None
            
            row = response.data[0]
            
            # Decrypt credentials if present
            credentials = None
            if row.get("google_calendar_credentials_encrypted"):
                try:
                    credentials_dict = self._decrypt_credentials(
                        row["google_calendar_credentials_encrypted"]
                    )
                    credentials = GoogleCalendarCredentials(**credentials_dict)
                except Exception as e:
                    logger.error(f"Error loading credentials for user {user_id}: {e}")
            
            # Convert to CalendarSettings model
            settings_data = {
                "google_calendar_enabled": row.get("google_calendar_enabled", False),
                "google_calendar_id": row.get("google_calendar_id"),
                "google_calendar_name": row.get("google_calendar_name"),
                "google_calendar_credentials": credentials,
                "google_calendar_timezone": row.get("google_calendar_timezone", "Europe/Bucharest"),
                "auto_create_events": row.get("auto_create_events", True),
                "sync_bidirectional": row.get("sync_bidirectional", False),
                "calendar_shared_with": row.get("calendar_shared_with", []),
                "calendar_permissions": row.get("calendar_permissions", "editor"),
                "event_color_id": row.get("event_color_id", "2"),
                "reminder_minutes": row.get("reminder_minutes", [1440, 30]),
                "calendar_created_at": row.get("calendar_created_at"),
                "calendar_last_sync": row.get("calendar_last_sync")
            }
            
            return CalendarSettings(**settings_data)
            
        except Exception as e:
            logger.error(f"Error getting calendar settings for user {user_id}: {e}")
            return None
    
    async def create_calendar_settings(
        self, 
        user_id: str, 
        settings: CalendarSettings
    ) -> bool:
        """Create new calendar settings for business"""
        try:
            # Encrypt credentials
            encrypted_credentials = None
            if settings.google_calendar_credentials:
                encrypted_credentials = self._encrypt_credentials(
                    settings.google_calendar_credentials.to_dict()
                )
            
            # Prepare data for database
            data = {
                "user_id": user_id,
                "google_calendar_enabled": settings.google_calendar_enabled,
                "google_calendar_id": settings.google_calendar_id,
                "google_calendar_name": settings.google_calendar_name,
                "google_calendar_credentials_encrypted": encrypted_credentials,
                "google_calendar_timezone": settings.google_calendar_timezone,
                "auto_create_events": settings.auto_create_events,
                "sync_bidirectional": settings.sync_bidirectional,
                "calendar_shared_with": settings.calendar_shared_with,
                "calendar_permissions": settings.calendar_permissions,
                "event_color_id": settings.event_color_id,
                "reminder_minutes": settings.reminder_minutes,
                "calendar_created_at": datetime.utcnow().isoformat(),
                "calendar_last_sync": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table).insert(data).execute()
            
            if response.data:
                logger.info(f"Calendar settings created for user {user_id}")
                return True
            else:
                logger.error(f"Failed to create calendar settings for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating calendar settings for user {user_id}: {e}")
            return False
    
    async def update_calendar_settings(
        self, 
        user_id: str, 
        settings: CalendarSettings
    ) -> bool:
        """Update calendar settings for business"""
        try:
            # Encrypt credentials
            encrypted_credentials = None
            if settings.google_calendar_credentials:
                encrypted_credentials = self._encrypt_credentials(
                    settings.google_calendar_credentials.to_dict()
                )
            
            # Prepare update data
            data = {
                "google_calendar_enabled": settings.google_calendar_enabled,
                "google_calendar_id": settings.google_calendar_id,
                "google_calendar_name": settings.google_calendar_name,
                "google_calendar_timezone": settings.google_calendar_timezone,
                "auto_create_events": settings.auto_create_events,
                "sync_bidirectional": settings.sync_bidirectional,
                "calendar_shared_with": settings.calendar_shared_with,
                "calendar_permissions": settings.calendar_permissions,
                "event_color_id": settings.event_color_id,
                "reminder_minutes": settings.reminder_minutes,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Only update credentials if provided
            if encrypted_credentials:
                data["google_calendar_credentials_encrypted"] = encrypted_credentials
            
            response = self.client.table(self.table)\
                .update(data)\
                .eq("user_id", user_id)\
                .execute()
            
            if response.data:
                logger.info(f"Calendar settings updated for user {user_id}")
                return True
            else:
                logger.error(f"Failed to update calendar settings for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating calendar settings for user {user_id}: {e}")
            return False
    
    async def delete_calendar_settings(self, user_id: str) -> bool:
        """Delete calendar settings for business"""
        try:
            response = self.client.table(self.table)\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            
            logger.info(f"Calendar settings deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting calendar settings for user {user_id}: {e}")
            return False
    
    async def update_sync_status(
        self, 
        user_id: str, 
        status: CalendarSyncStatus
    ) -> bool:
        """Update calendar sync status"""
        try:
            data = {
                "calendar_last_sync": status.last_sync.isoformat() if status.last_sync else None,
                "sync_status": status.sync_status,
                "events_synced": status.events_synced,
                "sync_conflicts": status.sync_conflicts,
                "last_sync_error": status.last_error,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table)\
                .update(data)\
                .eq("user_id", user_id)\
                .execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error updating sync status for user {user_id}: {e}")
            return False
    
    async def get_all_enabled_calendars(self) -> List[Dict[str, Any]]:
        """Get all businesses with enabled calendars"""
        try:
            response = self.client.table(self.table)\
                .select("user_id, google_calendar_id, google_calendar_name")\
                .eq("google_calendar_enabled", True)\
                .execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting enabled calendars: {e}")
            return []


# Database table creation SQL (for reference)
CALENDAR_SETTINGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS business_calendar_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Calendar configuration
    google_calendar_enabled BOOLEAN DEFAULT FALSE,
    google_calendar_id VARCHAR(255),
    google_calendar_name VARCHAR(255),
    google_calendar_credentials_encrypted TEXT,
    google_calendar_timezone VARCHAR(100) DEFAULT 'Europe/Bucharest',
    
    -- Features
    auto_create_events BOOLEAN DEFAULT TRUE,
    sync_bidirectional BOOLEAN DEFAULT FALSE,
    
    -- Sharing settings
    calendar_shared_with JSONB DEFAULT '[]',
    calendar_permissions VARCHAR(50) DEFAULT 'editor',
    
    -- Event settings
    event_color_id VARCHAR(10) DEFAULT '2',
    reminder_minutes JSONB DEFAULT '[1440, 30]',
    
    -- Sync status
    calendar_created_at TIMESTAMP WITH TIME ZONE,
    calendar_last_sync TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) DEFAULT 'never',
    events_synced INTEGER DEFAULT 0,
    sync_conflicts INTEGER DEFAULT 0,
    last_sync_error TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id)
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_calendar_settings_user_id ON business_calendar_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_settings_enabled ON business_calendar_settings(google_calendar_enabled);
"""