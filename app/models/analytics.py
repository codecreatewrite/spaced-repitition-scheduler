from sqlalchemy import Column, String, DateTime, Integer, Boolean
from datetime import datetime
from app.db.base import Base

class UserAnalytics(Base):
    """Track user engagement and learning metrics"""
    __tablename__ = "user_analytics"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Session tracking
    total_sessions = Column(Integer, default=0)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Schedule metrics
    total_schedules_created = Column(Integer, default=0)
    total_events_created = Column(Integer, default=0)
    
    # Engagement
    current_streak = Column(Integer, default=0)  # Days using app consecutively
    longest_streak = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
