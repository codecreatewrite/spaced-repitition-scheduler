from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.analytics import UserAnalytics
from app.models.schedule import Schedule
from datetime import datetime, timedelta
import uuid

class AnalyticsService:
    """Calculate user analytics and insights"""
    
    @staticmethod
    def get_or_create_analytics(db: Session, user_id: str) -> UserAnalytics:
        """Get user analytics or create if doesn't exist"""
        analytics = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == user_id
        ).first()
        
        if not analytics:
            analytics = UserAnalytics(
                id=str(uuid.uuid4()),
                user_id=user_id
            )
            db.add(analytics)
            db.commit()
            db.refresh(analytics)
        
        return analytics
    
    @staticmethod
    def update_session(db: Session, user_id: str):
        """Update user session tracking"""
        analytics = AnalyticsService.get_or_create_analytics(db, user_id)
        
        # Update session count
        analytics.total_sessions += 1
        
        # Calculate streak
        last_active = analytics.last_active
        now = datetime.utcnow()
        
        if last_active:
            days_diff = (now.date() - last_active.date()).days
            
            if days_diff == 0:
                # Same day, no change to streak
                pass
            elif days_diff == 1:
                # Consecutive day, increment streak
                analytics.current_streak += 1
                if analytics.current_streak > analytics.longest_streak:
                    analytics.longest_streak = analytics.current_streak
            else:
                # Streak broken, reset
                analytics.current_streak = 1
        else:
            # First session
            analytics.current_streak = 1
            analytics.longest_streak = 1
        
        analytics.last_active = now
        db.commit()
    
    @staticmethod
    def update_schedule_created(db: Session, user_id: str, events_count: int):
        """Update analytics when user creates a schedule"""
        analytics = AnalyticsService.get_or_create_analytics(db, user_id)
        
        analytics.total_schedules_created += 1
        analytics.total_events_created += events_count
        
        db.commit()
    
    @staticmethod
    def get_user_stats(db: Session, user_id: str) -> dict:
        """Get comprehensive user statistics"""
        analytics = AnalyticsService.get_or_create_analytics(db, user_id)
        
        # Get schedule breakdown
        schedules = db.query(Schedule).filter(Schedule.user_id == user_id).all()
        
        # Calculate stats
        total_schedules = len(schedules)
        
        # Group by intervals for insights
        interval_usage = {}
        for schedule in schedules:
            key = str(schedule.intervals)
            interval_usage[key] = interval_usage.get(key, 0) + 1
        
        # Most recent schedules
        recent_schedules = sorted(schedules, key=lambda x: x.created_at, reverse=True)[:5]
        
        return {
            'total_schedules': analytics.total_schedules_created,
            'total_events': analytics.total_events_created,
            'current_streak': analytics.current_streak,
            'longest_streak': analytics.longest_streak,
            'total_sessions': analytics.total_sessions,
            'member_since': analytics.created_at.strftime('%B %d, %Y'),
            'last_active': analytics.last_active.strftime('%B %d, %Y at %I:%M %p'),
            'interval_usage': interval_usage,
            'recent_topics': [
                {
                    'topic': s.topic,
                    'created': s.created_at.strftime('%b %d'),
                    'events': len(s.calendar_event_ids) if s.calendar_event_ids else 0
                }
                for s in recent_schedules
            ]
        }
