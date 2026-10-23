"""
Routers package initialization.

This module exports all API routers for registration in the main app.
"""

from app.routers.osmoseur import router as osmoseur_router
from app.routers.remplisseuse import router as remplisseuse_router
from app.routers.iot_osmoseur import router as iot_osmoseur_router

__all__ = [
    "osmoseur_router",
    "remplisseuse_router",
    "iot_osmoseur_router",
]
