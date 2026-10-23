import asyncio
import traceback
import sys
from app.database import SessionLocal
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate
from app.services.incident_service import create_incident

db = SessionLocal()
incident_data = IncidentCreate(
    ligne="Ligne 1",
    equipement="Mixer",
    type_incident="Test",
    criticite="Faible",
    description_probleme="This is a test incident",
    responsable="abdoul",
    deadline="2026-03-20"
)

try:
    db_inc = create_incident(db, incident_data)
    with open("traceback_out.txt", "w") as f:
        f.write("Success: " + str(db_inc.id))
except Exception as e:
    with open("traceback_out.txt", "w") as f:
        traceback.print_exc(file=f)
finally:
    db.close()
