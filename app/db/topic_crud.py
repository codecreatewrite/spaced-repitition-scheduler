from sqlalchemy.orm import Session
from app.models.topic import Topic, ExplainSession
from typing import Optional, List
import uuid
from datetime import datetime

class TopicCRUD:
    """Database operations for Topics"""
    
    @staticmethod
    def create(db: Session, user_id: str, title: str, subject: str = None, description: str = None) -> Topic:
        """Create a new topic"""
        topic = Topic(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            subject=subject,
            description=description,
            created_at=datetime.utcnow()
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
        return topic
    
    @staticmethod
    def get_by_id(db: Session, topic_id: str) -> Optional[Topic]:
        """Get topic by ID"""
        return db.query(Topic).filter(Topic.id == topic_id).first()
    
    @staticmethod
    def get_user_topics(db: Session, user_id: str) -> List[Topic]:
        """Get all topics for a user"""
        return db.query(Topic).filter(Topic.user_id == user_id).order_by(Topic.created_at.desc()).all()
    
    @staticmethod
    def update_after_explain(db: Session, topic_id: str):
        """Update topic stats after an explain session"""
        topic = TopicCRUD.get_by_id(db, topic_id)
        if topic:
            topic.total_explains += 1
            topic.last_explained = datetime.utcnow()
            
            # Calculate average confidence from all sessions
            sessions = db.query(ExplainSession).filter(ExplainSession.topic_id == topic_id).all()
            confidences = [s.confidence for s in sessions if s.confidence]
            if confidences:
                topic.avg_confidence = int(sum(confidences) / len(confidences))
            
            db.commit()
    
    @staticmethod
    def delete(db: Session, topic_id: str) -> bool:
        """Delete a topic"""
        topic = TopicCRUD.get_by_id(db, topic_id)
        if topic:
            db.delete(topic)
            db.commit()
            return True
        return False


class ExplainSessionCRUD:
    """Database operations for Explain Sessions"""
    
    @staticmethod
    def create(db: Session, session_data: dict) -> ExplainSession:
        """Create a new explain session"""
        session = ExplainSession(
            id=str(uuid.uuid4()),
            topic_id=session_data['topic_id'],
            user_id=session_data['user_id'],
            duration_seconds=session_data.get('duration_seconds'),
            struggles=session_data.get('struggles'),
            forgot=session_data.get('forgot'),
            unclear=session_data.get('unclear'),
            confidence=session_data.get('confidence'),
            created_at=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Update topic stats
        TopicCRUD.update_after_explain(db, session_data['topic_id'])
        
        return session
    
    @staticmethod
    def get_topic_sessions(db: Session, topic_id: str) -> List[ExplainSession]:
        """Get all sessions for a topic"""
        return db.query(ExplainSession).filter(
            ExplainSession.topic_id == topic_id
        ).order_by(ExplainSession.created_at.desc()).all()
