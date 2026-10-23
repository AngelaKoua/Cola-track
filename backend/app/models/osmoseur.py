"""
SQLAlchemy ORM model for Osmoseur machine data.

This model represents the 'osmoseur' table in the PostgreSQL database.
It stores operational parameters for the reverse osmosis (Osmoseur) machine.
"""

from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Osmoseur(Base):
    """
    Osmoseur machine data model.
    
    Stores operational parameters for the reverse osmosis water treatment system.
    Each record represents a snapshot of machine parameters at a specific time.
    
    Table: osmoseur_readings
    """
    
    __tablename__ = "osmoseur_readings"
    
    # ============================================================================
    # PRIMARY KEY
    # ============================================================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True
    )
    """Unique identifier for each record (UUID format)"""
    
    # ============================================================================
    # TECHNICIAN INFORMATION
    # ============================================================================
    technician_name = Column(String(100), nullable=False)
    """
    Name of the technician who recorded this data.
    Required for audit trail and accountability.
    """
    
    # ============================================================================
    # FLOW RATE PARAMETERS
    # ============================================================================
    debit_permeat = Column(Float, nullable=False)
    """
    Permeate flow rate in L/h (liters per hour).
    This is the purified water output from the reverse osmosis system.
    Typical range: 10,000 - 20,000 L/h
    """
    
    debit_concentrat = Column(Float, nullable=False)
    """
    Concentrate flow rate in L/h (liters per hour).
    This is the rejected water containing concentrated impurities.
    Typical range: 3,000 - 7,000 L/h
    """
    
    taux_recuperation = Column(Float, nullable=False)
    """
    Recovery rate as a percentage (%).
    Ratio of permeate to total feed water.
    Formula: (debit_permeat / (debit_permeat + debit_concentrat)) * 100
    Typical range: 70% - 80%
    """
    
    # ============================================================================
    # WATER QUALITY PARAMETERS
    # ============================================================================
    conductivite_permeat = Column(Float, nullable=False)
    """
    Permeate conductivity in µS/cm (microsiemens per centimeter).
    Measures the electrical conductivity of purified water.
    Lower values indicate better water quality.
    Typical range: 10 - 30 µS/cm
    """
    
    ph_entree = Column(Float, nullable=False)
    """
    Inlet pH level (dimensionless).
    Measures acidity/alkalinity of feed water.
    Typical range: 6.5 - 8.0
    """
    
    ph_sortie = Column(Float, nullable=False)
    """
    Outlet pH level (dimensionless).
    Measures acidity/alkalinity of permeate water.
    Typical range: 6.0 - 7.5
    """
    
    turbidite = Column(Float, nullable=False)
    """
    Turbidity in NTU (Nephelometric Turbidity Units).
    Measures water cloudiness/clarity.
    Lower values indicate clearer water.
    Typical range: 0.1 - 1.0 NTU
    """
    
    chlore_libre = Column(Float, nullable=False)
    """
    Free chlorine concentration in mg/L (milligrams per liter).
    Measures residual chlorine in water.
    Should be minimal in permeate.
    Typical range: 0.0 - 0.2 mg/L
    """
    
    durete_totale = Column(Float, nullable=False)
    """
    Total hardness in °f (French degrees).
    Measures calcium and magnesium content.
    Should be near zero in permeate.
    Typical range: 0 - 2 °f
    """
    
    tds = Column(Float, nullable=False)
    """
    Total Dissolved Solids in ppm (parts per million).
    Measures total concentration of dissolved substances.
    Lower values indicate better water quality.
    Typical range: 5 - 20 ppm
    """
    
    # ============================================================================
    # TIMESTAMP FIELDS
    # ============================================================================
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    """
    Timestamp when the record was created.
    Automatically set to current UTC time when record is inserted.
    Indexed for efficient time-based queries.
    """
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    """
    Timestamp when the record was last updated.
    Automatically updated to current UTC time on any modification.
    """
    
    def __repr__(self):
        """String representation of the Osmoseur record"""
        return f"<Osmoseur(id={self.id}, created_at={self.created_at})>"
