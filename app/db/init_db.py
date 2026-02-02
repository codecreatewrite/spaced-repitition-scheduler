from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.schedule import Schedule
from app.models.feedback import Feedback
from app.models.analytics import UserAnalytics
from app.models.topic import Topic, ExplainSession  # ADD THIS
from sqlalchemy import inspect

def init_db():
    """Create missing tables"""
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"📊 Existing tables before init: {existing_tables}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Check again
    existing_tables = inspector.get_table_names()
    print(f"✅ Tables after init: {existing_tables}")
    
    if len(existing_tables) == 0:
        print("⚠️ WARNING: No tables exist!")
    else:
        print(f"✅ Database has {len(existing_tables)} tables")

if __name__ == "__main__":
    init_db()
