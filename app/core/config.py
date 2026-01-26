from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from app.db.persistent import get_database_url

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

    # Email / Feedback (ADD THESE)
    FEEDBACK_EMAIL_TO: str = Field(..., env="FEEDBACK_EMAIL_TO")
    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    
    # Calendar
    DEFAULT_INTERVALS: str = "1,3,7,21"
    TIMEZONE: str = "Africa/Lagos"
    
    @property
    def intervals_list(self) -> List[int]:
        return [int(x.strip()) for x in self.DEFAULT_INTERVALS.split(",")]
    
    class Config:
        env_file = ".env"
        extra = "forbid"

settings = Settings()
