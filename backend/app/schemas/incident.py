"""
Pydantic schemas for Incident Management.

These schemas define the structure and validation rules for:
- Creating new Incidents
- Updating existing Incidents
- returning Incident data
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID


# ============================================================================
# BASE SCHEMA
# ============================================================================

class IncidentBase(BaseModel):
    """
    Base schema with common fields for Incidents.
    """
    ligne: str = Field(..., min_length=1, max_length=100, description="Production line")
    equipement: str = Field(..., min_length=1, max_length=150, description="Equipment name")
    type_incident: str = Field(..., min_length=1, max_length=50, description="Type of incident")
    criticite: str = Field(..., description="Criticality level (Critique, Élevé, Moyen, Faible)")
    description_probleme: str = Field(..., min_length=5, description="Detailed description of the problem")
    responsable: str = Field(..., min_length=1, max_length=150, description="Person responsible for resolution")
    deadline: date = Field(..., description="Deadline for resolution")
    
    @field_validator('criticite')
    @classmethod
    def validate_criticite(cls, v: str) -> str:
        valid_values = ["Critique", "Élevé", "Moyen", "Faible"]
        if v not in valid_values:
            raise ValueError(f"Criticité must be one of {valid_values}")
        return v


# ============================================================================
# CREATE SCHEMA
# ============================================================================

class IncidentCreate(IncidentBase):
    """
    Schema for creating a new Incident.
    """
    cause_racine: Optional[str] = Field(None, description="Root cause analysis (optional at creation)")
    action_corrective: Optional[str] = Field(None, description="Corrective action taken (optional at creation)")


# ============================================================================
# UPDATE SCHEMA
# ============================================================================

class IncidentUpdate(BaseModel):
    """
    Schema for updating an existing Incident.
    """
    ligne: Optional[str] = Field(None, min_length=1, max_length=100)
    equipement: Optional[str] = Field(None, min_length=1, max_length=150)
    type_incident: Optional[str] = Field(None, min_length=1, max_length=50)
    criticite: Optional[str] = Field(None)
    description_probleme: Optional[str] = Field(None, min_length=5)
    cause_racine: Optional[str] = Field(None)
    action_corrective: Optional[str] = Field(None)
    responsable: Optional[str] = Field(None, min_length=1, max_length=150)
    deadline: Optional[date] = Field(None)
    statut: Optional[str] = Field(None, description="Ouvert, En cours, En attente, Résolu")

    
    @field_validator('criticite')
    @classmethod
    def validate_criticite(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_values = ["Critique", "Élevé", "Moyen", "Faible"]
        if v not in valid_values:
            raise ValueError(f"Criticité must be one of {valid_values}")
        return v

    @field_validator('statut')
    @classmethod
    def validate_statut(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_values = ["Ouvert", "En cours", "En attente", "Résolu"]
        if v not in valid_values:
            raise ValueError(f"Statut must be one of {valid_values}")
        return v


# ============================================================================
# RESPONSE SCHEMA
# ============================================================================

class IncidentResponse(IncidentBase):
    """
    Schema for Incident data in API responses.
    """
    id: UUID
    date_declaration: datetime
    cause_racine: Optional[str] = None
    action_corrective: Optional[str] = None
    statut: str

    date_cloture: Optional[datetime] = None
    temps_resolution: Optional[timedelta] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# LIST RESPONSE SCHEMA
# ============================================================================

class IncidentListResponse(BaseModel):
    """
    Schema for paginated list of Incidents.
    """
    total: int
    page: int
    page_size: int
    data: list[IncidentResponse]
    
# ============================================================================
# KPI RESPONSE SCHEMA
# ============================================================================

class IncidentKPI(BaseModel):
    """
    Schema for Key Performance Indicators.
    """
    total_incidents: int
    incidents_ouverts: int
    incidents_critiques: int
    mttr_moyen_heures: float
    respect_deadline_percent: float
