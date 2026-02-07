from app.db.session import engine
from sqlalchemy import text

def add_updated_at_column():
    """Add updated_at column to schedules table"""
    
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='schedules' 
            AND column_name='updated_at';
        """))
        
        if not result.fetchone():
            # Add the column
            conn.execute(text("""
                ALTER TABLE schedules 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """))
            
            # Set existing rows to created_at value
            conn.execute(text("""
                UPDATE schedules 
                SET updated_at = created_at 
                WHERE updated_at IS NULL;
            """))
            
            conn.commit()
            print("✅ Added updated_at column to schedules table")
        else:
            print("✅ updated_at column already exists")

if __name__ == "__main__":
    add_updated_at_column()
