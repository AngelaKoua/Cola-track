"""
Configuration module for the CTrack FastAPI application.

This module uses Pydantic Settings to manage application configuration
from environment variables. It provides centralized configuration for:
- Database connection
- CORS settings
- JWT authentication
- API settings
- Rate limiting
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden by creating a .env file in the Backend directory.
    See env.example for a template.
    """
    
    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ctrack_db"
    """
    PostgreSQL database connection string.
    Format: postgresql://username:password@host:port/database_name
    
    Example: postgresql://postgres:mypassword@localhost:5432/ctrack_db
    """
    
    # ============================================================================
    # API CONFIGURATION
    # ============================================================================
    API_V1_PREFIX: str = "/api"
    """API route prefix for all endpoints"""
    
    PROJECT_NAME: str = "CTrack API"
    """Project name displayed in API documentation"""
    
    DEBUG: bool = True
    """Enable debug mode (set to False in production)"""
    
    # ============================================================================
    # CORS CONFIGURATION
    # ============================================================================
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    """
    Comma-separated list of allowed CORS origins.
    This allows your Next.js frontend to communicate with the backend.
    
    Example: http://localhost:3000,https://yourdomain.com
    """
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # ============================================================================
    # JWT AUTHENTICATION CONFIGURATION
    # ============================================================================
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    """
    Secret key for JWT token encoding/decoding.
    
    IMPORTANT: Change this in production!
    Generate a secure key using: openssl rand -hex 32
    """
    
    ALGORITHM: str = "HS256"
    """JWT encoding algorithm"""
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    """JWT token expiration time in minutes"""
    
    # ============================================================================
    # EMAIL / SMTP CONFIGURATION
    # ============================================================================
    SMTP_HOST: str = "smtp.gmail.com"
    """SMTP server hostname"""
    
    SMTP_PORT: int = 587
    """SMTP server port (587 for TLS, 465 for SSL)"""
    
    SMTP_USER: str = ""
    """SMTP authentication username (email address)"""
    
    SMTP_PASSWORD: str = ""
    """SMTP authentication password (App Password for Gmail)"""
    
    SMTP_FROM_EMAIL: str = ""
    """Sender email address"""
    
    SMTP_FROM_NAME: str = "Colatrack Platform"
    """Sender display name"""
    
    PLATFORM_URL: str = "http://localhost:3000"
    """Platform URL included in welcome emails"""
    
    # ============================================================================
    # RATE LIMITING CONFIGURATION
    # ============================================================================
    RATE_LIMIT_PER_MINUTE: int = 60
    """Maximum number of requests per minute per IP address"""

    # ============================================================================
    # BACKGROUND JOBS CONFIGURATION
    # ============================================================================
    DEADLINE_CHECK_INTERVAL_SECONDS: int = 1800
    """Interval between overdue-incident checks (default: 30 minutes)"""

    INFERENCE_INTERVAL_SECONDS: int = 1800
    """
    Interval between global ML inference runs (default: 30 minutes).
    Keep it above 5 minutes so a serverless database (e.g. Neon) can scale to zero
    between runs and stay within its free compute quota.
    """

    # ============================================================================
    # AI / LLM CONFIGURATION
    # ============================================================================
    GEMINI_API_KEY: str = ""
    """Google Gemini API Key for ColaAssist chat"""
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = True


# ============================================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================================
settings = Settings()
"""
Global settings instance used throughout the application.

Usage:
    from app.config import settings
    
    database_url = settings.DATABASE_URL
"""
