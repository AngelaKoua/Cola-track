"""
Business logic service for Osmoseur machine operations.

This service layer handles all CRUD operations and business logic for Osmoseur data.
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

from app.models.osmoseur import Osmoseur
from app.schemas.osmoseur import OsmoseurCreate, OsmoseurUpdate


# ============================================================================
# CREATE OPERATIONS
# ============================================================================

def create_osmoseur(db: Session, osmoseur_data: OsmoseurCreate) -> Osmoseur:
    """
    Create a new Osmoseur record in the database.
    
    This function automatically calculates the taux_recuperation (recovery rate)
    based on the permeate and concentrate flow rates.
    
    Args:
        db: Database session
        osmoseur_data: Validated Osmoseur data from request
        
    Returns:
        Osmoseur: Created database record with calculated taux_recuperation
        
    Example:
        new_record = create_osmoseur(db, osmoseur_data)
        print(f"Created record with ID: {new_record.id}")
        print(f"Calculated recovery rate: {new_record.taux_recuperation}%")
    """
    # --- AUTOMATIC CALCULATION LOGIC ---
    # Calculate total flow rate
    total_flow = osmoseur_data.debit_permeat + osmoseur_data.debit_concentrat
    
    # Calculate recovery rate percentage
    # Formula: (permeate flow / total flow) * 100
    taux_recuperation = (osmoseur_data.debit_permeat / total_flow * 100) if total_flow > 0 else 0
    
    # Create new Osmoseur instance from Pydantic model
    db_osmoseur = Osmoseur(
        **osmoseur_data.model_dump(),
        taux_recuperation=round(taux_recuperation, 2)  # Add calculated value
    )
    
    # Add to session and commit to database
    db.add(db_osmoseur)
    db.commit()
    db.refresh(db_osmoseur)  # Refresh to get generated ID and timestamps
    
    return db_osmoseur


# ============================================================================
# READ OPERATIONS
# ============================================================================

def get_osmoseur_by_id(db: Session, osmoseur_id: UUID) -> Optional[Osmoseur]:
    """
    Retrieve a single Osmoseur record by its ID.
    
    Args:
        db: Database session
        osmoseur_id: UUID of the record to retrieve
        
    Returns:
        Osmoseur or None: The record if found, None otherwise
        
    Example:
        record = get_osmoseur_by_id(db, "123e4567-e89b-12d3-a456-426614174000")
        if record:
            print(f"Found record: {record.debit_permeat}")
    """
    return db.query(Osmoseur).filter(Osmoseur.id == osmoseur_id).first()


def get_all_osmoseur(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[Osmoseur]:
    """
    Retrieve a paginated list of Osmoseur records.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        sort_by: Field name to sort by (default: "created_at")
        sort_order: Sort order "asc" or "desc" (default: "desc")
        
    Returns:
        List[Osmoseur]: List of Osmoseur records
        
    Example:
        # Get the 10 most recent records
        records = get_all_osmoseur(db, skip=0, limit=10, sort_by="created_at", sort_order="desc")
        
        # Get page 2 (records 20-40)
        records = get_all_osmoseur(db, skip=20, limit=20)
    """
    query = db.query(Osmoseur)
    
    # Apply sorting
    if hasattr(Osmoseur, sort_by):
        sort_column = getattr(Osmoseur, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def get_osmoseur_count(db: Session) -> int:
    """
    Get the total count of Osmoseur records.
    
    Args:
        db: Database session
        
    Returns:
        int: Total number of records
        
    Example:
        total = get_osmoseur_count(db)
        print(f"Total records: {total}")
    """
    return db.query(Osmoseur).count()


def get_latest_osmoseur(db: Session) -> Optional[Osmoseur]:
    """
    Get the most recent Osmoseur record.
    
    Args:
        db: Database session
        
    Returns:
        Osmoseur or None: Most recent record or None if no records exist
        
    Example:
        latest = get_latest_osmoseur(db)
        if latest:
            print(f"Latest reading: {latest.debit_permeat} L/h")
    """
    return db.query(Osmoseur).order_by(desc(Osmoseur.created_at)).first()


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_osmoseur(
    db: Session,
    osmoseur_id: UUID,
    osmoseur_data: OsmoseurUpdate
) -> Optional[Osmoseur]:
    """
    Update an existing Osmoseur record.
    
    Only the fields provided in osmoseur_data will be updated.
    Other fields remain unchanged.
    
    Args:
        db: Database session
        osmoseur_id: UUID of the record to update
        osmoseur_data: Partial or complete update data
        
    Returns:
        Osmoseur or None: Updated record if found, None otherwise
        
    Example:
        # Update only specific fields
        update_data = OsmoseurUpdate(debit_permeat=16000, conductivite_permeat=12.0)
        updated = update_osmoseur(db, record_id, update_data)
    """
    # Find the record
    db_osmoseur = get_osmoseur_by_id(db, osmoseur_id)
    
    if not db_osmoseur:
        return None
    
    # Update only the fields that were provided (exclude_unset=True)
    update_data = osmoseur_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_osmoseur, field, value)
    
    # Recalculate taux_recuperation if flow rates were updated
    if 'debit_permeat' in update_data or 'debit_concentrat' in update_data:
        total_flow = db_osmoseur.debit_permeat + db_osmoseur.debit_concentrat
        taux_recuperation = (db_osmoseur.debit_permeat / total_flow * 100) if total_flow > 0 else 0
        db_osmoseur.taux_recuperation = round(taux_recuperation, 2)
    
    # Update the updated_at timestamp
    db_osmoseur.updated_at = datetime.utcnow()
    
    # Commit changes
    db.commit()
    db.refresh(db_osmoseur)
    
    return db_osmoseur


# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def delete_osmoseur(db: Session, osmoseur_id: UUID) -> bool:
    """
    Delete an Osmoseur record from the database.
    
    Args:
        db: Database session
        osmoseur_id: UUID of the record to delete
        
    Returns:
        bool: True if deleted, False if record not found
        
    Example:
        success = delete_osmoseur(db, record_id)
        if success:
            print("Record deleted successfully")
        else:
            print("Record not found")
    """
    db_osmoseur = get_osmoseur_by_id(db, osmoseur_id)
    
    if not db_osmoseur:
        return False
    
    db.delete(db_osmoseur)
    db.commit()
    
    return True


# ============================================================================
# STATISTICS AND ANALYTICS
# ============================================================================

def get_osmoseur_stats(db: Session) -> dict:
    """
    Calculate statistical summary of Osmoseur data.
    
    Computes averages for key parameters from all records.
    
    Args:
        db: Database session
        
    Returns:
        dict: Dictionary containing statistical summaries
        
    Example:
        stats = get_osmoseur_stats(db)
        print(f"Average permeate flow: {stats['avg_debit_permeat']} L/h")
    """
    from sqlalchemy import func
    
    # Query for average values
    result = db.query(
        func.avg(Osmoseur.debit_permeat).label('avg_debit_permeat'),
        func.avg(Osmoseur.debit_concentrat).label('avg_debit_concentrat'),
        func.avg(Osmoseur.taux_recuperation).label('avg_taux_recuperation'),
        func.avg(Osmoseur.conductivite_permeat).label('avg_conductivite_permeat'),
        func.avg(Osmoseur.ph_entree).label('avg_ph_entree'),
        func.avg(Osmoseur.ph_sortie).label('avg_ph_sortie'),
        func.avg(Osmoseur.turbidite).label('avg_turbidite'),
        func.avg(Osmoseur.chlore_libre).label('avg_chlore_libre'),
        func.avg(Osmoseur.durete_totale).label('avg_durete_totale'),
        func.avg(Osmoseur.tds).label('avg_tds'),
        func.count(Osmoseur.id).label('total_records')
    ).first()
    
    # Convert to dictionary with rounded values
    return {
        'avg_debit_permeat': round(result.avg_debit_permeat, 2) if result.avg_debit_permeat else 0,
        'avg_debit_concentrat': round(result.avg_debit_concentrat, 2) if result.avg_debit_concentrat else 0,
        'avg_taux_recuperation': round(result.avg_taux_recuperation, 2) if result.avg_taux_recuperation else 0,
        'avg_conductivite_permeat': round(result.avg_conductivite_permeat, 2) if result.avg_conductivite_permeat else 0,
        'avg_ph_entree': round(result.avg_ph_entree, 2) if result.avg_ph_entree else 0,
        'avg_ph_sortie': round(result.avg_ph_sortie, 2) if result.avg_ph_sortie else 0,
        'avg_turbidite': round(result.avg_turbidite, 2) if result.avg_turbidite else 0,
        'avg_chlore_libre': round(result.avg_chlore_libre, 2) if result.avg_chlore_libre else 0,
        'avg_durete_totale': round(result.avg_durete_totale, 2) if result.avg_durete_totale else 0,
        'avg_tds': round(result.avg_tds, 2) if result.avg_tds else 0,
        'total_records': result.total_records
    }
