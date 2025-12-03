from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database settings
    #DATABASE_URL: str = "sqlite://user:pass@localhost/spendwise"
    DATABASE_URL: str = "sqlite:///./spendwise.db"  # Changed to SQLite
    # JWT settings
    SECRET_KEY: str = "6a0d5817fe4878488a609d563c9df56a8b15308c2fe9347a55b27d09c8ba60a9"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML model settings
    MODEL_PATH: str = "ml/models/budget_predictor.pkl"
    
    # Scheduler settings
    SCHEDULER_INTERVAL_HOURS: int = 1
    
    class Config:
        env_file = ".env"

settings = Settings()