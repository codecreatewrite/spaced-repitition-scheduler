from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.db.session import get_db
from app.db.crud import ScheduleCRUD
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/api/schedules", tags=["schedules"])

# Request/Response models
class CreateScheduleRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="Topic or subject to review")
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    intervals: Optional[str] = Field(None, description="Comma-separated intervals (e.g., '1,3,7,21')")
    topic_id: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: str
    topic: str
    start_date: str
    intervals: List[int]
    review_dates: List[str]


def generate_review_dates(start_date: date, intervals: List[int]) -> List[date]:
    """
    Generate review dates based on StudyCore intervals.
    
    Args:
        start_date: The date to start from
        intervals: List of days to add (e.g., [1, 3, 7, 21])
    
    Returns:
        List of review dates
    """
    return [start_date + timedelta(days=interval) for interval in intervals]


@router.post("/create", response_model=dict)
async def create_schedule(
    request: CreateScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new spaced repetition schedule (internal tracking only).
    """
    
    # Parse start date (default to today if not provided)
    if request.start_date:
        try:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        start_date = date.today()
    
    # Parse intervals (default to settings if not provided)
    if request.intervals:
        try:
            intervals = [int(x.strip()) for x in request.intervals.split(',')]
            if not intervals or any(i <= 0 for i in intervals):
                raise ValueError("Intervals must be positive numbers")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid intervals: {str(e)}")
    else:
        intervals = settings.intervals_list
    
    # Generate review dates
    review_dates = generate_review_dates(start_date, intervals)
    
    try:
        # Store schedule in database (internal tracking only)
        schedule_data = {
            'user_id': current_user.id,
            'topic': request.topic,
            'topic_id': request.topic_id,
            'start_date': start_date,
            'intervals': intervals,
        }
        
        schedule = ScheduleCRUD.create(db, schedule_data)
        
        return {
            'success': True,
            'schedule_id': schedule.id,
            'topic': request.topic,
            'start_date': start_date.isoformat(),
            'intervals': intervals,
            'review_dates': [d.isoformat() for d in review_dates],
            'total_created': len(review_dates),
            'message': f"Successfully created schedule for '{request.topic}' with {len(review_dates)} review dates"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")


@router.get("/my-schedules")
async def get_my_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all schedules for the current user"""
    schedules = ScheduleCRUD.get_by_user(db, current_user.id)
    
    return {
        'total': len(schedules),
        'schedules': [
            {
                'id': s.id,
                'topic': s.topic,
                'start_date': s.start_date.isoformat(),
                'intervals': s.intervals,
                'created_at': s.created_at.isoformat(),
                'review_count': len(s.intervals) if s.intervals else 0
            }
            for s in schedules
        ]
    }
