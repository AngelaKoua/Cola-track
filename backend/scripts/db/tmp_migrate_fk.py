from sqlalchemy import text
from app.database import engine

def apply_migration():
    print("Connecting to database to update Foreign Key constraint...")
    with engine.connect() as conn:
        # Drop the existing constraint
        try:
            conn.execute(text("ALTER TABLE notifications DROP CONSTRAINT notifications_incident_id_fkey;"))
            print("Dropped old constraint.")
        except Exception as e:
            print(f"Error dropping constraint: {e}")
            
        # Add the new constraint with CASCADE
        try:
            conn.execute(text("ALTER TABLE notifications ADD CONSTRAINT notifications_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE;"))
            conn.commit()
            print("Added new constraint with ON DELETE CASCADE.")
        except Exception as e:
            print(f"Error adding constraint: {e}")
            
if __name__ == "__main__":
    apply_migration()
