from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.feedback import Feedback
from app.core.dependencies import get_current_user_optional
from app.core.email import send_feedback_email
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
    # Save feedback to DB
    feedback = Feedback(
        id=str(uuid.uuid4()),
        name=feedback_data.name or "Anonymous",
        email=feedback_data.email or "not provided",
        type=feedback_data.type,
        message=feedback_data.message,
        user_id=current_user.id if current_user else None
    )
    db.add(feedback)
    db.commit()

    # Send email
    send_feedback_email(
        name=feedback.name,
        email=feedback.email,
        feedback_type=feedback.type,
        message=feedback.message
    )

    return {"success": True, "message": "Feedback received and email sent."}
