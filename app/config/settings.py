import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class Settings(BaseSettings):
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Project settings
    PROJECT_NAME: str = "FastAPI MVC Application"
    PROJECT_DESCRIPTION: str = "FastAPI application following MVC architecture with service layer"
    PROJECT_VERSION: str = "0.1.0"
    
    # Server settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_mvc"
    DB_ECHO: bool = False
    AUTO_CREATE_TABLES: bool = False  # Set to True to auto-create tables without migrations (development only)
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: Optional[str] = "logs/app.log"
    
    # Redis and Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # JWT Auth
    JWT_SECRET_KEY: str = "YOUR_SECRET_KEY"  # should be overridden in .env
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Initialize settings
settings = Settings()
