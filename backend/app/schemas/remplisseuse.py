"""
Pydantic schemas for Remplisseuse machine data validation.

These schemas define the structure and validation rules for:
- Creating new Remplisseuse records (API requests)
- Updating existing records (API requests)
- Returning data to clients (API responses)

Pydantic automatically validates data types, ranges, and constraints.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


# ============================================================================
# BASE SCHEMA
# ============================================================================

class RemplisseuseBase(BaseModel):
    """
    Base schema with common fields for Remplisseuse data.
    
    This schema contains all the operational parameters without the ID
    and timestamp fields. It's used as a foundation for other schemas.
    """
    
    technician_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the technician recording the data",
        examples=["Jean Dupont"]
    )
    """
    Technician name for audit trail.
    Required field, 1-100 characters.
    """
    
    temperature_remplissage: float = Field(
        ...,
        ge=-50,
        le=150,
        description="Filling temperature in °C",
        examples=[4.0]
    )
    """
    Filling temperature.
    Must be between -5°C and 15°C (typical cold filling range).
    """
    
    volume_remplissage: float = Field(
        ...,
        ge=0,
        le=50,
        description="Fill volume in liters",
        examples=[1.5]
    )
    """
    Fill volume per bottle.
    Must be positive and typically less than 5 liters.
    """
    
    carbonation: float = Field(
        ...,
        ge=0,
        le=150,
        description="CO₂ carbonation level in g/L",
        examples=[8.0]
    )
    """
    CO₂ carbonation level.
    Must be between 0 and 15 g/L (typical beverage range).
    """
    
    unites_produites_conformes: float = Field(
        ...,
        ge=0,
        le=1000000,
        description="Number of conforming units produced",
        examples=[9500]
    )
    """
    Number of conforming units produced.
    Used to calculate production efficiency (rendement).
    """
    
    heures_arret: float = Field(
        ...,
        ge=0,
        le=240,
        description="Number of hours the machine was stopped",
        examples=[2.0]
    )
    """
    Number of hours the machine was stopped.
    Used to calculate production efficiency (rendement).
    """
    
    mtbf: float = Field(
        ...,
        ge=0,
        le=10000,
        description="Mean Time Between Failures in hours",
        examples=[48.0]
    )
    """
    Mean Time Between Failures.
    Must be non-negative, typically less than 1000 hours.
    """
    
    conso_air_co2: float = Field(
        ...,
        ge=0,
        le=5000,
        description="Air/CO₂ consumption in m³/h",
        examples=[120.0]
    )
    """
    Air and CO₂ consumption.
    Must be non-negative, typically less than 500 m³/h.
    """
    
    vibrations: float = Field(
        ...,
        ge=0,
        le=500,
        description="Motor vibration level in mm/s",
        examples=[2.5]
    )
    """
    Motor vibration level.
    Must be non-negative, typically less than 50 mm/s.
    
    ISO 10816 guidelines:
    - < 2.8 mm/s: Good
    - 2.8-7.1 mm/s: Acceptable
    - 7.1-18.0 mm/s: Unsatisfactory
    - > 18.0 mm/s: Unacceptable
    """


# ============================================================================
# CREATE SCHEMA
# ============================================================================

class RemplisseuseCreate(RemplisseuseBase):
    """
    Schema for creating a new Remplisseuse record.
    
    Inherits all fields from RemplisseuseBase.
    Used when receiving data from POST requests.
    
    Note: rendement is NOT included here as it is calculated
    automatically by the server based on conforming units and downtime.
    
    Example usage:
        POST /api/remplisseuse
        {
            "technician_name": "Jean Dupont",
            "temperature_remplissage": 4.0,
            "volume_remplissage": 1.5,
            "carbonation": 8.0,
            "unites_produites_conformes": 9500,
            "heures_arret": 2.0,
            ...
        }
    """
    pass


# ============================================================================
# UPDATE SCHEMA
# ============================================================================

class RemplisseuseUpdate(BaseModel):
    """
    Schema for updating an existing Remplisseuse record.
    
    All fields are optional, allowing partial updates.
    Only the fields provided in the request will be updated.
    
    Example usage:
        PUT /api/remplisseuse/{id}
        {
            "temperature_remplissage": 3.5,
            "vibrations": 2.8
        }
    """
    
    technician_name: Optional[str] = Field(None, min_length=1, max_length=100)
    temperature_remplissage: Optional[float] = Field(None, ge=-5, le=15)
    volume_remplissage: Optional[float] = Field(None, gt=0, le=5)
    carbonation: Optional[float] = Field(None, ge=0, le=15)
    unites_produites_conformes: Optional[float] = Field(None, ge=0, le=100000)
    heures_arret: Optional[float] = Field(None, ge=0, le=24)
    mtbf: Optional[float] = Field(None, ge=0, le=1000)
    conso_air_co2: Optional[float] = Field(None, ge=0, le=500)
    vibrations: Optional[float] = Field(None, ge=0, le=50)


# ============================================================================
# RESPONSE SCHEMA
# ============================================================================

class RemplisseuseResponse(RemplisseuseBase):
    """
    Schema for Remplisseuse data in API responses.
    
    Includes all fields from RemplisseuseBase plus ID, timestamps,
    and the calculated rendement field.
    Used when returning data to clients.
    
    Example response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "technician_name": "Jean Dupont",
            "temperature_remplissage": 4.0,
            "volume_remplissage": 1.5,
            "rendement": 95.0,
            ...
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """
    
    rendement: float = Field(..., description="Calculated production efficiency percentage")
    id: UUID = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)
    """
    Configuration for Pydantic v2.
    from_attributes=True allows the schema to work with SQLAlchemy models.
    This replaces the old orm_mode=True from Pydantic v1.
    """


# ============================================================================
# LIST RESPONSE SCHEMA
# ============================================================================

class RemplisseuseListResponse(BaseModel):
    """
    Schema for paginated list of Remplisseuse records.
    
    Used for GET /api/remplisseuse endpoint with pagination.
    """
    
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of records per page")
    data: list[RemplisseuseResponse] = Field(..., description="List of Remplisseuse records")
