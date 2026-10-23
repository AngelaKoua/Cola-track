"""
Models package initialization.

This module exports all database models for easy importing.
"""

from app.models.osmoseur import Osmoseur
from app.models.remplisseuse import Remplisseuse
from app.models.user import User
from app.models.notification import Notification
from app.models.prediction import Prediction
from app.models.incident import Incident
from app.models.iot_osmoseur_reading import IoTOsmoseurReading

__all__ = ["Osmoseur", "Remplisseuse", "User", "Notification", "Prediction", "Incident", "IoTOsmoseurReading"]
