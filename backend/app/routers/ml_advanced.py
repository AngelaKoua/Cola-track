"""
Advanced ML Analytics Router.

Provides rich, layered analytical endpoints for the AI diagnostic dashboard.
Integrates the 5-layer AI architecture:
  Layer 1: Situation (via ml_insights.py / existing)
  Layer 2: Anomaly Detection (anomaly_engine)
  Layer 3: Root Cause (diagnostic_engine)
  Layer 4: Prognostics (prognostic_engine)
  Layer 5: Decision Support (decision_engine)
  Transversal: Explainability (explainability)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.prediction import Prediction
from app.models.incident import Incident
from app.models.osmoseur import Osmoseur
from app.models.remplisseuse import Remplisseuse

# AI Engines
from app.services.ai.anomaly_engine import AnomalyEngine
from app.services.ai.diagnostic_engine import DiagnosticEngine
from app.services.ai.prognostic_engine import PrognosticEngine
from app.services.ai.decision_engine import DecisionEngine
from app.services.ai.explainability import ExplainabilityEngine
from app.services.ai.situation_engine import SituationEngine

router = APIRouter(
    prefix="/api/ml/advanced",
    tags=["Advanced ML Analytics"]
)

# Instantiate engines (stateless singletons)
anomaly_engine = AnomalyEngine()
diagnostic_engine = DiagnosticEngine()
prognostic_engine = PrognosticEngine()
decision_engine = DecisionEngine()
explainability_engine = ExplainabilityEngine()
situation_engine = SituationEngine()


# ==============================================================================
# HELPERS
# ==============================================================================

def _get_machine_type(machine_id: str) -> str:
    return "osmoseur" if "OSM" in machine_id.upper() else "remplisseuse"

def _get_model(machine_id: str):
    return Osmoseur if "OSM" in machine_id.upper() else Remplisseuse

def _readings_to_dicts(readings, machine_type: str) -> List[Dict]:
    """Convert SQLAlchemy model instances to plain dicts for the AI engines.
    Uses getattr with defaults to safely handle missing columns."""
    result = []
    if machine_type == "osmoseur":
        for r in readings:
            result.append({
                "debit_permeat": getattr(r, 'debit_permeat', 0),
                "debit_concentrat": getattr(r, 'debit_concentrat', 0),
                "taux_recuperation": getattr(r, 'taux_recuperation', 0),
                "conductivite_permeat": getattr(r, 'conductivite_permeat', 0),
                "ph_entree": getattr(r, 'ph_entree', 0),
                "ph_sortie": getattr(r, 'ph_sortie', 0),
                "turbidite": getattr(r, 'turbidite', 0),
                "chlore_libre": getattr(r, 'chlore_libre', 0),
                "durete_totale": getattr(r, 'durete_totale', 0),
                "tds": getattr(r, 'tds', 0),
            })
    else:
        for r in readings:
            result.append({
                "vibrations": getattr(r, 'vibrations', 0),
                "volume_remplissage": getattr(r, 'volume_remplissage', 0),
                "temperature_remplissage": getattr(r, 'temperature_remplissage', 0),
                "carbonation": getattr(r, 'carbonation', 0),
                "mtbf": getattr(r, 'mtbf', 0),
                "rendement": getattr(r, 'rendement', 0),
                "conso_air_co2": getattr(r, 'conso_air_co2', 0),
            })
    return result


# ==============================================================================
# ENDPOINT 1: TIMELINE
# ==============================================================================

@router.get("/{machine_id}/timeline")
def get_machine_timeline(machine_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Chronological log of incidents and ML alerts."""
    machine_type = "Osmoseur" if "OSM" in machine_id.upper() else "Remplisseuse"
    incidents = db.query(Incident).filter(
        Incident.equipement.ilike(f"%{machine_type}%")
    ).order_by(desc(Incident.date_declaration)).limit(limit).all()
    
    alerts = db.query(Prediction).filter(
        Prediction.machine_id == machine_id,
        Prediction.alert_level > 0
    ).order_by(desc(Prediction.timestamp)).limit(limit).all()
    
    timeline = []
    for inc in incidents:
        timeline.append({
            "type": "Incident",
            "timestamp": inc.date_declaration,
            "title": f"Incident: {inc.type_incident}",
            "severity": inc.criticite,
            "description": inc.description_probleme,
            "status": inc.statut
        })
    for alt in alerts:
        severity_label = "Warning" if alt.alert_level == 1 else "Critical" if alt.alert_level == 2 else "Halt"
        timeline.append({
            "type": "Predictive Alert",
            "timestamp": alt.timestamp,
            "title": f"ML Alert Level {alt.alert_level} Detected",
            "severity": severity_label,
            "description": alt.reason or "Anomaly detected by AI",
            "status": "Logged"
        })
    
    timeline.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min, reverse=True)
    return timeline[:limit]


# ==============================================================================
# ENDPOINT 2: BASELINE COMPARISON
# ==============================================================================

@router.get("/{machine_id}/comparison")
def get_normal_comparison(machine_id: str, db: Session = Depends(get_db)):
    """Calculate delta between current readings and normal baseline."""
    machine_type = _get_machine_type(machine_id)
    model = _get_model(machine_id)
    latest = db.query(model).order_by(desc(model.created_at)).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No telemetry data found.")
    
    # Use the anomaly engine baselines for consistent comparison
    baselines_info = anomaly_engine.BASELINES.get(machine_type, {})
    
    comparison = []
    for param, info in baselines_info.items():
        value = getattr(latest, param, None)
        if value is None:
            continue
        normal_val = info["mean"]
        delta_pct = ((value - normal_val) / normal_val) * 100 if normal_val != 0 else 0.0
        comparison.append({
            "parameter": info.get("unit", "") and f"{param} ({info['unit']})" or param,
            "normal": round(normal_val, 3),
            "current": round(value, 3),
            "delta_pct": round(delta_pct, 1)
        })
    
    return comparison


# ==============================================================================
# ENDPOINT 3: SENSOR TRENDS
# ==============================================================================

@router.get("/{machine_id}/sensor-trends")
def get_sensor_trends(machine_id: str, limit: int = 36, db: Session = Depends(get_db)):
    """Time-series telemetry data for chart visualizations."""
    is_osm = "OSM" in machine_id.upper()
    model = _get_model(machine_id)
    readings = db.query(model).order_by(desc(model.created_at)).limit(limit).all()
    readings.reverse()
    
    trends = []
    if is_osm:
        for r in readings:
            trends.append({
                "timestamp": r.created_at,
                "debit": r.debit_permeat,
                "conductivite": r.conductivite_permeat,
                "tds": r.tds,
                "taux_recuperation": r.taux_recuperation
            })
    else:
        for r in readings:
            trends.append({
                "timestamp": r.created_at,
                "volume": r.volume_remplissage,
                "vibrations": r.vibrations,
                "temperature": r.temperature_remplissage,
                "carbonation": r.carbonation
            })
    return trends


# ==============================================================================
# ENDPOINT 4: FORECAST (Enhanced with Prognostic Engine)
# ==============================================================================

@router.get("/{machine_id}/forecast")
def get_forecast(machine_id: str, db: Session = Depends(get_db)):
    """Parameter-level forecasting and RUL estimation."""
    machine_type = _get_machine_type(machine_id)
    model = _get_model(machine_id)
    
    # Get telemetry history
    readings = db.query(model).order_by(desc(model.created_at)).limit(24).all()
    readings.reverse()
    history_dicts = _readings_to_dicts(readings, machine_type)
    
    # Get health history
    predictions = db.query(Prediction).filter(
        Prediction.machine_id == machine_id
    ).order_by(desc(Prediction.timestamp)).limit(24).all()
    predictions.reverse()
    health_history = [p.health_index for p in predictions]
    current_health = health_history[-1] if health_history else 80.0
    
    # Forecast parameters
    param_forecasts = prognostic_engine.forecast_parameters(history_dicts, machine_type)
    
    # RUL estimation
    rul = prognostic_engine.estimate_rul(current_health, health_history)
    
    return {
        "parameter_forecasts": param_forecasts,
        "rul": rul
    }


# ==============================================================================
# ENDPOINT 5: DIAGNOSIS (Layer 3 — Root Cause)
# ==============================================================================

@router.get("/{machine_id}/diagnosis")
def get_diagnosis(machine_id: str, db: Session = Depends(get_db)):
    """
    Pattern-based root cause analysis with confidence scores.
    Returns probable causes sorted by confidence.
    """
    machine_type = _get_machine_type(machine_id)
    model = _get_model(machine_id)
    
    # Get recent readings
    readings = db.query(model).order_by(desc(model.created_at)).limit(12).all()
    readings.reverse()
    
    if not readings:
        return {"diagnoses": [], "anomalies": {"total_anomalies": 0, "parameters": []}}
    
    history_dicts = _readings_to_dicts(readings, machine_type)
    t0_data = history_dicts[-1] if history_dicts else {}
    
    # Layer 2: Anomaly detection per parameter
    anomalies = anomaly_engine.evaluate(t0_data, machine_type)
    
    # Layer 3: Diagnostic pattern matching
    diagnoses = diagnostic_engine.evaluate(t0_data, history_dicts, machine_type)
    
    return {
        "diagnoses": diagnoses,
        "anomalies": anomalies
    }


# ==============================================================================
# ENDPOINT 6: RECOMMENDATIONS (Layer 5 — Decision Support)
# ==============================================================================

@router.get("/{machine_id}/recommendations")
def get_recommendations(machine_id: str, db: Session = Depends(get_db)):
    """
    Structured maintenance recommendation with priority, deadline, and justification.
    """
    machine_type = _get_machine_type(machine_id)
    model = _get_model(machine_id)
    
    # Get current prediction
    prediction = db.query(Prediction).filter(
        Prediction.machine_id == machine_id
    ).order_by(desc(Prediction.timestamp)).first()
    
    if not prediction:
        return {"recommendation": None}
    
    # Get history for diagnosis
    readings = db.query(model).order_by(desc(model.created_at)).limit(12).all()
    readings.reverse()
    history_dicts = _readings_to_dicts(readings, machine_type)
    t0_data = history_dicts[-1] if history_dicts else {}
    
    # Layer 2: Anomalies
    anomalies = anomaly_engine.evaluate(t0_data, machine_type)
    
    # Layer 3: Diagnosis
    diagnoses = diagnostic_engine.evaluate(t0_data, history_dicts, machine_type)
    
    # Layer 4: RUL
    predictions = db.query(Prediction).filter(
        Prediction.machine_id == machine_id
    ).order_by(desc(Prediction.timestamp)).limit(24).all()
    predictions.reverse()
    health_history = [p.health_index for p in predictions]
    rul = prognostic_engine.estimate_rul(prediction.health_index, health_history)
    
    # Layer 1: Situation
    situation = situation_engine.evaluate(
        health_index=prediction.health_index,
        failure_prob_24h=prediction.failure_probability_24h,
        is_anomaly=prediction.is_anomaly,
        quality_risk=prediction.quality_risk,
        alert_level=prediction.alert_level,
        reason=prediction.reason or "",
        health_history=health_history
    )
    
    # Layer 5: Decision
    recommendation = decision_engine.evaluate(
        health_index=prediction.health_index,
        failure_prob=prediction.failure_probability_24h,
        alert_level=prediction.alert_level,
        diagnoses=diagnoses,
        rul_hours=rul.get("hours_to_critical"),
        anomaly_count=anomalies["total_anomalies"],
        velocity_label=situation["velocity_label"]
    )
    
    return {
        "recommendation": recommendation,
        "situation": situation
    }


# ==============================================================================
# ENDPOINT 7: EXPLAINABILITY (Transversal)
# ==============================================================================

@router.get("/{machine_id}/explainability")
def get_explainability(machine_id: str, db: Session = Depends(get_db)):
    """
    Feature importance analysis for the failure prediction model.
    Returns top contributing features with human-readable labels.
    """
    import os
    import joblib
    
    machine_type = _get_machine_type(machine_id)
    model_cls = _get_model(machine_id)
    
    # Load the XGBoost failure model
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODELS_DIR = os.path.join(BASE_DIR, "ml_models")
    
    model_file = f"xgboost_failure24h_{machine_type}.joblib"
    model_path = os.path.join(MODELS_DIR, model_file)
    
    try:
        xgb_model = joblib.load(model_path)
    except Exception:
        return {"feature_importance": [], "explanation": {"explanation": "Model not available."}}
    
    # Feature names (must match train_models.py order)
    if machine_type == "osmoseur":
        feature_names = [
            "pression_membranaire", "debit_permeat", "conductivite_permeat",
            "temperature_eau", "turbidite", "ph_entree", "ph_sortie",
            "vibrations_pompe", "pression_rate", "conductivite_rate",
            "pression_membranaire_rolling_1h", "debit_permeat_rolling_1h",
            "conductivite_permeat_rolling_1h", "vibrations_pompe_rolling_1h"
        ]
    else:
        feature_names = [
            "vibrations", "mtbf", "pression_co2", "temperature_remplissage",
            "volume_remplissage", "vitesse_ligne", "vibrations_rate", "mtbf_rate",
            "vibrations_rolling_1h", "mtbf_rolling_1h",
            "pression_co2_rolling_1h", "volume_remplissage_rolling_1h"
        ]
    
    # Get feature importance
    importance = explainability_engine.get_feature_importance(
        xgb_model, feature_names, machine_type, top_n=10
    )
    
    # Get anomalies for contextual explanation
    readings = db.query(model_cls).order_by(desc(model_cls.created_at)).limit(12).all()
    readings.reverse()
    history_dicts = _readings_to_dicts(readings, machine_type)
    t0_data = history_dicts[-1] if history_dicts else {}
    
    anomalies = anomaly_engine.evaluate(t0_data, machine_type)
    diagnoses = diagnostic_engine.evaluate(t0_data, history_dicts, machine_type)
    
    context = explainability_engine.explain_prediction_context(
        importance, anomalies["parameters"], diagnoses
    )
    
    return {
        "feature_importance": importance,
        "explanation": context
    }
