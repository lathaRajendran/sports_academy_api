import sys
from sqlalchemy import text
from database import SessionLocal

def upgrade():
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE class_schedules ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"))
        db.commit()
        print("Successfully added is_active to class_schedules")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()
