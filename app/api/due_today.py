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
    
    # Get current date/time
    today = date.today()
    now = datetime.now()
    
    # ✅ FIXED: Get schedules due TODAY OR EARLIER (includes overdue)
    due_schedules = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        Schedule.start_date <= datetime.combine(today, datetime.max.time())  # ✅ Changed to <=
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
        
        # Calculate how overdue (if at all)
        days_overdue = (now.date() - schedule.start_date.date()).days
        
        reviews_due.append({
            "schedule_id": schedule.id,
            "topic": schedule.topic,
            "topic_id": schedule.topic_id,
            "topic_exists": topic is not None,
            "can_explain": topic is not None,
            "confidence": topic.avg_confidence if topic else 0,
            "last_explained": topic.last_explained.isoformat() if topic and topic.last_explained else None,
            "due_date": schedule.start_date.date().isoformat(),
            "days_overdue": days_overdue if days_overdue > 0 else 0,
            "status": "overdue" if days_overdue > 0 else "due_today"
        })
    
    # ✅ FIXED: Topics that need review (exclude if they have FUTURE schedule)
    topics_needing_review = []
    scheduled_topic_ids = {s.topic_id for s in due_schedules if s.topic_id}
    
    for topic in all_topics:
        # Skip if already in due_schedules
        if topic.id in scheduled_topic_ids:
            continue
        
        # Check if has future schedule (not due yet)
        future_schedule = db.query(Schedule).filter(
            Schedule.topic_id == topic.id,
            Schedule.user_id == current_user.id,
            Schedule.start_date > now  # ✅ Only exclude if scheduled in FUTURE
        ).first()
        
        # If has future schedule, skip
        if future_schedule:
            continue
        
        # If never explained, suggest it
        if not topic.last_explained:
            continue  # Don't suggest brand new topics
        
        # Calculate days since last explained
        days_since = (now - topic.last_explained).days
        
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
