from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.feedback import Feedback
from app.core.dependencies import get_current_user_optional
import uuid

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
    """Submit user feedback"""
    
    feedback = Feedback(
        id=str(uuid.uuid4()),
        name=feedback_data.name,
        email=feedback_data.email,
        type=feedback_data.type,
        message=feedback_data.message,
        user_id=current_user.id if current_user else None
    )
    
    db.add(feedback)
    db.commit()
    
    # TODO: Send email notification to you
    # For now, you can check the database
    
    return {"success": True, "message": "Feedback received"}
