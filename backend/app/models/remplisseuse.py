"""
SQLAlchemy ORM model for Remplisseuse machine data.

This model represents the 'remplisseuse' table in the PostgreSQL database.
It stores operational parameters for the filling machine (Remplisseuse).
"""

from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Remplisseuse(Base):
    """
    Remplisseuse (Filling Machine) data model.
    
    Stores operational parameters for the bottle filling and carbonation system.
    Each record represents a snapshot of machine parameters at a specific time.
    
    Table: remplisseuse_readings
    """
    
    __tablename__ = "remplisseuse_readings"
    
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
    # FILLING PROCESS PARAMETERS
    # ============================================================================
    temperature_remplissage = Column(Float, nullable=False)
    """
    Filling temperature in °C (degrees Celsius).
    Temperature of the liquid during the filling process.
    Critical for product quality and carbonation retention.
    Typical range: 2.0 - 6.0 °C
    """
    
    volume_remplissage = Column(Float, nullable=False)
    """
    Fill volume in L (liters).
    Volume of liquid dispensed per bottle.
    Must be precise for regulatory compliance.
    Typical range: 0.5 - 2.0 L (depending on bottle size)
    """
    
    carbonation = Column(Float, nullable=False)
    """
    CO₂ carbonation level in g/L (grams per liter).
    Concentration of dissolved carbon dioxide.
    Determines the fizziness of the beverage.
    Typical range: 6.0 - 10.0 g/L
    """
    
    # ============================================================================
    # RAW DATA FOR AUTOMATIC CALCULATION
    # ============================================================================
    unites_produites_conformes = Column(Float, nullable=False)
    """
    Number of conforming units produced.
    Used to calculate production efficiency (rendement).
    Typical range: 0 - 10000 units
    """
    
    heures_arret = Column(Float, nullable=False)
    """
    Number of hours the machine was stopped.
    Used to calculate production efficiency (rendement).
    Typical range: 0 - 24 hours
    """
    
    # ============================================================================
    # RELIABILITY AND PERFORMANCE METRICS
    # ============================================================================
    mtbf = Column(Float, nullable=False)
    """
    MTBF (Mean Time Between Failures) in hours.
    Average operating time between equipment failures.
    Higher values indicate better reliability.
    Typical range: 24 - 200 hours
    """
    
    rendement = Column(Float, nullable=False)
    """
    Production efficiency as a percentage (%).
    Ratio of actual output to theoretical maximum output.
    Formula: (actual_production / theoretical_production) * 100
    Typical range: 85% - 99%
    """
    
    # ============================================================================
    # RESOURCE CONSUMPTION
    # ============================================================================
    conso_air_co2 = Column(Float, nullable=False)
    """
    Air/CO₂ consumption in m³/h (cubic meters per hour).
    Combined consumption of compressed air and carbon dioxide.
    Important for operational cost tracking.
    Typical range: 80 - 150 m³/h
    """
    
    # ============================================================================
    # MECHANICAL HEALTH INDICATORS
    # ============================================================================
    vibrations = Column(Float, nullable=False)
    """
    Motor vibration level in mm/s (millimeters per second).
    RMS (Root Mean Square) vibration velocity.
    Indicator of mechanical health and bearing condition.
    
    Vibration severity guidelines (ISO 10816):
    - < 2.8 mm/s: Good condition
    - 2.8 - 7.1 mm/s: Acceptable
    - 7.1 - 18.0 mm/s: Unsatisfactory (maintenance required)
    - > 18.0 mm/s: Unacceptable (immediate action required)
    
    Typical range: 1.0 - 5.0 mm/s
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
        """String representation of the Remplisseuse record"""
        return f"<Remplisseuse(id={self.id}, created_at={self.created_at})>"
