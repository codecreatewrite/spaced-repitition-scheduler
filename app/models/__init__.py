# app/models/__init__.py

from app.db.base import Base

# Import ALL models so SQLAlchemy registers them
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.schedule import Schedule

__all__ = [
    "Base",
    "User",
    "OAuthToken",
    "Schedule",
]
