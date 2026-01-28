from pydantic_settings import BaseSettings
from typing import List
from app.db.persistent import get_database_url
from dotenv import load_dotenv  # ADD THIS
import os  # ADD THIS

# ADD THIS LINE - Force load .env file
load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Spaced Repetition Scheduler"
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    
    # Database - UPDATE THIS LINE
    DATABASE_URL: str = get_database_url()
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    # Calendar
    DEFAULT_INTERVALS: str = "1,3,7,21"
    TIMEZONE: str = "Africa/Lagos"
    
    # Email - ADD THESE WITH DEFAULTS
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_RECIPIENT: str = os.getenv("EMAIL_RECIPIENT", "")
    
    @property
    def intervals_list(self) -> List[int]:
        return [int(x.strip()) for x in self.DEFAULT_INTERVALS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # ADD THIS

settings = Settings()
