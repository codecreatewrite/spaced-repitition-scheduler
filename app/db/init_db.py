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
    """Create missing tables (doesn't drop existing ones)"""
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"📊 Existing tables before init: {existing_tables}")
    
    # This only creates tables that don't exist
    Base.metadata.create_all(bind=engine)
    
    # Check again after creation
    existing_tables = inspector.get_table_names()
    print(f"✅ Tables after init: {existing_tables}")
    
    if len(existing_tables) == 0:
        print("⚠️ WARNING: No tables exist! Database might not be connected properly.")
    else:
        print(f"✅ Database has {len(existing_tables)} tables")

if __name__ == "__main__":
    init_db()
