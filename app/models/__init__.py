# app/models/__init__.py

from app.db.base import Base

# Import ALL models so SQLAlchemy registers them
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.feedback import Feedback
from app.models.analytics import UserAnalytics
from app.models.topic import Topic, ExplainSession
from app.models.schedule import Schedule

__all__ = [
    "Base",
    "User",
    "OAuthToken", 
    "Schedule",
    "Feedback",
    "UserAnalytics",
    "Topic",
    "ExplainSession"
]
