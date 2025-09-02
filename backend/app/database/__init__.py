# Database operations
from app.database.supabase_client import supabase_manager as database

# Compatibility function for FastAPI dependency injection
async def get_database():
    """Dependency injection for database connection"""
    if not database.is_connected:
        await database.connect()
    return database

__all__ = ['database', 'get_database']