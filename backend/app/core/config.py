import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # App configuration
    app_name: str = "Voice Booking App API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase configuration
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_realtime_model: str = "gpt-4o-realtime-preview"
    
    # Google Calendar configuration  
    google_calendar_credentials_b64: Optional[str] = None
    google_calendar_id: str = "primary"
    
    # Session & dialogue configuration
    fsm_session_timeout: int = 300  # 5 minutes
    slot_lock_duration: int = 120   # 2 minutes
    
    # CORS configuration
    cors_origins: list[str] = [
        "http://localhost:3000",  # Next.js dev
        "http://127.0.0.1:3000",  # Alternative localhost
        "https://voice-booking-app.vercel.app",  # Production frontend
        "https://*.vercel.app",  # Vercel preview deployments
        "https://voice-booking-app-*.vercel.app",  # Vercel branch deployments
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()