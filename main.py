from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.api import auth, schedules, feedback
from app.core.config import settings
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.db.init_db import init_db  # ADD THIS

# ADD THIS: Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    print("🚀 Initializing database...")
    init_db()
    print("✅ Database ready")
    yield
    # Shutdown: cleanup if needed
    print("👋 Shutting down...")

# UPDATE THIS LINE: Add lifespan
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router)
app.include_router(schedules.router)
app.include_router(feedback.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: User = Depends(get_current_user_optional)):
    """Landing page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(get_current_user_optional)):
    """Dashboard - requires login"""
    if not user:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "user": None, "error": "Please sign in to continue"}
        )
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request):
    """Feedback page"""
    return templates.TemplateResponse("feedback.html", {"request": request})

@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    """Privacy Policy"""
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    """Terms of Service"""
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy", 
        "environment": settings.ENVIRONMENT,
        "database": "connected"  # Could add actual DB check here
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
