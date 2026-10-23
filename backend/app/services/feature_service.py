import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Any, Tuple, Optional

from app.repositories.telemetry_repository import TelemetryRepository
from app.services.cache_service import telemetry_cache

logger = logging.getLogger(__name__)

class FeatureService:
    """
    Feature Engineering Service.
    Separates the mathematical transformations (rolling windows, rates) 
    from ML inference and Database fetching.
    """
    def __init__(self, repository: TelemetryRepository):
        self.repository = repository

    def _get_history(self, machine_id: str) -> List[Any]:
        """Fetch history from Cache, fallback to DB using Repository."""
        cache_key = f"telemetry_hist_{machine_id}"
        cached_data = telemetry_cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
            
        logger.debug(f"Cache miss for {machine_id}. Fetching from DB.")
        history = self.repository.get_last_n_readings(machine_id, limit=12) # 1 hour of 5-min intervals
        
        # Sort chronologically (oldest to newest) since DB returns DESC
        history = sorted(history, key=lambda x: x.created_at)
        
        telemetry_cache.set(cache_key, history)
        return history

    def build_feature_vector_osmoseur(self, machine_id: str) -> Tuple[Optional[np.ndarray], Optional[Dict]]:
        """
        Builds the exact feature vector expected by the Osmoseur ML Models.
        Returns: (feature_vector_2d_array, raw_t0_dict)
        """
        history = self._get_history(machine_id)
        if not history or len(history) < 2:
            logger.warning("Not enough history to compute features.")
            return None, None

        # Convert to DataFrame for easy rolling/diff calculations
        data = [{
            "pression_membranaire": r.pression_membranaire,
            "debit_permeat": r.debit_permeat,
            "conductivite_permeat": r.conductivite_permeat,
            "temperature_eau": r.temperature_eau,
            "turbidite": r.turbidite,
            "ph_entree": r.ph_entree,
            "ph_sortie": r.ph_sortie,
            "vibrations_pompe": r.vibrations_pompe,
            "chlore_libre": r.chlore_libre,
            "tds": r.tds,
            "debit_concentrat": r.debit_concentrat,
            "taux_recuperation": r.taux_recuperation
        } for r in history]
        
        df = pd.DataFrame(data)
        
        # Current instant T0 is the last row
        t0_data = df.iloc[-1].to_dict()

        # Feature Engineering: Rates
        df['pression_rate'] = df['pression_membranaire'].diff()
        df['conductivite_rate'] = df['conductivite_permeat'].diff()
        
        # Feature Engineering: Rolling Means
        for col in ['pression_membranaire', 'debit_permeat', 'conductivite_permeat', 'vibrations_pompe']:
            df[f'{col}_rolling_1h'] = df[col].rolling(window=12, min_periods=1).mean()
            
        # Get the final row containing T0 + all calculated rates and rollings
        final_row = df.iloc[-1]
        
        # Construct exact array for ML:
        # Expected order (from train_models.py X_osm):
        # ['pression_membranaire', 'debit_permeat', 'conductivite_permeat', 'temperature_eau', 
        #  'turbidite', 'ph_entree', 'ph_sortie', 'vibrations_pompe', 'pression_rate', 
        #  'conductivite_rate', 'pression_membranaire_rolling_1h', 'debit_permeat_rolling_1h', 
        #  'conductivite_permeat_rolling_1h', 'vibrations_pompe_rolling_1h']
        
        features = [
            final_row['pression_membranaire'],
            final_row['debit_permeat'],
            final_row['conductivite_permeat'],
            final_row['temperature_eau'],
            final_row['turbidite'],
            final_row['ph_entree'],
            final_row['ph_sortie'],
            final_row['vibrations_pompe'],
            final_row['pression_rate'],
            final_row['conductivite_rate'],
            final_row['pression_membranaire_rolling_1h'],
            final_row['debit_permeat_rolling_1h'],
            final_row['conductivite_permeat_rolling_1h'],
            final_row['vibrations_pompe_rolling_1h']
        ]
        
        # Handle NaN from rolling/diff if not enough data
        features = [0.0 if pd.isna(x) else x for x in features]
        
        return np.array(features).reshape(1, -1), t0_data

    def build_feature_vector_remplisseuse(self, machine_id: str) -> Tuple[Optional[np.ndarray], Optional[Dict]]:
        """
        Builds the exact feature vector expected by the Remplisseuse ML Models.
        Returns: (feature_vector_2d_array, raw_t0_dict)
        """
        history = self._get_history(machine_id)
        if not history or len(history) < 2:
            return None, None

        data = [{
            "vibrations": r.vibrations,
            "mtbf": r.mtbf,
            "pression_co2": r.pression_co2,
            "temperature_remplissage": r.temperature_remplissage,
            "volume_remplissage": r.volume_remplissage,
            "vitesse_ligne": r.vitesse_ligne,
            "conso_air_co2": r.conso_air_co2,
            "carbonation": r.carbonation
        } for r in history]
        
        df = pd.DataFrame(data)
        t0_data = df.iloc[-1].to_dict()

        # Rates
        df['vibrations_rate'] = df['vibrations'].diff()
        df['mtbf_rate'] = df['mtbf'].diff()
        
        # Rolling Means
        for col in ['vibrations', 'mtbf', 'pression_co2', 'volume_remplissage']:
            df[f'{col}_rolling_1h'] = df[col].rolling(window=12, min_periods=1).mean()
            
        final_row = df.iloc[-1]
        
        # Expected order (from X_rmp):
        # ['vibrations', 'mtbf', 'pression_co2', 'temperature_remplissage', 'volume_remplissage', 
        #  'vitesse_ligne', 'vibrations_rate', 'mtbf_rate', 'vibrations_rolling_1h', 
        #  'mtbf_rolling_1h', 'pression_co2_rolling_1h', 'volume_remplissage_rolling_1h']
        
        features = [
            final_row['vibrations'],
            final_row['mtbf'],
            final_row['pression_co2'],
            final_row['temperature_remplissage'],
            final_row['volume_remplissage'],
            final_row['vitesse_ligne'],
            final_row['vibrations_rate'],
            final_row['mtbf_rate'],
            final_row['vibrations_rolling_1h'],
            final_row['mtbf_rolling_1h'],
            final_row['pression_co2_rolling_1h'],
            final_row['volume_remplissage_rolling_1h']
        ]
        
        features = [0.0 if pd.isna(x) else x for x in features]
        return np.array(features).reshape(1, -1), t0_data

    def build_feature_vector(self, machine_id: str) -> Tuple[Optional[np.ndarray], Optional[Dict]]:
        """Main router to build vectors based on machine type."""
        if "OSM" in machine_id.upper() or "OSMOSEUR" in machine_id.upper():
            return self.build_feature_vector_osmoseur(machine_id)
        elif "RMP" in machine_id.upper() or "REMPLISSEUSE" in machine_id.upper():
            return self.build_feature_vector_remplisseuse(machine_id)
        return None, None
