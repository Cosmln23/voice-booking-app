import asyncio
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SupabaseManager:
    """Enhanced Supabase database manager with real-time capabilities"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.service_client: Optional[Client] = None  # For service role operations
        self._connected: bool = False
    
    async def connect(self) -> None:
        """Initialize Supabase connections"""
        try:
            if not settings.supabase_url or not settings.supabase_anon_key:
                logger.warning("Supabase credentials not configured")
                self._connected = False
                return
            
            # Anonymous/public client for standard operations
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            
            # Service role client for admin operations (if available)
            if settings.supabase_service_key:
                self.service_client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_key
                )
            
            # Test connection
            response = self.client.table("business_settings").select("id").limit(1).execute()
            
            self._connected = True
            logger.info("Supabase connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self._connected = False
    
    async def disconnect(self) -> None:
        """Close database connections"""
        if self.client:
            self.client = None
        if self.service_client:
            self.service_client = None
        self._connected = False
        logger.info("Supabase connections closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected
    
    def get_client(self, use_service_role: bool = False) -> Optional[Client]:
        """Get Supabase client instance"""
        if not self._connected:
            return None
        
        if use_service_role and self.service_client:
            return self.service_client
        
        return self.client


# Global Supabase manager instance
supabase_manager = SupabaseManager()


async def get_supabase() -> SupabaseManager:
    """Dependency injection for Supabase connection"""
    if not supabase_manager.is_connected:
        await supabase_manager.connect()
    return supabase_manager