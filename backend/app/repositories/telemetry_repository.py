from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Type, Dict, Any
import logging

from app.models.osmoseur import Osmoseur
from app.models.remplisseuse import Remplisseuse

logger = logging.getLogger(__name__)

class TelemetryRepository:
    """
    Data Access Layer for Telemetry.
    Isolates SQL logic from ML feature engineering.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_last_n_readings_osmoseur(self, limit: int = 12) -> List[Osmoseur]:
        """Fetch the last N readings for Osmoseur (default 12 = 1 hour)."""
        return self.db.query(Osmoseur).order_by(desc(Osmoseur.created_at)).limit(limit).all()

    def get_last_n_readings_remplisseuse(self, limit: int = 12) -> List[Remplisseuse]:
        """Fetch the last N readings for Remplisseuse (default 12 = 1 hour)."""
        return self.db.query(Remplisseuse).order_by(desc(Remplisseuse.created_at)).limit(limit).all()

    def get_last_n_readings(self, machine_id: str, limit: int = 12) -> List[Any]:
        """
        Generic fetcher routing to the correct model based on machine_id.
        In a real app, logic might be more complex if machine_id is dynamic,
        but here we assume 'OSM-001' maps to Osmoseur and 'RMP-001' to Remplisseuse.
        """
        if "OSM" in machine_id.upper() or "OSMOSEUR" in machine_id.upper():
            return self.get_last_n_readings_osmoseur(limit)
        elif "RMP" in machine_id.upper() or "REMPLISSEUSE" in machine_id.upper():
            return self.get_last_n_readings_remplisseuse(limit)
        else:
            logger.error(f"Unknown machine_id pattern: {machine_id}")
            return []
