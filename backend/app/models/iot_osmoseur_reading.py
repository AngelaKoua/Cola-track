"""
SQLAlchemy ORM model for IoT Osmoseur sensor readings.

This model represents the 'iot_osmoseur_readings' table in the 'iot' schema.
It stores real-time sensor data sent by the ESP32 prototype every second.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class IoTOsmoseurReading(Base):
    """
    IoT Osmoseur sensor reading model.

    Stores real-time data from the ESP32 prototype monitoring the reverse
    osmosis system. Data is received via HTTP POST every second.

    Table: iot.iot_osmoseur_readings
    """

    __tablename__ = "iot_osmoseur_readings"
    __table_args__ = {"schema": "iot"}

    # ============================================================================
    # PRIMARY KEY
    # ============================================================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ============================================================================
    # DEVICE IDENTIFICATION
    # ============================================================================
    device_id = Column(String(50), nullable=False, index=True)
    """Unique identifier of the ESP32 device (e.g. 'osmoseur_esp32_01')."""

    # ============================================================================
    # SENSOR DATA – INPUT SIDE
    # ============================================================================
    debit_in = Column(Integer, nullable=True)
    """Input flow rate (pulse count per second)."""

    turb_in = Column(Float, nullable=True)
    """Input turbidity (voltage reading converted from analog)."""

    # ============================================================================
    # WATER QUALITY PARAMETERS
    # ============================================================================
    ph = Column(Float, nullable=True)
    """pH level of the water (0-14 scale)."""

    tds = Column(Float, nullable=True)
    """Total Dissolved Solids in ppm."""

    # ============================================================================
    # SENSOR DATA – OUTPUT SIDE
    # ============================================================================
    debit_out = Column(Integer, nullable=True)
    """Output flow rate (pulse count per second)."""

    turb_out = Column(Float, nullable=True)
    """Output turbidity (voltage reading converted from analog)."""

    # ============================================================================
    # TIMESTAMP
    # ============================================================================
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
    """Timestamp when this reading was recorded."""

    def __repr__(self) -> str:
        return (
            f"<IoTOsmoseurReading("
            f"id={self.id}, "
            f"device_id={self.device_id}, "
            f"created_at={self.created_at}"
            f")>"
        )
