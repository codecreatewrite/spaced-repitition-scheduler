"""Force database migration to add missing tables"""
from app.db.session import engine
from app.db.base import Base

# Import ALL models
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.schedule import Schedule
from app.models.feedback import Feedback
from app.models.analytics import UserAnalytics

def migrate():
    print("🔄 Checking database tables...")
    
    # This will create any missing tables without dropping existing ones
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database migration complete!")
    print("📊 Tables that should exist:")
    for table in Base.metadata.sorted_tables:
        print(f"   - {table.name}")

if __name__ == "__main__":
    migrate()
