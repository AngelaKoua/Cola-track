"""
Service layer for Incident Management.

Handles business logic for:
- Creating incidents
- Updating status/resolution
- KPI calculations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from datetime import timezone

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.notification_service import (
    trigger_assignation_notification,
    trigger_critical_notification
)


# ============================================================================
# CRUD OPERATIONS
# ============================================================================

def create_incident(db: Session, incident: IncidentCreate) -> Incident:
    """
    Create a new incident.
    """
    db_incident = Incident(
        ligne=incident.ligne,
        equipement=incident.equipement,
        type_incident=incident.type_incident,
        criticite=incident.criticite,
        description_probleme=incident.description_probleme,
        cause_racine=incident.cause_racine,
        action_corrective=incident.action_corrective,
        responsable=incident.responsable,
        deadline=incident.deadline,
        statut="Ouvert",

    )
    
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    # Trigger notifications
    trigger_assignation_notification(db, db_incident)
    if db_incident.criticite == "Critique":
        trigger_critical_notification(db, db_incident)

    return db_incident


def get_incident(db: Session, incident_id: UUID) -> Optional[Incident]:
    """
    Get incident by ID.
    """
    return db.query(Incident).filter(Incident.id == incident_id).first()


def get_all_incidents(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    ligne: Optional[str] = None,
    statut: Optional[str] = None,
    criticite: Optional[str] = None,
    responsable: Optional[str] = None
) -> List[Incident]:
    """
    Get all incidents with optional filtering.
    """
    query = db.query(Incident)
    
    if ligne:
        query = query.filter(Incident.ligne == ligne)
    if statut:
        query = query.filter(Incident.statut == statut)
    if criticite:
        query = query.filter(Incident.criticite == criticite)
    if responsable:
        query = query.filter(Incident.responsable.ilike(f"%{responsable}%"))
        
    return query.order_by(Incident.date_declaration.desc()).offset(skip).limit(limit).all()


def get_incident_count(db: Session) -> int:
    """
    Get total count of incidents.
    """
    return db.query(func.count(Incident.id)).scalar()


def update_incident(db: Session, incident_id: UUID, incident_update: IncidentUpdate) -> Optional[Incident]:
    """
    Update an incident.
    Handles automatic status updates and resolution timestamping.
    """
    db_incident = get_incident(db, incident_id)
    if not db_incident:
        return None
    
    # Capture original status before update
    original_statut = db_incident.statut
    original_responsable = db_incident.responsable
    
    update_data = incident_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_incident, key, value)
    
    # Business Logic: Use statut for resolution tracking
    if incident_update.statut == "Résolu" and original_statut != "Résolu":
        # Ensure status is set (already done by setattr but good for clarity if logic changes)
        db_incident.statut = "Résolu" 
        if not db_incident.date_cloture:
            db_incident.date_cloture = datetime.now(timezone.utc)
            if db_incident.date_declaration:
                # Basic duration calculation
                db_incident.temps_resolution = db_incident.date_cloture - db_incident.date_declaration

    elif incident_update.statut and incident_update.statut != "Résolu" and original_statut == "Résolu":
        # Reopening incident
        db_incident.date_cloture = None
        db_incident.temps_resolution = None

    # Trigger notification if responsable changed
    if incident_update.responsable and incident_update.responsable != original_responsable:
        trigger_assignation_notification(db, db_incident)

    db.commit()
    db.refresh(db_incident)
    return db_incident


def delete_incident(db: Session, incident_id: UUID) -> bool:
    """
    Delete an incident.
    """
    print(f"DEBUG: Attempting to delete incident_id={incident_id}")
    db_incident = get_incident(db, incident_id)
    if not db_incident:
        print("DEBUG: Incident not found in db_incident")
        return False
    
    db.delete(db_incident)
    try:
        db.commit()
        print("DEBUG: Commit successful")
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Commit failed with exception {e}")
        return False
    return True

# ============================================================================
# KPI ANALYTICS
# ============================================================================

def get_incident_kpis(db: Session) -> Dict:
    """
    Calculate KPIs for the dashboard.
    """
    total = db.query(func.count(Incident.id)).scalar()
    
    # Open Incidents (Not resolved)
    ouverts = db.query(func.count(Incident.id)).filter(Incident.statut != "Résolu").scalar()
    
    # Critical Incidents
    critiques = db.query(func.count(Incident.id)).filter(Incident.criticite == "Critique").scalar()
    
    # MTTR (Mean Time To Repair) - Average of temps_resolution
    # Note: temps_resolution is an Interval
    avg_duration = db.query(func.avg(Incident.temps_resolution)).filter(Incident.statut == "Résolu").scalar()
    
    mttr_hours = 0.0
    if avg_duration:
        # avg_duration is a timedelta
        mttr_hours = avg_duration.total_seconds() / 3600.0
        
    # Respect Deadline %
    # Count resolved incidents where date_cloture <= deadline
    # Note: deadline is Date, date_cloture is DateTime. Need to cast.
    
    resolved_count = db.query(func.count(Incident.id)).filter(Incident.statut == "Résolu").scalar()
    
    if resolved_count > 0:
        on_time = db.query(func.count(Incident.id)).filter(
            Incident.statut == "Résolu",
            func.date(Incident.date_cloture) <= Incident.deadline
        ).scalar()
        deadline_percent = (on_time / resolved_count) * 100.0
    else:
        deadline_percent = 100.0 # Default if no resolved incidents? or 0? 
        # If no resolved incidents, strictly speaking it's N/A. Let's return 0 or 100. 
        # Typically 100 if nothing was late.
    
    return {
        "total_incidents": total or 0,
        "incidents_ouverts": ouverts or 0,
        "incidents_critiques": critiques or 0,
        "mttr_moyen_heures": round(mttr_hours, 2),
        "respect_deadline_percent": round(deadline_percent, 1)
    }
