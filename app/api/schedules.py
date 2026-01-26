from app.services.analytics_service import AnalyticsService
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional
from app.db.session import get_db
from app.db.crud import TokenCRUD, ScheduleCRUD
from app.core.dependencies import get_current_user
from app.services.calendar_service import CalendarService
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/api/schedules", tags=["schedules"])

# Request/Response models
class CreateScheduleRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="Topic or subject to review")
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    intervals: Optional[str] = Field(None, description="Comma-separated intervals (e.g., '1,3,7,21')")
    calendar_id: str = Field("primary", description="Google Calendar ID")

class ScheduleResponse(BaseModel):
    id: str
    topic: str
    start_date: str
    intervals: List[int]
    review_dates: List[str]
    events_created: int
    calendar_link: Optional[str] = None

@router.post("/create", response_model=dict)
async def create_schedule(
    request: CreateScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new spaced repetition schedule and add events to Google Calendar.
    """
    
    # Get user's OAuth token
    token_record = TokenCRUD.get_by_user(db, current_user.id)
    if not token_record:
        raise HTTPException(status_code=401, detail="Google Calendar access not authorized")
    
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
    
    # Initialize Calendar Service with user's credentials
    calendar_service = CalendarService(token_record.token_data)
    
    try:
        # Create the full schedule in Google Calendar
        result = calendar_service.create_full_schedule(
            topic=request.topic,
            start_date=start_date,
            intervals=intervals,
            calendar_id=request.calendar_id
        )
        
        if result['total_failed'] > 0:
            # Some events failed
            raise HTTPException(
                status_code=500,
                detail=f"Created {result['total_created']} events, but {result['total_failed']} failed"
            )
        
        # Store schedule in database
        event_ids = [e['event_id'] for e in result['events'] if 'event_id' in e]
        schedule_data = {
            'user_id': current_user.id,
            'topic': request.topic,
            'start_date': start_date,
            'intervals': intervals,
            'calendar_id': request.calendar_id,
            'calendar_event_ids': event_ids
        }
        
        schedule = ScheduleCRUD.create(db, schedule_data)

        AnalyticsService.update_schedule_created(db, current_user.id, len(event_ids))
        
        return {
            'success': True,
            'schedule_id': schedule.id,
            'topic': result['topic'],
            'start_date': result['start_date'],
            'intervals': result['intervals'],
            'review_dates': result['review_dates'],
            'events': result['events'],
            'total_created': result['total_created'],
            'message': f"Successfully created {result['total_created']} review events for '{request.topic}'"
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
                'events_count': len(s.calendar_event_ids) if s.calendar_event_ids else 0
            }
            for s in schedules
        ]
    }

@router.get("/calendars")
async def get_calendars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of user's Google Calendars"""
    token_record = TokenCRUD.get_by_user(db, current_user.id)
    if not token_record:
        raise HTTPException(status_code=401, detail="Google Calendar access not authorized")
    
    calendar_service = CalendarService(token_record.token_data)
    
    try:
        calendars = calendar_service.list_calendars()
        return {'calendars': calendars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendars: {str(e)}")
