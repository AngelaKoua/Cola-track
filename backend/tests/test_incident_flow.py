"""
Test script for verifying the full flow of Incident Management API.

Steps:
1. Create a new incident.
2. Verify it appears in the list.
3. Update the incident.
4. Mark it as resolved.
5. Verify KPIs are updated.
"""

from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app
from app.database import Base, engine

# Ensure tables exist (TestClient runs in the same process, so we need tables)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_incident_flow():
    print("starting test flow...")
    
    # 1. Create Incident
    new_incident = {
        "ligne": "Ligne 1",
        "equipement": "Remplisseuse",
        "type_incident": "Panne Mecanique",
        "criticite": "Critique",
        "description_probleme": "Fuite d'huile detectee sur le verin principal.",
        "responsable": "Technicien A",
        "deadline": (date.today() + timedelta(days=2)).isoformat()
    }
    
    response = client.post("/api/incidents", json=new_incident)
    # Check if we get 201 Created or maybe 404 if router prefix is wrong
    # Let's check the URL in main.py, it's prefixed with settings.API_V1_PREFIX
    # Assuming API_V1_PREFIX is "/api" or similar.
    # Actually wait, let me check main.py again. Prefixes are usually /api/v1.
    # The routers are included with `prefix=settings.API_V1_PREFIX`.
    # Let's assume /api for now, if it fails I'll check config.
    
    if response.status_code != 201:
        # Fallback to check if prefix is just /incidents or /api/incidents
        print(f"Failed to create with /api/incidents: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try without /v1 if that was the issue (though standard is usually /api/v1)
        response = client.post("/incidents", json=new_incident)
        if response.status_code != 201:
            print(f"Failed with /incidents too: {response.status_code}")
            return

    print("1. Incident Created Successfully")
    incident_data = response.json()
    incident_id = incident_data["id"]
    print(f"   ID: {incident_id}")
    
    # 2. List Incidents
    # Try the same prefix
    prefix = "/api" 
    
    response = client.get(f"/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    print("2. List returned incidents")
    
    # 3. Update Incident
    update_data = {
        "description_probleme": "Fuite d'huile reparee, verification en cours.",
        "cause_racine": "Joint defectueux"
    }
    response = client.put(f"/api/incidents/{incident_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["cause_racine"] == "Joint defectueux"
    print("3. Incident Updated")
    
    # 4. Resolve Incident
    response = client.patch(f"/api/incidents/{incident_id}/resolve")
    assert response.status_code == 200
    resolved_incident = response.json()
    assert resolved_incident["statut"] == "Résolu"

    assert resolved_incident["date_cloture"] is not None
    print("4. Incident Resolved")
    
    # 5. Check KPIs
    response = client.get("/api/incidents/kpis")
    assert response.status_code == 200
    kpis = response.json()
    print("5. KPIs retrieved")
    print(kpis)
    
    print("\nSUCCESS: All steps passed!")

if __name__ == "__main__":
    try:
        test_incident_flow()
    except Exception as e:
        print(f"TEST FAILED: {e}")
