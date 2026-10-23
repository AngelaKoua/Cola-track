"""
API Router for Incident Management.

Exposes REST endpoints for:
- Creating, reading, updating, deleting incidents
- Resolving incidents
- Fetching KPI statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    IncidentKPI
)
from app.services.incident_service import (
    create_incident,
    get_incident,
    get_all_incidents,
    get_incident_count,
    update_incident,
    delete_incident,
    get_incident_kpis
)

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
    responses={404: {"description": "Not found"}}
)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_new_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    """
    Create a new incident.
    """
    return create_incident(db=db, incident=incident)


@router.get("", response_model=IncidentListResponse)
def read_incidents(
    skip: int = 0,
    limit: int = 50,
    ligne: Optional[str] = None,
    statut: Optional[str] = None,
    criticite: Optional[str] = None,
    responsable: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get a list of incidents with optional filtering.
    """
    incidents = get_all_incidents(
        db, 
        skip=skip, 
        limit=limit,
        ligne=ligne,
        statut=statut,
        criticite=criticite,
        responsable=responsable
    )
    total = get_incident_count(db)
    
    return {
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "data": incidents
    }


@router.get("/kpis", response_model=IncidentKPI)
def read_kpis(db: Session = Depends(get_db)):
    """
    Get KPI statistics for the dashboard.
    """
    return get_incident_kpis(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def read_incident(incident_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific incident by ID.
    """
    db_incident = get_incident(db, incident_id=incident_id)
    if db_incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db_incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_existing_incident(
    incident_id: UUID, 
    incident_update: IncidentUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an incident.
    """
    db_incident = update_incident(db, incident_id=incident_id, incident_update=incident_update)
    if db_incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db_incident


@router.patch("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(incident_id: UUID, db: Session = Depends(get_db)):
    """
    Mark an incident as resolved.
    """
    update_data = IncidentUpdate(statut="Résolu")
    db_incident = update_incident(db, incident_id=incident_id, incident_update=update_data)
    if db_incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db_incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_incident(incident_id: UUID, db: Session = Depends(get_db)):
    """
    Delete an incident.
    """
    success = delete_incident(db, incident_id=incident_id)
    if not success:
        raise HTTPException(status_code=404, detail="Incident not found")
    return None
