"""
Router for technician management endpoints.

Provides APIs for:
- Listing technicians with statistics
- Getting technician details
- Creating, updating, and deleting technicians
- Toggling technician active status
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.technician import (
    TechnicianSummaryStats,
    TechnicianListItem,
    TechnicianDetail,
    TechnicianCreate,
    TechnicianUpdate,
    TechnicianStatusUpdate,
    TechnicianResponse
)
from app.services.technician_analytics import TechnicianAnalyticsService
from app.services.email_service import send_welcome_email
from app.routers.auth import get_password_hash, require_manager


# Technician management is restricted to authenticated managers
router = APIRouter(
    prefix="/api/technicians",
    tags=["Technicians"],
    dependencies=[Depends(require_manager)]
)


@router.get("/stats/summary", response_model=TechnicianSummaryStats)
def get_summary_stats(
    period_days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get summary KPIs for all technicians.
    
    Returns:
        - total: Total number of technicians
        - active: Number of active technicians
        - inactive: Number of inactive technicians
        - total_entries: Total data entries in the period
        - period_days: Period analyzed
    """
    stats = TechnicianAnalyticsService.get_summary_stats(db, period_days)
    return stats


@router.get("", response_model=List[TechnicianListItem])
def get_technicians_list(
    period_days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get list of all technicians with their activity statistics.
    
    Returns list with:
        - Basic info (id, username, status, created_at)
        - Activity stats (total_entries, last_entry, equipment_type)
    """
    technicians = TechnicianAnalyticsService.get_technicians_list(db, period_days)
    return technicians


@router.get("/{technician_id}", response_model=TechnicianDetail)
def get_technician_detail(
    technician_id: int,
    period_days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed statistics for a specific technician.
    
    Returns:
        - Basic info
        - Activity charts data (by day, by equipment, by hour)
    """
    detail = TechnicianAnalyticsService.get_technician_detail(db, technician_id, period_days)
    
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technician with id {technician_id} not found"
        )
    
    return detail


@router.post("", response_model=TechnicianResponse, status_code=status.HTTP_201_CREATED)
def create_technician(
    technician_data: TechnicianCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new technician account.
    
    Args:
        - username: Unique username
        - email: Technician's email address (will receive credentials)
    
    Returns created technician data with email_sent status.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == technician_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Auto-generate password
    generated_password = f"{technician_data.username}123"
    
    # Create new technician
    hashed_password = get_password_hash(generated_password)
    new_technician = User(
        username=technician_data.username,
        password_hash=hashed_password,
        email=technician_data.email,
        role="technician",
        is_active=True
    )
    
    db.add(new_technician)
    db.commit()
    db.refresh(new_technician)
    
    # Send welcome email with credentials
    email_sent = send_welcome_email(
        to_email=technician_data.email,
        username=technician_data.username,
        password=generated_password
    )
    
    return TechnicianResponse(
        id=new_technician.id,
        username=new_technician.username,
        email=new_technician.email,
        is_active=new_technician.is_active,
        role=new_technician.role,
        created_at=new_technician.created_at.isoformat() if new_technician.created_at else None,
        email_sent=email_sent
    )


@router.patch("/{technician_id}", response_model=TechnicianResponse)
def update_technician(
    technician_id: int,
    technician_data: TechnicianUpdate,
    db: Session = Depends(get_db)
):
    """
    Update technician information (currently only username).
    
    Args:
        - technician_id: ID of the technician to update
        - username: New username (optional)
    
    Returns updated technician data.
    """
    technician = db.query(User).filter(
        User.id == technician_id,
        User.role == "technician"
    ).first()
    
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technician with id {technician_id} not found"
        )
    
    # Update username if provided
    if technician_data.username:
        # Check if new username already exists
        existing_user = db.query(User).filter(
            User.username == technician_data.username,
            User.id != technician_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        technician.username = technician_data.username
    
    db.commit()
    db.refresh(technician)
    
    return TechnicianResponse(
        id=technician.id,
        username=technician.username,
        is_active=technician.is_active,
        role=technician.role,
        created_at=technician.created_at.isoformat() if technician.created_at else None
    )


@router.patch("/{technician_id}/status", response_model=TechnicianResponse)
def update_technician_status(
    technician_id: int,
    status_data: TechnicianStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Toggle technician active status.
    
    Args:
        - technician_id: ID of the technician
        - is_active: New status (true/false)
    
    Returns updated technician data.
    """
    technician = db.query(User).filter(
        User.id == technician_id,
        User.role == "technician"
    ).first()
    
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technician with id {technician_id} not found"
        )
    
    technician.is_active = status_data.is_active
    db.commit()
    db.refresh(technician)
    
    return TechnicianResponse(
        id=technician.id,
        username=technician.username,
        is_active=technician.is_active,
        role=technician.role,
        created_at=technician.created_at.isoformat() if technician.created_at else None
    )


@router.delete("/{technician_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_technician(
    technician_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete (deactivate) a technician.
    
    Note: This sets is_active to False without removing historical data.
    Data warehouse entries remain intact.
    
    Args:
        - technician_id: ID of the technician to delete
    """
    technician = db.query(User).filter(
        User.id == technician_id,
        User.role == "technician"
    ).first()
    
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technician with id {technician_id} not found"
        )
    
    # Soft delete: mark as inactive
    technician.is_active = False
    db.commit()
    
    return None
