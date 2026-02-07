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
    subject = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Tracking
    total_explains = Column(Integer, default=0)
    avg_confidence = Column(Integer, default=0)  # 1-5 scale
    last_explained = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    explain_sessions = relationship("ExplainSession", back_populates="topic", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="topic_relation", cascade="all, delete-orphan")  # ✅ FIXED


class ExplainSession(Base):
    """Record of explain mode sessions"""
    __tablename__ = "explain_sessions"
    
    id = Column(String, primary_key=True)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Session data
    duration_seconds = Column(Integer)
    
    # The three critical questions
    struggles = Column(Text, nullable=True)
    forgot = Column(Text, nullable=True)
    unclear = Column(Text, nullable=True)
    
    confidence = Column(Integer, nullable=True)  # 1-5
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="explain_sessions")
