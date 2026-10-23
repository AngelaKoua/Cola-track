"""
Schemas package initialization.

This module exports all Pydantic schemas for easy importing.
"""

from app.schemas.osmoseur import (
    OsmoseurBase,
    OsmoseurCreate,
    OsmoseurUpdate,
    OsmoseurResponse,
    OsmoseurListResponse
)

from app.schemas.remplisseuse import (
    RemplisseuseBase,
    RemplisseuseCreate,
    RemplisseuseUpdate,
    RemplisseuseResponse,
    RemplisseuseListResponse
)

from app.schemas.iot_osmoseur import (
    IoTOsmoseurCreate,
    IoTOsmoseurResponse,
    IoTOsmoseurStatusResponse,
)

__all__ = [
    # Osmoseur schemas
    "OsmoseurBase",
    "OsmoseurCreate",
    "OsmoseurUpdate",
    "OsmoseurResponse",
    "OsmoseurListResponse",
    # Remplisseuse schemas
    "RemplisseuseBase",
    "RemplisseuseCreate",
    "RemplisseuseUpdate",
    "RemplisseuseResponse",
    "RemplisseuseListResponse",
    # IoT Osmoseur schemas
    "IoTOsmoseurCreate",
    "IoTOsmoseurResponse",
    "IoTOsmoseurStatusResponse",
]
