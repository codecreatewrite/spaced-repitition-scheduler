from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db.crud import ScheduleCRUD
from app.db.topic_crud import TopicCRUD
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/due-today", tags=["due-today"])

@router.get("")
async def get_due_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schedules and topics due for review today"""
    
    # Get all user's schedules
    schedules = ScheduleCRUD.get_by_user(db, current_user.id)
    
    # Get all user's topics
    topics = TopicCRUD.get_user_topics(db, current_user.id)
    
    # Find schedules due today
    today = datetime.now().date()
    due_schedules = []
    
    for schedule in schedules:
        # Check if any review is due today based on intervals
        schedule_date = schedule.start_date.date() if isinstance(schedule.start_date, datetime) else schedule.start_date
        
        for interval in schedule.intervals:
            review_date = schedule_date + timedelta(days=interval)
            if review_date == today:
                # Find matching topic if exists
                matching_topic = None
                if schedule.topic_id:
                    matching_topic = TopicCRUD.get_by_id(db, schedule.topic_id)
                
                # If no linked topic, try to find by name
                if not matching_topic:
                    for topic in topics:
                        if topic.title.lower() in schedule.topic.lower() or schedule.topic.lower() in topic.title.lower():
                            matching_topic = topic
                            break
                
                due_schedules.append({
                    "schedule_id": schedule.id,
                    "schedule_topic": schedule.topic,
                    "interval": interval,
                    "topic_id": matching_topic.id if matching_topic else None,
                    "topic_exists": matching_topic is not None,
                    "can_explain": matching_topic is not None
                })
    
    # Topics that haven't been explained in a while
    topics_needing_review = []
    for topic in topics:
        if topic.last_explained:
            days_since = (datetime.now() - topic.last_explained).days
            # If confidence was low and it's been a few days
            if topic.avg_confidence < 4 and days_since >= 3:
                topics_needing_review.append({
                    "topic_id": topic.id,
                    "title": topic.title,
                    "days_since": days_since,
                    "confidence": topic.avg_confidence
                })
    
    return {
        "due_schedules": due_schedules,
        "topics_needing_review": topics_needing_review,
        "total_due": len(due_schedules) + len(topics_needing_review)
    }
