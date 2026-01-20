from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.crud import UserCRUD, TokenCRUD
from app.services.google_auth import GoogleAuthService
from app.core.security import create_access_token
import secrets

router = APIRouter(prefix="/auth", tags=["authentication"])

# Store state tokens temporarily (in production, use Redis)
# For now, we'll use a simple dict
oauth_states = {}

@router.get("/login")
async def login():
    """Initiate Google OAuth login"""
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True  # Mark as valid
    
    # Get Google authorization URL
    auth_url = GoogleAuthService.get_authorization_url(state)
    
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def auth_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    
    # Verify state (CSRF protection)
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Clean up state
    del oauth_states[state]
    
    try:
        # Exchange code for tokens
        token_data = GoogleAuthService.exchange_code_for_token(code)
        
        # Get user info from Google
        user_info = GoogleAuthService.get_user_info(token_data)
        
        # Check if user exists
        user = UserCRUD.get_by_email(db, user_info['email'])
        
        if not user:
            # Create new user
            user = UserCRUD.create(db, user_info)
        else:
            # Update last login
            UserCRUD.update_last_login(db, user.id)
        
        # Store/update OAuth token
        TokenCRUD.create_or_update(db, user.id, token_data)
        
        # Create session token (JWT)
        access_token = create_access_token(data={"sub": user.id})
        
        # Redirect to dashboard with token in cookie
        response = RedirectResponse(url="/dashboard")
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=86400,  # 24 hours
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/logout")
async def logout():
    """Log out user"""
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response
