from pydantic_settings import BaseSettings
from typing import List
from app.db.persistent import get_database_url
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # App - UPDATED
    APP_NAME: str = "StudyCore"
    APP_TAGLINE: str = "Study smarter, not harder. Built for Nigerian students."
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str = get_database_url()
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    # Calendar
    DEFAULT_INTERVALS: str = "1,3,7,21"
    TIMEZONE: str = "Africa/Lagos"
    
    # Email
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_RECIPIENT: str = os.getenv("EMAIL_RECIPIENT", "")
    
    @property
    def intervals_list(self) -> List[int]:
        return [int(x.strip()) for x in self.DEFAULT_INTERVALS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
