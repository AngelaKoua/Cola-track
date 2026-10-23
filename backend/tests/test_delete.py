from app.database import SessionLocal
from app.models.incident import Incident
from app.services.incident_service import delete_incident

print("Testing Delete via Script...")
db = SessionLocal()
try:
    incidents = db.query(Incident).limit(5).all()
    print(f"Found {len(incidents)} incidents.")
    target_id = incidents[0].id if incidents else None

    if target_id:
        print(f"Attempting to delete first found incident {target_id}...")
        res = delete_incident(db, target_id)
        print(f"Delete result: {res}")
    else:
        print("No test incident found to delete.")
finally:
    db.close()
