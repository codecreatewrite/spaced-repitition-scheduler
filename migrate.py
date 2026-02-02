from app.db.session import SessionLocal, engine
from sqlalchemy import text
import uuid

def migrate_simple():
    """Simple migration: create topics from existing schedule.topic data"""
    
    db = SessionLocal()
    
    try:
        print("🚀 Starting migration...")
        
        # 1. Check if we need to migrate
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'schedules' AND column_name = 'topic'
        """))
        
        has_old_topic = result.fetchone() is not None
        
        if not has_old_topic:
            print("✅ Already migrated! No 'topic' column found.")
            return
        
        # 2. Get all unique topic names from schedules
        result = db.execute(text("""
            SELECT DISTINCT user_id, topic 
            FROM schedules 
            WHERE topic IS NOT NULL AND topic != ''
        """))
        
        schedule_topics = result.fetchall()
        print(f"📊 Found {len(schedule_topics)} unique topic/user combinations")
        
        # 3. Create topics and get mapping
        topic_mapping = {}  # (user_id, topic_name) -> topic_id
        
        for user_id, topic_name in schedule_topics:
            topic_id = str(uuid.uuid4())
            
            # Insert topic
            db.execute(text("""
                INSERT INTO topics (id, user_id, title, subject, difficulty, total_explains, created_at, updated_at)
                VALUES (:id, :user_id, :title, 'General', 3, 0, NOW(), NOW())
            """), {
                "id": topic_id,
                "user_id": user_id,
                "title": topic_name
            })
            
            topic_mapping[(user_id, topic_name)] = topic_id
            print(f"✅ Created topic: {topic_name} (user: {user_id[:8]}...)")
        
        db.commit()
        print("✅ All topics created")
        
        # 4. ADD THE topic_id COLUMN (THIS WAS MISSING!)
        print("📝 Adding topic_id column to schedules table...")
        db.execute(text("ALTER TABLE schedules ADD COLUMN topic_id VARCHAR"))
        db.commit()
        print("✅ Added topic_id column")
        
        # 5. Update schedules with topic_ids
        print("📝 Updating schedules with topic_ids...")
        for (user_id, topic_name), topic_id in topic_mapping.items():
            db.execute(text("""
                UPDATE schedules 
                SET topic_id = :topic_id 
                WHERE user_id = :user_id AND topic = :topic_name
            """), {
                "topic_id": topic_id,
                "user_id": user_id,
                "topic_name": topic_name
            })
        
        db.commit()
        print("✅ Updated all schedules with topic_ids")
        
        # 6. Drop old topic column
        print("📝 Dropping old 'topic' column...")
        db.execute(text("ALTER TABLE schedules DROP COLUMN topic"))
        db.commit()
        print("✅ Dropped old 'topic' column")
        
        print("🎉 Migration complete!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_simple()
