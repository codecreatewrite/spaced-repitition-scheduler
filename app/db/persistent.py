import os

def get_database_url():
    """Get database URL - ephemeral for free tier"""
    
    if os.getenv('RENDER'):
        # Use /tmp directory which is writable on Render free tier
        return 'sqlite:////tmp/app.db'
    
    # Local development
    return 'sqlite:///./app.db'
