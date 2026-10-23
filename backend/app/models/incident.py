"""
SQLAlchemy ORM model for Incidents and Corrective Actions.

This model represents the 'incidents' table in the PostgreSQL database.
It stores details about operational incidents, their status, and resolution.
"""

from sqlalchemy import Column, String, Text, Date, DateTime, Boolean, Interval, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class Incident(Base):
    """
    Incident Management Data Model.
    
    Stores information about incidents, including declaration, assignment,
    status tracking, and resolution details.
    
    Table: incidents
    """
    
    __tablename__ = "incidents"
    
    # ============================================================================
    # IDENTIFICATION
    # ============================================================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True
    )
    
    # ============================================================================
    # DECLARATION INFO
    # ============================================================================
    date_declaration = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
    
    ligne = Column(String(100), nullable=False)
    equipement = Column(String(150), nullable=False)
    type_incident = Column(String(50), nullable=False)
    
    # ============================================================================
    # DETAILS & ANALYSIS
    # ============================================================================
    criticite = Column(String(20), nullable=False)  # Critique, Élevé, Moyen, Faible
    description_probleme = Column(Text, nullable=False)
    cause_racine = Column(Text, nullable=True)
    action_corrective = Column(Text, nullable=True)
    
    # ============================================================================
    # ASSIGNMENT & STATUS
    # ============================================================================
    responsable = Column(String(150), nullable=False)
    deadline = Column(Date, nullable=False)
    
    statut = Column(String(50), default='Ouvert', nullable=False)  # Ouvert, En cours, En attente, Résolu

    
    # ============================================================================
    # RESOLUTION METRICS
    # ============================================================================
    date_cloture = Column(DateTime(timezone=True), nullable=True)
    temps_resolution = Column(Interval, nullable=True)
    
    def __repr__(self):
        return f"<Incident(id={self.id}, ligne={self.ligne}, type={self.type_incident}, statut={self.statut})>"
