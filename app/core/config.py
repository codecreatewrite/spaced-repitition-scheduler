from pydantic_settings import BaseSettings
from typing import List
from app.db.persistent import get_database_url

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Spaced Repetition Scheduler"
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    
    # Database - UPDATE THIS LINE
    DATABASE_URL: str = get_database_url()

    #Email Configuration
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    EMAIL_RECIPIENT: str
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
 
    # Calendar
    DEFAULT_INTERVALS: str = "1,3,7,21"
    TIMEZONE: str = "Africa/Lagos"
    
    @property
    def intervals_list(self) -> List[int]:
        return [int(x.strip()) for x in self.DEFAULT_INTERVALS.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()
