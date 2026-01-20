import os
from pathlib import Path

def get_database_url():
    """Get database URL based on environment"""
    
    # Check if we're on Render (they set this env var)
    if os.getenv('RENDER'):
        # Use Render's persistent disk path
        db_path = '/var/data/app.db'
        
        # Create directory if it doesn't exist
        Path('/var/data').mkdir(parents=True, exist_ok=True)
        
        return f'sqlite:///{db_path}'
    
    # Local development
    return 'sqlite:///./app.db'
