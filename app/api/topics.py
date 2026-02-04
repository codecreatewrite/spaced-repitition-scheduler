from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.session import get_db
from app.db.topic_crud import TopicCRUD, ExplainSessionCRUD
from app.core.dependencies import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/api/topics", tags=["topics"])

# Request/Response models
class CreateTopicRequest(BaseModel):
    title: str
    subject: Optional[str] = None
    description: Optional[str] = None

class TopicResponse(BaseModel):
    id: str
    title: str
    subject: Optional[str]
    description: Optional[str]
    total_explains: int
    avg_confidence: int
    last_explained: Optional[str]
    created_at: str

class CreateExplainSessionRequest(BaseModel):
    topic_id: str
    duration_seconds: int
    struggles: Optional[str] = None
    forgot: Optional[str] = None
    unclear: Optional[str] = None
    confidence: Optional[int] = None

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
    
    return {
        "id": topic.id,
        "title": topic.title,
        "subject": topic.subject,
        "description": topic.description,
        "total_explains": topic.total_explains,
        "avg_confidence": topic.avg_confidence,
        "last_explained": topic.last_explained.isoformat() if topic.last_explained else None,
        "created_at": topic.created_at.isoformat(),
        "recent_sessions": [
            {
                "id": s.id,
                "duration_seconds": s.duration_seconds,
                "confidence": s.confidence,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions[:5]  # Last 5 sessions
        ]
    }

@router.post("/explain")
async def save_explain_session(
    request: CreateExplainSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save an explain mode session"""
    
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

    # ADD THIS: Update analytics
    from app.services.analytics_service import AnalyticsService
    AnalyticsService.update_explain_completed(db, current_user.id)
    
    return {
        "success": True,
        "session_id": session.id,
        "message": "Session saved successfully"
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
