from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.db.session import get_db
from app.models.schedule import Schedule
from app.db.topic_crud import TopicCRUD
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/due-today")
async def get_due_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schedules and topics due for review today"""
    
    today = date.today()
    
    # Get schedules due today (new auto-scheduled ones)
    due_schedules = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        Schedule.start_date >= datetime.combine(today, datetime.min.time()),
        Schedule.start_date < datetime.combine(today, datetime.max.time())
    ).all()
    
    # Get all user's topics for context
    all_topics = TopicCRUD.get_user_topics(db, current_user.id)
    
    # Build response
    reviews_due = []
    
    for schedule in due_schedules:
        # Find matching topic
        topic = None
        if schedule.topic_id:
            topic = TopicCRUD.get_by_id(db, schedule.topic_id)
        
        reviews_due.append({
            "schedule_id": schedule.id,
            "topic": schedule.topic,
            "topic_id": schedule.topic_id,
            "topic_exists": topic is not None,
            "can_explain": topic is not None,
            "confidence": topic.avg_confidence if topic else 0,
            "last_explained": topic.last_explained.isoformat() if topic and topic.last_explained else None
        })
    
    # Topics that haven't been explained in a while (no schedule yet)
    topics_needing_review = []
    for topic in all_topics:
        # Skip if already has a schedule
        existing_schedule = db.query(Schedule).filter(
            Schedule.topic_id == topic.id,
            Schedule.user_id == current_user.id
        ).first()
        
        if not existing_schedule and topic.last_explained:
            days_since = (datetime.now() - topic.last_explained).days
            
            # Suggest review if:
            # - Low confidence (< 4) and it's been 3+ days
            # - Any topic that hasn't been reviewed in 7+ days
            if (topic.avg_confidence < 4 and days_since >= 3) or days_since >= 7:
                topics_needing_review.append({
                    "topic_id": topic.id,
                    "title": topic.title,
                    "days_since": days_since,
                    "confidence": topic.avg_confidence,
                    "reason": "Low confidence - review recommended" if topic.avg_confidence < 4 else "Long time since last review"
                })
    
    return {
        "due_schedules": reviews_due,
        "topics_needing_review": topics_needing_review,
        "total_due": len(reviews_due) + len(topics_needing_review)
    }
