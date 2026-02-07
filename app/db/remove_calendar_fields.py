"""
Migration: Remove Google Calendar integration fields
Run this ONCE to clean up the database
"""
from sqlalchemy import text
from app.db.session import get_db

def remove_calendar_fields():
    """Remove calendar_event_ids and calendar_id from schedules table"""
    db = next(get_db())
    
    try:
        # PostgreSQL syntax to drop columns
        db.execute(text("""
            ALTER TABLE schedules 
            DROP COLUMN IF EXISTS calendar_event_ids,
            DROP COLUMN IF EXISTS calendar_id;
        """))
        db.commit()
        print("✅ Successfully removed calendar fields from schedules table")
    except Exception as e:
        db.rollback()
        print(f"❌ Error removing calendar fields: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    remove_calendar_fields()
