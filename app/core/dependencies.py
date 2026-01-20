from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.crud import UserCRUD
from app.core.security import decode_access_token
from app.models.user import User
from typing import Optional

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Dependency to get current logged-in user"""
    
    # Get token from cookie
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    # Decode token
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    user_id: str = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = UserCRUD.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Optional authentication - returns None if not authenticated"""
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None
