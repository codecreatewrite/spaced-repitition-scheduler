from sqlalchemy.orm import Session
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.schedule import Schedule
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class UserCRUD:
    """Database operations for Users"""
    
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create(db: Session, user_data: Dict[str, Any]) -> User:
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data.get('name', ''),
            picture=user_data.get('picture', ''),
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_last_login(db: Session, user_id: str):
        user = UserCRUD.get_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()

class TokenCRUD:
    """Database operations for OAuth Tokens"""
    
    @staticmethod
    def get_by_user(db: Session, user_id: str) -> Optional[OAuthToken]:
        return db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
    
    @staticmethod
    def create_or_update(db: Session, user_id: str, token_data: Dict[str, Any]) -> OAuthToken:
        token = TokenCRUD.get_by_user(db, user_id)
        
        if token:
            # Update existing token
            token.token_data = token_data
            token.updated_at = datetime.utcnow()
        else:
            # Create new token
            token = OAuthToken(
                id=str(uuid.uuid4()),
                user_id=user_id,
                token_data=token_data,
                created_at=datetime.utcnow()
            )
            db.add(token)
        
        db.commit()
        db.refresh(token)
        return token

class ScheduleCRUD:
    """Database operations for Schedules"""
    
    @staticmethod
    def get_by_user(db: Session, user_id: str):
        return db.query(Schedule).filter(Schedule.user_id == user_id).all()
    
    @staticmethod
    def create(db: Session, schedule_data: Dict[str, Any]) -> Schedule:
        schedule = Schedule(
            id=str(uuid.uuid4()),
            user_id=schedule_data['user_id'],
            topic=schedule_data['topic'],
            topic_id=schedule_data.get('topic_id'),
            start_date=schedule_data['start_date'],
            intervals=schedule_data['intervals'],
            calendar_id=schedule_data.get('calendar_id', 'primary'),
            calendar_event_ids=schedule_data.get('calendar_event_ids', []),
            created_at=datetime.utcnow()
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule
