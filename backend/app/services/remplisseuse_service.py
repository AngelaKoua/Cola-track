"""
Business logic service for Remplisseuse machine operations.

This service layer handles all CRUD operations and business logic for Remplisseuse data.
It sits between the API routes and the database, providing:
- Data validation
- Transaction management
- Error handling
- Query optimization
- Automatic calculation of derived metrics
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.remplisseuse import Remplisseuse
from app.schemas.remplisseuse import RemplisseuseCreate, RemplisseuseUpdate


# ============================================================================
# CREATE OPERATIONS
# ============================================================================

def create_remplisseuse(db: Session, remplisseuse_data: RemplisseuseCreate) -> Remplisseuse:
    """
    Create a new Remplisseuse record in the database.
    
    This function automatically calculates the rendement (production efficiency)
    based on the conforming units produced and machine downtime.
    
    Args:
        db: Database session
        remplisseuse_data: Validated Remplisseuse data from request
        
    Returns:
        Remplisseuse: Created database record with calculated rendement
        
    Example:
        new_record = create_remplisseuse(db, remplisseuse_data)
        print(f"Created record with ID: {new_record.id}")
        print(f"Calculated efficiency: {new_record.rendement}%")
    """
    # --- AUTOMATIC CALCULATION LOGIC ---
    # Calculate production efficiency (rendement)
    # Formula: Based on conforming units produced and machine downtime
    # This is a simplified formula - adjust based on your actual business logic
    
    # Example: rendement = (conforming units / theoretical max units) * 100
    # Assuming theoretical max is based on 24h operation minus downtime
    hours_operational = 24 - remplisseuse_data.heures_arret
    theoretical_max_units = hours_operational * 500  # Assuming 500 units/hour capacity
    
    rendement = (remplisseuse_data.unites_produites_conformes / theoretical_max_units * 100) if theoretical_max_units > 0 else 0
    # Cap at 100% to handle edge cases
    rendement = min(rendement, 100.0)
    
    # Create new Remplisseuse instance from Pydantic model
    db_remplisseuse = Remplisseuse(
        **remplisseuse_data.model_dump(),
        rendement=round(rendement, 2)  # Add calculated value
    )
    
    # Add to session and commit to database
    db.add(db_remplisseuse)
    db.commit()
    db.refresh(db_remplisseuse)  # Refresh to get generated ID and timestamps
    
    return db_remplisseuse


# ============================================================================
# READ OPERATIONS
# ============================================================================

def get_remplisseuse_by_id(db: Session, remplisseuse_id: UUID) -> Optional[Remplisseuse]:
    """
    Retrieve a single Remplisseuse record by its ID.
    
    Args:
        db: Database session
        remplisseuse_id: UUID of the record to retrieve
        
    Returns:
        Remplisseuse or None: The record if found, None otherwise
        
    Example:
        record = get_remplisseuse_by_id(db, "123e4567-e89b-12d3-a456-426614174000")
        if record:
            print(f"Found record: {record.temperature_remplissage}°C")
    """
    return db.query(Remplisseuse).filter(Remplisseuse.id == remplisseuse_id).first()


def get_all_remplisseuse(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[Remplisseuse]:
    """
    Retrieve a paginated list of Remplisseuse records.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        sort_by: Field name to sort by (default: "created_at")
        sort_order: Sort order "asc" or "desc" (default: "desc")
        
    Returns:
        List[Remplisseuse]: List of Remplisseuse records
        
    Example:
        # Get the 10 most recent records
        records = get_all_remplisseuse(db, skip=0, limit=10, sort_by="created_at", sort_order="desc")
        
        # Get page 2 (records 20-40)
        records = get_all_remplisseuse(db, skip=20, limit=20)
    """
    query = db.query(Remplisseuse)
    
    # Apply sorting
    if hasattr(Remplisseuse, sort_by):
        sort_column = getattr(Remplisseuse, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def get_remplisseuse_count(db: Session) -> int:
    """
    Get the total count of Remplisseuse records.
    
    Args:
        db: Database session
        
    Returns:
        int: Total number of records
        
    Example:
        total = get_remplisseuse_count(db)
        print(f"Total records: {total}")
    """
    return db.query(Remplisseuse).count()


def get_latest_remplisseuse(db: Session) -> Optional[Remplisseuse]:
    """
    Get the most recent Remplisseuse record.
    
    Args:
        db: Database session
        
    Returns:
        Remplisseuse or None: Most recent record or None if no records exist
        
    Example:
        latest = get_latest_remplisseuse(db)
        if latest:
            print(f"Latest temperature: {latest.temperature_remplissage}°C")
    """
    return db.query(Remplisseuse).order_by(desc(Remplisseuse.created_at)).first()


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_remplisseuse(
    db: Session,
    remplisseuse_id: UUID,
    remplisseuse_data: RemplisseuseUpdate
) -> Optional[Remplisseuse]:
    """
    Update an existing Remplisseuse record.
    
    Only the fields provided in remplisseuse_data will be updated.
    Other fields remain unchanged.
    
    Args:
        db: Database session
        remplisseuse_id: UUID of the record to update
        remplisseuse_data: Partial or complete update data
        
    Returns:
        Remplisseuse or None: Updated record if found, None otherwise
        
    Example:
        # Update only specific fields
        update_data = RemplisseuseUpdate(temperature_remplissage=3.5, vibrations=2.8)
        updated = update_remplisseuse(db, record_id, update_data)
    """
    # Find the record
    db_remplisseuse = get_remplisseuse_by_id(db, remplisseuse_id)
    
    if not db_remplisseuse:
        return None
    
    # Update only the fields that were provided (exclude_unset=True)
    update_data = remplisseuse_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_remplisseuse, field, value)
    
    # Recalculate rendement if raw data fields were updated
    if 'unites_produites_conformes' in update_data or 'heures_arret' in update_data:
        hours_operational = 24 - db_remplisseuse.heures_arret
        theoretical_max_units = hours_operational * 500
        rendement = (db_remplisseuse.unites_produites_conformes / theoretical_max_units * 100) if theoretical_max_units > 0 else 0
        db_remplisseuse.rendement = round(min(rendement, 100.0), 2)
    
    # Update the updated_at timestamp
    db_remplisseuse.updated_at = datetime.utcnow()
    
    # Commit changes
    db.commit()
    db.refresh(db_remplisseuse)
    
    return db_remplisseuse


# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def delete_remplisseuse(db: Session, remplisseuse_id: UUID) -> bool:
    """
    Delete a Remplisseuse record from the database.
    
    Args:
        db: Database session
        remplisseuse_id: UUID of the record to delete
        
    Returns:
        bool: True if deleted, False if record not found
        
    Example:
        success = delete_remplisseuse(db, record_id)
        if success:
            print("Record deleted successfully")
        else:
            print("Record not found")
    """
    db_remplisseuse = get_remplisseuse_by_id(db, remplisseuse_id)
    
    if not db_remplisseuse:
        return False
    
    db.delete(db_remplisseuse)
    db.commit()
    
    return True


# ============================================================================
# STATISTICS AND ANALYTICS
# ============================================================================

def get_remplisseuse_stats(db: Session) -> dict:
    """
    Calculate statistical summary of Remplisseuse data.
    
    Computes averages for key parameters from all records.
    
    Args:
        db: Database session
        
    Returns:
        dict: Dictionary containing statistical summaries
        
    Example:
        stats = get_remplisseuse_stats(db)
        print(f"Average efficiency: {stats['avg_rendement']}%")
    """
    from sqlalchemy import func
    
    # Query for average values
    result = db.query(
        func.avg(Remplisseuse.temperature_remplissage).label('avg_temperature_remplissage'),
        func.avg(Remplisseuse.volume_remplissage).label('avg_volume_remplissage'),
        func.avg(Remplisseuse.carbonation).label('avg_carbonation'),
        func.avg(Remplisseuse.mtbf).label('avg_mtbf'),
        func.avg(Remplisseuse.rendement).label('avg_rendement'),
        func.avg(Remplisseuse.conso_air_co2).label('avg_conso_air_co2'),
        func.avg(Remplisseuse.vibrations).label('avg_vibrations'),
        func.count(Remplisseuse.id).label('total_records')
    ).first()
    
    # Convert to dictionary with rounded values
    return {
        'avg_temperature_remplissage': round(result.avg_temperature_remplissage, 2) if result.avg_temperature_remplissage else 0,
        'avg_volume_remplissage': round(result.avg_volume_remplissage, 2) if result.avg_volume_remplissage else 0,
        'avg_carbonation': round(result.avg_carbonation, 2) if result.avg_carbonation else 0,
        'avg_mtbf': round(result.avg_mtbf, 2) if result.avg_mtbf else 0,
        'avg_rendement': round(result.avg_rendement, 2) if result.avg_rendement else 0,
        'avg_conso_air_co2': round(result.avg_conso_air_co2, 2) if result.avg_conso_air_co2 else 0,
        'avg_vibrations': round(result.avg_vibrations, 2) if result.avg_vibrations else 0,
        'total_records': result.total_records
    }
