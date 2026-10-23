"""
Pydantic schemas for technician-related API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


class TechnicianSummaryStats(BaseModel):
    """Summary statistics for all technicians."""
    total: int
    active: int
    inactive: int
    total_entries: int
    period_days: int


class TechnicianListItem(BaseModel):
    """Technician data for list view."""
    id: int
    username: str
    is_active: bool
    created_at: Optional[str]
    total_entries: int
    last_entry: Optional[str]
    equipment_type: str
    osmo_entries: int
    remp_entries: int


class EntriesByDay(BaseModel):
    """Entry count for a specific day."""
    date: str
    count: int


class TechnicianDetail(BaseModel):
    """Detailed technician data with analytics."""
    id: int
    username: str
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    last_activity: Optional[str]
    entries_by_day: List[EntriesByDay]
    entries_by_equipment: Dict[str, int]
    entries_by_hour: List[int]


class TechnicianCreate(BaseModel):
    """Schema for creating a new technician."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="Technician's email address for sending credentials")


class TechnicianUpdate(BaseModel):
    """Schema for updating a technician."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class TechnicianStatusUpdate(BaseModel):
    """Schema for updating technician status."""
    is_active: bool


class TechnicianResponse(BaseModel):
    """Response schema for technician operations."""
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    role: str
    created_at: Optional[str]
    email_sent: Optional[bool] = None
    
    class Config:
        from_attributes = True
