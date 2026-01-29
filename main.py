from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.api import auth, schedules, feedback, analytics
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
app.include_router(analytics.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: User = Depends(get_current_user_optional)):
    """Landing page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user, "settings": settings}
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(get_current_user_optional)):
    """Dashboard - requires login"""
    if not user:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "user": None, "error": "Please sign in to continue", "settings": settings}
        )
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "settings": settings}
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, user: User = Depends(get_current_user_optional)):
    """Analytics page"""
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("analytics.html", {"request": request, "user": user, "settings": settings})

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request):
    """Feedback page"""
    return templates.TemplateResponse("feedback.html", {"request": request, "settings": settings})

@app.get("/admin/feedback", response_class=HTMLResponse)
async def admin_feedback(request: Request, user: User = Depends(get_current_user_optional)):
    """Admin feedback dashboard"""
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("admin_feedback.html", {"request": request})

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

# Include HEAD method for pinging
@app.head("/health")
async def healthcheckhead():
    """HEAD method for health check endpoint"""
    # Return 200 OK with no body
    return JSONResponse(content=None, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
