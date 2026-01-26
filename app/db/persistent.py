import os

def get_database_url():
    """Get database URL from environment"""
    # Render and production use DATABASE_URL env var
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # PostgreSQL URL might start with postgres:// (old) or postgresql://
        # SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Local development fallback
    return 'sqlite:///./app.db'
