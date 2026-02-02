from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Topic(Base):
    """Topics students are studying"""
    __tablename__ = "topics"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Topic info
    title = Column(String, nullable=False)
    subject = Column(String)  # e.g., "Organic Chemistry", "Anatomy"
    difficulty = Column(Integer, default=3)  # 1-5 scale
    
    # Tracking
    total_explains = Column(Integer, default=0)
    last_explained = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    explain_sessions = relationship("ExplainSession", back_populates="topic", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="topic")  # Must match Schedule's back_populates


class ExplainSession(Base):
    """Record of explain mode sessions"""
    __tablename__ = "explain_sessions"
    
    id = Column(String, primary_key=True)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Session data
    duration_seconds = Column(Integer)  # How long they explained
    struggles = Column(Text)  # What they struggled with
    forgot = Column(Text)  # What they forgot
    unclear = Column(Text)  # What felt unclear
    
    confidence = Column(Integer)  # 1-5: How confident they felt
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="explain_sessions")
