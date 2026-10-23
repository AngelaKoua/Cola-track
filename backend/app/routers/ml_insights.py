from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any

from app.database import get_db
from app.models.prediction import Prediction

router = APIRouter(
    prefix="/api/ml",
    tags=["Machine Learning Insights"]
)

@router.get("/predictions/latest/{machine_id}")
def get_latest_prediction(machine_id: str, db: Session = Depends(get_db)):
    """
    Get the most recent instantaneous inference for a machine.
    This is extremely fast O(1) as it just reads the background job result from DB.
    """
    prediction = db.query(Prediction).filter(
        Prediction.machine_id == machine_id
    ).order_by(desc(Prediction.timestamp)).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="No ML predictions found for this machine. Background job might still be running or telemetry is missing.")
        
    return {
        "id": prediction.id,
        "timestamp": prediction.timestamp,
        "machine_id": prediction.machine_id,
        "health_index": prediction.health_index,
        "failure_probability_24h": prediction.failure_probability_24h,
        "quality_risk": prediction.quality_risk,
        "is_anomaly": prediction.is_anomaly,
        "alert_level": prediction.alert_level,
        "reason": prediction.reason
    }

@router.get("/analytics/rul/{machine_id}")
def get_historical_rul(machine_id: str, limit: int = 24, db: Session = Depends(get_db)):
    """
    Get the historical trajectory of the Health Index (RUL Proxy) for a machine.
    Useful for line charts in the dashboard.
    """
    predictions = db.query(Prediction).filter(
        Prediction.machine_id == machine_id
    ).order_by(desc(Prediction.timestamp)).limit(limit).all()
    
    # Reverse to return chronologically
    predictions.reverse()
    
    return [
        {
            "timestamp": p.timestamp,
            "health_index": p.health_index,
            "failure_probability": p.failure_probability_24h,
            "alert_level": p.alert_level
        }
        for p in predictions
    ]
