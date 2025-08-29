"""
Configuration settings for the Setlist application.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Setlist"
    
    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_RELOAD: bool = True
    BACKEND_LOG_LEVEL: str = "info"
    
    # CORS Configuration
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres.vtoxkfrkpzwotgvsigrw:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    
    # Supabase Configuration
    SUPABASE_URL: str = "https://vtoxkfrkpzwotgvsigrw.supabase.co"
    SUPABASE_API_KEY: str = "sb_publishable__6mwT6WNeD6raZ-9-hU99g_8WBEeDGB"
    SUPABASE_SECRET_KEY: str = "sb_secret_QzFHoXCLuWM2huhnECOZ9g__gTYuZZK"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads/"
    ALLOWED_AUDIO_EXTENSIONS: List[str] = ["mp3", "wav", "flac", "aac"]
    ALLOWED_VIDEO_EXTENSIONS: List[str] = ["mp4", "avi", "mov"]
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
