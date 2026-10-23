"""
Pydantic schemas for Osmoseur machine data validation.

These schemas define the structure and validation rules for:
- Creating new Osmoseur records (API requests)
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

class OsmoseurBase(BaseModel):
    """
    Base schema with common fields for Osmoseur data.
    
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
    
    debit_permeat: float = Field(
        ...,
        ge=0,
        le=30000,
        description="Permeate flow rate in L/h",
        examples=[15000]
    )
    """
    Permeate flow rate (purified water output).
    Must be positive and typically less than 30,000 L/h.
    """
    
    debit_concentrat: float = Field(
        ...,
        ge=0,
        le=15000,
        description="Concentrate flow rate in L/h",
        examples=[5000]
    )
    """
    Concentrate flow rate (rejected water).
    Must be positive and typically less than 15,000 L/h.
    """
    
    conductivite_permeat: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Permeate conductivity in µS/cm",
        examples=[15.0]
    )
    """
    Permeate conductivity.
    Must be non-negative, typically less than 100 µS/cm.
    """
    
    ph_entree: float = Field(
        ...,
        ge=0,
        le=100,
        description="Inlet pH level",
        examples=[7.2]
    )
    """
    Inlet pH level.
    Must be between 0 and 14 (pH scale).
    """
    
    ph_sortie: float = Field(
        ...,
        ge=0,
        le=100,
        description="Outlet pH level",
        examples=[6.8]
    )
    """
    Outlet pH level.
    Must be between 0 and 14 (pH scale).
    """
    
    turbidite: float = Field(
        ...,
        ge=0,
        le=100,
        description="Turbidity in NTU",
        examples=[0.5]
    )
    """
    Turbidity measurement.
    Must be non-negative, typically less than 10 NTU.
    """
    
    chlore_libre: float = Field(
        ...,
        ge=0,
        le=100,
        description="Free chlorine in mg/L",
        examples=[0.1]
    )
    """
    Free chlorine concentration.
    Must be non-negative, typically less than 5 mg/L.
    """
    
    durete_totale: float = Field(
        ...,
        ge=0,
        le=500,
        description="Total hardness in °f",
        examples=[0.0]
    )
    """
    Total hardness.
    Must be non-negative, typically less than 50 °f.
    """
    
    tds: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Total Dissolved Solids in ppm",
        examples=[10.0]
    )
    """
    Total Dissolved Solids.
    Must be non-negative, typically less than 100 ppm.
    """


# ============================================================================
# CREATE SCHEMA
# ============================================================================

class OsmoseurCreate(OsmoseurBase):
    """
    Schema for creating a new Osmoseur record.
    
    Inherits all fields from OsmoseurBase.
    Used when receiving data from POST requests.
    
    Note: taux_recuperation is NOT included here as it is calculated
    automatically by the server based on flow rates.
    
    Example usage:
        POST /api/osmoseur
        {
            "technician_name": "Jean Dupont",
            "debit_permeat": 15000,
            "debit_concentrat": 5000,
            "conductivite_permeat": 15.0,
            ...
        }
    """
    pass


# ============================================================================
# UPDATE SCHEMA
# ============================================================================

class OsmoseurUpdate(BaseModel):
    """
    Schema for updating an existing Osmoseur record.
    
    All fields are optional, allowing partial updates.
    Only the fields provided in the request will be updated.
    
    Example usage:
        PUT /api/osmoseur/{id}
        {
            "debit_permeat": 16000,
            "conductivite_permeat": 12.0
        }
    """
    
    technician_name: Optional[str] = Field(None, min_length=1, max_length=100)
    debit_permeat: Optional[float] = Field(None, gt=0, le=30000)
    debit_concentrat: Optional[float] = Field(None, gt=0, le=15000)
    conductivite_permeat: Optional[float] = Field(None, ge=0, le=100)
    ph_entree: Optional[float] = Field(None, ge=0, le=14)
    ph_sortie: Optional[float] = Field(None, ge=0, le=14)
    turbidite: Optional[float] = Field(None, ge=0, le=10)
    chlore_libre: Optional[float] = Field(None, ge=0, le=5)
    durete_totale: Optional[float] = Field(None, ge=0, le=50)
    tds: Optional[float] = Field(None, ge=0, le=100)


# ============================================================================
# RESPONSE SCHEMA
# ============================================================================

class OsmoseurResponse(OsmoseurBase):
    """
    Schema for Osmoseur data in API responses.
    
    Includes all fields from OsmoseurBase plus ID, timestamps,
    and the calculated taux_recuperation field.
    Used when returning data to clients.
    
    Example response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "technician_name": "Jean Dupont",
            "debit_permeat": 15000,
            "debit_concentrat": 5000,
            "taux_recuperation": 75.0,
            ...
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """
    
    taux_recuperation: float = Field(..., description="Calculated recovery rate percentage")
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

class OsmoseurListResponse(BaseModel):
    """
    Schema for paginated list of Osmoseur records.
    
    Used for GET /api/osmoseur endpoint with pagination.
    """
    
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of records per page")
    data: list[OsmoseurResponse] = Field(..., description="List of Osmoseur records")
