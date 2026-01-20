# test_db.py
from app.db.session import SessionLocal
from app.models import User
import uuid

db = SessionLocal()

# Create a test user
test_user = User(
    id=str(uuid.uuid4()),
    email="test@example.com",
    name="Test User"
)

db.add(test_user)
db.commit()

# Query it back
user = db.query(User).filter(User.email == "test@example.com").first()
print(f"✅ Created user: {user.name} ({user.email})")

db.close()
