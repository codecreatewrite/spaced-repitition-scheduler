from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=True)
    
    # Schedule details
    topic = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)  # This is the NEXT REVIEW DATE
    intervals = Column(JSON, nullable=False)
    
    # Google Calendar integration
    calendar_event_ids = Column(JSON)
    calendar_id = Column(String, default="primary")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="schedules")
    topic_relation = relationship("Topic", back_populates="schedules")
