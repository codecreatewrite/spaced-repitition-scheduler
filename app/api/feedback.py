from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.feedback import Feedback
from app.core.dependencies import get_current_user_optional
from app.services.email_service import EmailService
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    name: str
    email: str
    type: str
    message: str

@router.post("")
async def submit_feedback(
    feedback_data: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Submit user feedback and notify admin via email"""
    
    # Validate feedback type
    valid_types = ["feature", "bug", "improvement", "automation", "other"]
    if feedback_data.type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid feedback type")
    
    # Validate message length
    if len(feedback_data.message.strip()) < 10:
        raise HTTPException(status_code=400, detail="Message too short. Please provide more details.")
    
    # Create feedback record
    feedback = Feedback(
        id=str(uuid.uuid4()),
        name=feedback_data.name,
        email=feedback_data.email,
        type=feedback_data.type,
        message=feedback_data.message,
        user_id=current_user.id if current_user else None,
        created_at=datetime.utcnow()
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    # Send email notification to admin
    try:
        notification_data = {
            "type": feedback_data.type,
            "name": feedback_data.name,
            "email": feedback_data.email,
            "message": feedback_data.message,
            "created_at": feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Send email (async, won't block response)
        await EmailService.send_feedback_notification(notification_data)
        
    except Exception as e:
        print(f"⚠️ Email notification failed: {str(e)}")
        # Don't fail the request if email fails
    
    return {
        "success": True, 
        "message": "Thank you! Your feedback has been received.",
        "feedback_id": feedback.id
    }

@router.get("/admin/list")
async def list_feedback(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get all feedback (admin only - add proper auth later)"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    feedback_list = db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).limit(100).all()
    
    return {
        "total": len(feedback_list),
        "feedback": [
            {
                "id": f.id,
                "type": f.type,
                "name": f.name,
                "email": f.email,
                "message": f.message,
                "created_at": f.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "user_id": f.user_id
            }
            for f in feedback_list
        ]
    }
