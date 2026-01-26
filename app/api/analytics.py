from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.analytics_service import AnalyticsService
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user analytics and statistics"""
    stats = AnalyticsService.get_user_stats(db, current_user.id)
    return stats
