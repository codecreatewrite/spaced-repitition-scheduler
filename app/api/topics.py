from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.db.topic_crud import TopicCRUD, ExplainSessionCRUD
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.schedule import Schedule
from datetime import datetime, timedelta, date
import uuid

router = APIRouter(prefix="/api/topics", tags=["topics"])

# Request/Response models
class CreateTopicRequest(BaseModel):
    title: str
    subject: Optional[str] = None
    description: Optional[str] = None

class CreateExplainSessionRequest(BaseModel):
    topic_id: str
    duration_seconds: int
    struggles: Optional[str] = None
    forgot: Optional[str] = None
    unclear: Optional[str] = None
    confidence: Optional[int] = None

# Helper: Calculate next review date based on confidence
def calculate_next_review_date(confidence: int) -> date:
    """
    Confidence → Days until review:
    1 (Lost)      → 1 day
    2 (Struggling) → 2 days
    3 (Okay)       → 3 days
    4 (Good)       → 7 days
    5 (Mastered)   → 14 days
    """
    confidence_to_days = {
        1: 1,
        2: 2,
        3: 3,
        4: 7,
        5: 14
    }
    days = confidence_to_days.get(confidence, 3)
    return date.today() + timedelta(days=days)

# Helper: Create or update schedule (ONE schedule per topic)
def create_or_update_schedule(
    db: Session,
    user_id: str,
    topic_id: str,
    topic_title: str,
    next_review_date: date
) -> Schedule:
    """
    CRITICAL RULE: One topic = one active schedule.
    Most recent explain always wins.
    """
    # Check if schedule already exists for this topic
    existing = db.query(Schedule).filter(
        Schedule.topic_id == topic_id,
        Schedule.user_id == user_id
    ).first()

    if existing:
        # UPDATE existing schedule (most recent explain wins)
        existing.start_date = datetime.combine(next_review_date, datetime.min.time())
        db.commit()
        db.refresh(existing)
        print(f"✅ Updated schedule for topic {topic_id}: next review {next_review_date}")
        return existing
    else:
        # CREATE new schedule
        schedule = Schedule(
            id=str(uuid.uuid4()),
            user_id=user_id,
            topic_id=topic_id,
            topic=topic_title,
            start_date=datetime.combine(next_review_date, datetime.min.time()),
            intervals=[1, 3, 7, 14],  # Default intervals
            completed=0,
            created_at=datetime.utcnow()
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        print(f"✅ Created schedule for topic {topic_id}: next review {next_review_date}")
        return schedule

@router.post("/create")
async def create_topic(
    request: CreateTopicRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new topic"""
    if not request.title.strip():
        raise HTTPException(status_code=400, detail="Topic title cannot be empty")

    topic = TopicCRUD.create(
        db=db,
        user_id=current_user.id,
        title=request.title,
        subject=request.subject,
        description=request.description
    )

    return {
        "success": True,
        "topic": {
            "id": topic.id,
            "title": topic.title,
            "subject": topic.subject,
            "description": topic.description
        }
    }

@router.get("/list")
async def list_topics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all topics for current user"""
    topics = TopicCRUD.get_user_topics(db, current_user.id)

    return {
        "total": len(topics),
        "topics": [
            {
                "id": t.id,
                "title": t.title,
                "subject": t.subject,
                "description": t.description,
                "total_explains": t.total_explains,
                "avg_confidence": t.avg_confidence,
                "last_explained": t.last_explained.isoformat() if t.last_explained else None,
                "created_at": t.created_at.isoformat()
            }
            for t in topics
        ]
    }

@router.get("/{topic_id}")
async def get_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific topic"""
    topic = TopicCRUD.get_by_id(db, topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this topic")

    # Get recent sessions
    sessions = ExplainSessionCRUD.get_topic_sessions(db, topic_id)

    # Get next review date (if scheduled)
    schedule = db.query(Schedule).filter(
        Schedule.topic_id == topic_id,
        Schedule.user_id == current_user.id
    ).first()

    next_review = None
    if schedule:
        next_review = schedule.start_date.date().isoformat()

    return {
        "id": topic.id,
        "title": topic.title,
        "subject": topic.subject,
        "description": topic.description,
        "total_explains": topic.total_explains,
        "avg_confidence": topic.avg_confidence,
        "last_explained": topic.last_explained.isoformat() if topic.last_explained else None,
        "next_review": next_review,
        "created_at": topic.created_at.isoformat(),
        "recent_sessions": [
            {
                "id": s.id,
                "duration_seconds": s.duration_seconds,
                "confidence": s.confidence,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions[:5]
        ]
    }

@router.post("/explain")
async def save_explain_session(
    request: CreateExplainSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save explain session and AUTO-SCHEDULE next review"""

    print(f"\n🎯 Explain endpoint called for topic {request.topic_id}")
    print(f"   Confidence: {request.confidence}")

    # Verify topic belongs to user
    topic = TopicCRUD.get_by_id(db, request.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create session
    session_data = {
        "topic_id": request.topic_id,
        "user_id": current_user.id,
        "duration_seconds": request.duration_seconds,
        "struggles": request.struggles,
        "forgot": request.forgot,
        "unclear": request.unclear,
        "confidence": request.confidence
    }

    session = ExplainSessionCRUD.create(db, session_data)
    print(f"✅ Explain session saved: {session.id}")

    # Update analytics (optional)
    try:
        from app.services.analytics_service import AnalyticsService
        AnalyticsService.update_explain_completed(db, current_user.id)
    except Exception as e:
        print(f"⚠️  Analytics update failed: {e}")

    # AUTO-SCHEDULE next review based on confidence
    next_review_date = None
    days_until_review = None

    if request.confidence:
        print(f"📅 Auto-scheduling review...")
        next_review_date = calculate_next_review_date(request.confidence)
        days_until_review = (next_review_date - date.today()).days

        # Create or update schedule (ONE schedule per topic)
        schedule = create_or_update_schedule(
            db=db,
            user_id=current_user.id,
            topic_id=request.topic_id,
            topic_title=topic.title,
            next_review_date=next_review_date
        )

        # ✅ FORCE COMMIT (ensure DB writes immediately)
        db.commit()
        db.flush()

        print(f"✅ Schedule saved: {schedule.id}")
        print(f"   Next review: {next_review_date} ({days_until_review} days)")
    else:
        print(f"⚠️  No confidence provided, skipping auto-scheduling")

    return {
        "success": True,
        "session_id": session.id,
        "message": "Session saved and review scheduled" if next_review_date else "Session saved",
        "next_review_date": next_review_date.isoformat() if next_review_date else None,
        "days_until_review": days_until_review,
        "confidence": request.confidence
    }

@router.get("/{topic_id}/sessions")
async def get_topic_sessions(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all explain sessions for a topic with reflections"""
    
    # Verify topic ownership
    topic = TopicCRUD.get_by_id(db, topic_id)
    if not topic or topic.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get all sessions
    sessions = ExplainSessionCRUD.get_topic_sessions(db, topic_id)
    
    return {
        "topic_id": topic_id,
        "topic_title": topic.title,
        "total_sessions": len(sessions),
        "sessions": [
            {
                "id": s.id,
                "date": s.created_at.isoformat(),
                "duration_seconds": s.duration_seconds,
                "confidence": s.confidence,
                "struggles": s.struggles,
                "forgot": s.forgot,
                "unclear": s.unclear,
                "days_ago": (datetime.utcnow() - s.created_at).days
            }
            for s in sessions
        ]
    }

@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a topic"""
    topic = TopicCRUD.get_by_id(db, topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    TopicCRUD.delete(db, topic_id)

    return {"success": True, "message": "Topic deleted"}
