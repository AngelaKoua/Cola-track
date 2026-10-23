"""
Pydantic schemas for IoT Osmoseur sensor readings.

Used for request validation (ESP32 payload) and response serialization.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class IoTOsmoseurCreate(BaseModel):
    """Schema for creating a new IoT osmoseur reading (ESP32 POST payload)."""

    device_id: str = Field(..., max_length=50, description="ESP32 device identifier")
    debit_in: int = Field(..., description="Input flow rate (pulse count)")
    turb_in: float = Field(..., description="Input turbidity (voltage)")
    ph: float = Field(..., description="pH level (0-14)")
    tds: float = Field(..., description="Total Dissolved Solids in ppm")
    debit_out: int = Field(..., description="Output flow rate (pulse count)")
    turb_out: float = Field(..., description="Output turbidity (voltage)")


class IoTOsmoseurResponse(BaseModel):
    """Schema for returning an IoT osmoseur reading."""

    id: UUID
    device_id: str
    debit_in: int | None
    turb_in: float | None
    ph: float | None
    tds: float | None
    debit_out: int | None
    turb_out: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class IoTOsmoseurStatusResponse(BaseModel):
    """Schema for device connectivity status."""

    status: str = Field(..., description="CONNECTED or DISCONNECTED")
    last_seen: datetime | None = Field(None, description="Timestamp of last reading")
