import os
import joblib
import json
import logging
from typing import Dict, Any, Optional

from app.services.feature_service import FeatureService

logger = logging.getLogger(__name__)

# Resolve the absolute path of the backend so joblib always finds models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "ml_models")

class MLService:
    """
    Core Machine Learning Service.
    Wraps the models and hybrid decision engine, receiving processed feature 
    vectors from the FeatureService.
    """
    def __init__(self, feature_service: FeatureService):
        self.feature_service = feature_service
        self.models = {}
        self.scalers = {}
        self._load_models()

    def _load_models(self):
        """Loads models in memory."""
        try:
            self.scalers['iso_osm'] = joblib.load(os.path.join(MODELS_DIR, "iso_forest_scaler_osmoseur.joblib"))
            self.scalers['iso_rmp'] = joblib.load(os.path.join(MODELS_DIR, "iso_forest_scaler_remplisseuse.joblib"))
            
            self.models['iso_osm'] = joblib.load(os.path.join(MODELS_DIR, "iso_forest_osmoseur.joblib"))
            self.models['iso_rmp'] = joblib.load(os.path.join(MODELS_DIR, "iso_forest_remplisseuse.joblib"))
            
            self.models['xgb_osm'] = joblib.load(os.path.join(MODELS_DIR, "xgboost_failure24h_osmoseur.joblib"))
            self.models['xgb_rmp'] = joblib.load(os.path.join(MODELS_DIR, "xgboost_failure24h_remplisseuse.joblib"))
            
            self.models['rf_qual_rmp'] = joblib.load(os.path.join(MODELS_DIR, "rf_quality_model.joblib"))
            
            self.models['gbr_osm'] = joblib.load(os.path.join(MODELS_DIR, "gbr_health_osmoseur.joblib"))
            self.models['gbr_rmp'] = joblib.load(os.path.join(MODELS_DIR, "gbr_health_remplisseuse.joblib"))
            logger.info("MLService: All models loaded successfully from disk.")
        except Exception as e:
            logger.error(f"Failed to load ML models from {MODELS_DIR}: {e}")

    def evaluate_osmoseur(self, machine_id: str) -> Optional[Dict[str, Any]]:
        # 1. Feature Engineering
        feature_vector, t0_data = self.feature_service.build_feature_vector_osmoseur(machine_id)
        if feature_vector is None or t0_data is None:
            return None
            
        # 2. ML Inference
        scaled_features = self.scalers['iso_osm'].transform(feature_vector)
        anomaly = self.models['iso_osm'].predict(scaled_features)[0] == -1
        
        # XGBoost expects specific feature names sometimes, but predict(np.array) works
        import xgboost as xgb
        # Provide it as numpy array if required or direct 2d array
        failure_prob = float(self.models['xgb_osm'].predict_proba(feature_vector)[0][1])
        health_index = float(self.models['gbr_osm'].predict(feature_vector)[0])
        
        # 3. Hybrid Rules
        pression = t0_data.get('pression_membranaire', 0)
        conductivite = t0_data.get('conductivite_permeat', 0)
        
        decision = "NORMAL"
        alert_level = 0
        reasons = []

        if pression > 15.5 or conductivite > 45.0:
            decision = "Arrêt Critique (Seuils physiques dépassés)"
            alert_level = 3
            reasons.append("Pression > 15.5 ou Conductivité > 45")
        elif failure_prob > 0.8 and anomaly:
            decision = "Maintenance Urgente (< 24h)"
            alert_level = 2
            reasons.append(f"Probabilité de panne: {failure_prob:.1%}")
        elif health_index < 75.0 and failure_prob > 0.4:
            decision = "Inspection recommandée (Dégradation détectée)"
            alert_level = 1
            reasons.append(f"Health Index bas ({health_index:.1f})")

        return {
            "machine_id": machine_id,
            "decision": decision,
            "alert_level": alert_level,
            "reason": " | ".join(reasons) if reasons else "Opérations nominales",
            "health_index": round(health_index, 2),
            "failure_probability_24h": round(failure_prob, 3),
            "quality_risk": None,
            "is_anomaly": bool(anomaly)
        }

    def evaluate_remplisseuse(self, machine_id: str) -> Optional[Dict[str, Any]]:
        # 1. Feature Engineering
        feature_vector, t0_data = self.feature_service.build_feature_vector_remplisseuse(machine_id)
        if feature_vector is None or t0_data is None:
            return None

        # 2. ML Inference
        scaled_features = self.scalers['iso_rmp'].transform(feature_vector)
        anomaly = self.models['iso_rmp'].predict(scaled_features)[0] == -1
        
        failure_prob = float(self.models['xgb_rmp'].predict_proba(feature_vector)[0][1])
        quality_risk_prob = float(self.models['rf_qual_rmp'].predict_proba(feature_vector)[0][1])
        health_index = float(self.models['gbr_rmp'].predict(feature_vector)[0])
        
        # 3. Hybrid Rules
        vibrations = t0_data.get('vibrations', 0)
        volume = t0_data.get('volume_remplissage', 0.5)
        
        decision = "NORMAL"
        alert_level = 0
        reasons = []

        if volume > 0.515 or volume < 0.485:
            decision = "Arrêt Critique (Non-conformité produit)"
            alert_level = 3
            reasons.append(f"Volume hors spec ({volume:.3f} L)")
        elif vibrations > 4.5 and failure_prob > 0.85:
            decision = "Arrêt Critique (Panne Moteur Imminente)"
            alert_level = 3
            reasons.append(f"Vibrations critiques ({vibrations:.1f} mm/s) + proba panne {failure_prob:.1%}")
        elif quality_risk_prob > 0.7:
            decision = "Alerte Qualité (Ajuster paramètres)"
            alert_level = 2
            reasons.append(f"Risque Qualité élevé ({quality_risk_prob:.1%})")
        elif health_index < 70.0 and anomaly:
            decision = "Inspection recommandée (Dégradation globale)"
            alert_level = 1
            reasons.append(f"Anomalie détectée et Health Index bas ({health_index:.1f})")

        return {
            "machine_id": machine_id,
            "decision": decision,
            "alert_level": alert_level,
            "reason": " | ".join(reasons) if reasons else "Opérations nominales",
            "health_index": round(health_index, 2),
            "failure_probability_24h": round(failure_prob, 3),
            "quality_risk": round(quality_risk_prob, 3),
            "is_anomaly": bool(anomaly)
        }

    def process_machine(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """Main entry point."""
        if "OSM" in machine_id.upper() or "OSMOSEUR" in machine_id.upper():
            return self.evaluate_osmoseur(machine_id)
        elif "RMP" in machine_id.upper() or "REMPLISSEUSE" in machine_id.upper():
            return self.evaluate_remplisseuse(machine_id)
        return None
