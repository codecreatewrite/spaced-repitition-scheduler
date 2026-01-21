from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.schedule import Schedule
from app.models.feedback import Feedback  # ADD THIS

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

if __name__ == "__main__":
    init_db()
