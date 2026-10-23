import os
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODELS_DIR = os.path.join(BASE_DIR, "..", "backend", "app", "ml_models")

class ColatrackHybridEngine:
    """
    Hybrid Decision Engine for Colatrack Industrial AI.
    Combines Machine Learning model predictions with hard industrial business rules.
    """
    
    def __init__(self, models_dir=DEFAULT_MODELS_DIR):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.load_models()
        
        # Define expected features
        self.features_osm = [
            'debit_permeat_lh', 'debit_concentrat_lh', 'conductivite_permeat_uscm', 
            'ph_entree', 'ph_sortie', 'turbidite_ntu', 'chlore_libre_mgl', 
            'durete_totale_f', 'tds_ppm', 'pression_membrane_bar', 'temperature_eau_c',
            'pression_rate', 'conductivite_rate'
        ] + [f'{c}_rolling_1h' for c in ['debit_permeat_lh', 'debit_concentrat_lh', 'conductivite_permeat_uscm', 'ph_entree', 'ph_sortie', 'turbidite_ntu', 'chlore_libre_mgl', 'durete_totale_f', 'tds_ppm', 'pression_membrane_bar', 'temperature_eau_c', 'pression_rate', 'conductivite_rate']]

        self.features_rmp = [
            'temperature_remplissage_c', 'volume_remplissage_l', 'carbonation_co_gl', 
            'unites_produites', 'heures_arret_h', 'mtbf_h', 'conso_air_co_m3h', 'vibrations_moteur_mms',
            'vibrations_rate', 'mtbf_rate'
        ] + [f'{c}_rolling_1h' for c in ['temperature_remplissage_c', 'volume_remplissage_l', 'carbonation_co_gl', 'unites_produites', 'heures_arret_h', 'mtbf_h', 'conso_air_co_m3h', 'vibrations_moteur_mms', 'vibrations_rate', 'mtbf_rate']]

    def load_models(self):
        """Load all pre-trained models from the models directory."""
        try:
            # Scalers
            self.scalers['iso_osm'] = joblib.load(f"{self.models_dir}/iso_forest_scaler_osmoseur.joblib")
            self.scalers['iso_rmp'] = joblib.load(f"{self.models_dir}/iso_forest_scaler_remplisseuse.joblib")
            
            # Anomaly Detection (Isolation Forest)
            self.models['iso_osm'] = joblib.load(f"{self.models_dir}/iso_forest_osmoseur.joblib")
            self.models['iso_rmp'] = joblib.load(f"{self.models_dir}/iso_forest_remplisseuse.joblib")
            
            # Failure Prediction (XGBoost)
            self.models['xgb_osm'] = joblib.load(f"{self.models_dir}/xgboost_failure24h_osmoseur.joblib")
            self.models['xgb_rmp'] = joblib.load(f"{self.models_dir}/xgboost_failure24h_remplisseuse.joblib")
            
            # Quality Risk (Random Forest)
            self.models['rf_qual_rmp'] = joblib.load(f"{self.models_dir}/rf_quality_model.joblib")
            
            # Remaining Useful Life Proxy (Gradient Boosting)
            self.models['gbr_osm'] = joblib.load(f"{self.models_dir}/gbr_health_osmoseur.joblib")
            self.models['gbr_rmp'] = joblib.load(f"{self.models_dir}/gbr_health_remplisseuse.joblib")
            print("Colatrack Hybrid Engine: Models loaded successfully.")
        except Exception as e:
            print(f"Error loading models: {e}. Please ensure train_models.py has been run.")

    def evaluate_osmoseur(self, data_dict):
        """
        Evaluate real-time Osmoseur data.
        Returns a decision dictionary.
        """
        df = pd.DataFrame([data_dict])
        
        # ML Inference
        features = df[self.features_osm]
        scaled_features = self.scalers['iso_osm'].transform(features)
        
        anomaly = self.models['iso_osm'].predict(scaled_features)[0] == -1
        failure_prob = float(self.models['xgb_osm'].predict_proba(features)[0][1])
        health_index = float(self.models['gbr_osm'].predict(features)[0])
        
        # Business Rules (Hybrid Logic)
        pression = data_dict['pression_membrane_bar']
        conductivite = data_dict['conductivite_permeat_uscm']
        
        decision = "NORMAL"
        alert_level = 0
        reasons = []

        # Rule 1: Hard physical threshold
        if pression > 15.5 or conductivite > 45.0:
            decision = "Arrêt Critique (Seuils physiques dépassés)"
            alert_level = 3
            reasons.append("Pression > 15.5 ou Conductivité > 45")
            
        # Rule 2: ML + Soft physical threshold
        elif failure_prob > 0.8 and anomaly:
            decision = "Maintenance Urgente (< 24h)"
            alert_level = 2
            reasons.append(f"Probabilité de panne critique: {failure_prob:.1%}")

        # Rule 3: Predictive ML early warning
        elif health_index < 75.0 and failure_prob > 0.4:
            decision = "Inspection recommandée (Dégradation détectée)"
            alert_level = 1
            reasons.append(f"Health Index bas ({health_index:.1f}) avec risque de panne modéré")

        return {
            "machine": "OSM-001",
            "decision": decision,
            "alert_level": alert_level,
            "reasons": reasons,
            "metrics": {
                "health_index": round(health_index, 2),
                "failure_probability_24h": round(failure_prob, 3),
                "is_anomaly": bool(anomaly)
            }
        }

    def evaluate_remplisseuse(self, data_dict):
        """
        Evaluate real-time Remplisseuse data.
        Returns a decision dictionary.
        """
        df = pd.DataFrame([data_dict])
        
        # ML Inference
        features = df[self.features_rmp]
        scaled_features = self.scalers['iso_rmp'].transform(features)
        
        anomaly = self.models['iso_rmp'].predict(scaled_features)[0] == -1
        failure_prob = float(self.models['xgb_rmp'].predict_proba(features)[0][1])
        quality_risk_prob = float(self.models['rf_qual_rmp'].predict_proba(features)[0][1])
        health_index = float(self.models['gbr_rmp'].predict(features)[0])
        
        # Business Rules (Hybrid Logic)
        vibrations = data_dict['vibrations_moteur_mms']
        volume = data_dict['volume_remplissage_l']
        
        decision = "NORMAL"
        alert_level = 0
        reasons = []

        # Rule 1: Quality failure + Vibration spike
        if volume > 0.515 or volume < 0.485:
            decision = "Arrêt Critique (Non-conformité produit)"
            alert_level = 3
            reasons.append(f"Volume hors spec ({volume:.3f} L)")
            
        elif vibrations > 4.5 and failure_prob > 0.85:
            decision = "Arrêt Critique (Panne Moteur Imminente)"
            alert_level = 3
            reasons.append(f"Vibrations critiques ({vibrations:.1f} mm/s) + proba panne {failure_prob:.1%}")

        # Rule 2: High quality rejection probability
        elif quality_risk_prob > 0.7:
            decision = "Alerte Qualité (Ajuster paramètres)"
            alert_level = 2
            reasons.append(f"Risque Qualité élevé ({quality_risk_prob:.1%})")

        # Rule 3: General predictive wear
        elif health_index < 70.0 and anomaly:
            decision = "Inspection recommandée (Dégradation globale)"
            alert_level = 1
            reasons.append(f"Anomalie détectée et Health Index bas ({health_index:.1f})")

        return {
            "machine": "RMP-001",
            "decision": decision,
            "alert_level": alert_level,
            "reasons": reasons,
            "metrics": {
                "health_index": round(health_index, 2),
                "failure_probability_24h": round(failure_prob, 3),
                "quality_risk_probability": round(quality_risk_prob, 3),
                "is_anomaly": bool(anomaly)
            }
        }

if __name__ == "__main__":
    import json
    print("Testing Colatrack Hybrid Engine...")
    engine = ColatrackHybridEngine()
    
    # Test with a single row from the generated dataset to verify it works
    print("\nExtracting test samples from dataset...")
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "industrial_iot_timeseries.csv"), nrows=1000)
    
    # Needs to match engineered features - normally the real-time pipeline does this
    # For testing, we just simulate the rolling/rate features for one row
    
    # Simple simulated normal test row for Osmoseur
    osm_test = {
        'debit_permeat_lh': 1050, 'debit_concentrat_lh': 350, 'conductivite_permeat_uscm': 25, 
        'ph_entree': 7.0, 'ph_sortie': 7.0, 'turbidite_ntu': 0.1, 'chlore_libre_mgl': 0.1, 
        'durete_totale_f': 12, 'tds_ppm': 250, 'pression_membrane_bar': 12, 'temperature_eau_c': 18,
        'pression_rate': 0.01, 'conductivite_rate': -0.05
    }
    # Add rolling duplicates for testing structure
    for c in list(osm_test.keys()):
        osm_test[f'{c}_rolling_1h'] = osm_test[c]
        
    # Simulated critical test row for Remplisseuse
    rmp_test = {
        'temperature_remplissage_c': 5, 'volume_remplissage_l': 0.505, 'carbonation_co_gl': 6.5, 
        'unites_produites': 85, 'heures_arret_h': 0, 'mtbf_h': 85, 'conso_air_co_m3h': 90, 
        'vibrations_moteur_mms': 4.7, # High vibration
        'vibrations_rate': 0.5, 'mtbf_rate': -1.2
    }
    for c in list(rmp_test.keys()):
        rmp_test[f'{c}_rolling_1h'] = rmp_test[c]

    print("\n---> Result for Normal Osmoseur State:")
    print(json.dumps(engine.evaluate_osmoseur(osm_test), indent=2))
    
    print("\n---> Result for Critical Remplisseuse State:")
    print(json.dumps(engine.evaluate_remplisseuse(rmp_test), indent=2))
