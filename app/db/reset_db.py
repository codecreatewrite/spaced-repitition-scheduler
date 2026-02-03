from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.schedule import Schedule
from app.models.feedback import Feedback
from app.models.analytics import UserAnalytics
from app.models.topic import Topic, ExplainSession
from sqlalchemy import inspect, text

def reset_db():
    """Drop all tables and recreate them"""
    
    print("🗑️  Dropping all existing tables...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    print("✅ All tables dropped")
    
    # Recreate all tables
    print("🔨 Creating new tables with updated schema...")
    Base.metadata.create_all(bind=engine)
    
    # Verify
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Created {len(tables)} tables: {tables}")

if __name__ == "__main__":
    reset_db()
