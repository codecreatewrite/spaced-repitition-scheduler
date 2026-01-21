from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from app.db.base import Base

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    type = Column(String)  # feature, bug, improvement, automation, other
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True)  # If user is logged in
