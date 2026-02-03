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
    subject = Column(String, nullable=True)  # e.g., "Anatomy", "Chemistry"
    description = Column(Text, nullable=True)  # Optional notes
    
    # Tracking
    total_explains = Column(Integer, default=0)
    avg_confidence = Column(Integer, default=0)  # 1-5 scale
    last_explained = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    explain_sessions = relationship("ExplainSession", back_populates="topic", cascade="all, delete-orphan")
    schedules = relationship("Schedule",back_populates="topic_relation", cascade="all, delete-orphan"
    )


class ExplainSession(Base):
    """Record of explain mode sessions"""
    __tablename__ = "explain_sessions"
    
    id = Column(String, primary_key=True)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Session data
    duration_seconds = Column(Integer)  # How long they explained
    
    # The three critical questions
    struggles = Column(Text, nullable=True)  # What they struggled with
    forgot = Column(Text, nullable=True)     # What they forgot
    unclear = Column(Text, nullable=True)    # What felt unclear
    
    confidence = Column(Integer, nullable=True)  # 1-5: How confident they felt
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="explain_sessions")
