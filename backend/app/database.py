import asyncio
from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Database:
    """Supabase database connection manager"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._connected: bool = False
    
    async def connect(self) -> None:
        """Initialize Supabase connection"""
        try:
            if not settings.supabase_url or not settings.supabase_anon_key:
                logger.warning("Supabase credentials not configured, using mock mode")
                self._connected = False
                return
                
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            
            # Test connection with a simple query
            response = self.client.table("clients").select("id").limit(1).execute()
            
            self._connected = True
            logger.info("Supabase connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}", extra={"error": str(e)})
            self._connected = False
    
    async def disconnect(self) -> None:
        """Close database connection"""
        if self.client:
            self.client = None
            self._connected = False
            logger.info("Database connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected
    
    def get_client(self) -> Optional[Client]:
        """Get Supabase client instance"""
        return self.client if self._connected else None


# Global database instance
database = Database()


async def get_database() -> Database:
    """Dependency injection for database connection"""
    if not database.is_connected:
        await database.connect()
    return database