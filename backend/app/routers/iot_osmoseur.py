"""
FastAPI router for IoT Osmoseur endpoints.

Handles data ingestion from the ESP32 prototype and exposes
endpoints for the frontend dashboard (latest values, timeseries, status).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.iot_osmoseur_reading import IoTOsmoseurReading
from app.schemas.iot_osmoseur import (
    IoTOsmoseurCreate,
    IoTOsmoseurResponse,
    IoTOsmoseurStatusResponse,
)

router = APIRouter(
    prefix="/iot/osmoseur",
    tags=["IoT Osmoseur"],
)


# ============================================================================
# POST – Receive data from ESP32
# ============================================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Receive IoT sensor reading",
    description="Receives a JSON payload from the ESP32 and stores it in the database.",
)
def create_reading(
    payload: IoTOsmoseurCreate,
    db: Session = Depends(get_db),
):
    """Ingest a sensor reading from the ESP32 prototype."""
    try:
        reading = IoTOsmoseurReading(
            device_id=payload.device_id,
            debit_in=payload.debit_in,
            turb_in=payload.turb_in,
            ph=payload.ph,
            tds=payload.tds,
            debit_out=payload.debit_out,
            turb_out=payload.turb_out,
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)

        return {"message": "Reading saved", "id": str(reading.id)}

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save reading: {str(exc)}",
        )


# ============================================================================
# GET – Latest reading
# ============================================================================

@router.get(
    "/latest",
    response_model=IoTOsmoseurResponse,
    summary="Get latest IoT reading",
    description="Returns the most recent sensor reading ordered by created_at DESC.",
)
def get_latest_reading(db: Session = Depends(get_db)):
    """Return the most recent IoT osmoseur sensor reading."""
    reading = (
        db.query(IoTOsmoseurReading)
        .order_by(IoTOsmoseurReading.created_at.desc())
        .first()
    )

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No IoT readings found",
        )

    return reading


# ============================================================================
# GET – Timeseries (last X minutes)
# ============================================================================

@router.get(
    "/timeseries",
    response_model=list[IoTOsmoseurResponse],
    summary="Get timeseries data",
    description="Returns all readings from the last X minutes, sorted ASC. Used for charting.",
)
def get_timeseries(
    minutes: int = Query(default=5, ge=1, le=60, description="Number of minutes to look back"),
    db: Session = Depends(get_db),
):
    """Return IoT readings from the last N minutes for chart display."""
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)

    readings = (
        db.query(IoTOsmoseurReading)
        .filter(IoTOsmoseurReading.created_at >= cutoff)
        .order_by(IoTOsmoseurReading.created_at.asc())
        .all()
    )

    return readings


# ============================================================================
# GET – Device connectivity status
# ============================================================================

@router.get(
    "/status",
    response_model=IoTOsmoseurStatusResponse,
    summary="Get device connection status",
    description="Returns CONNECTED if the latest reading is less than 5 seconds old, else DISCONNECTED.",
)
def get_device_status(db: Session = Depends(get_db)):
    """Check if the ESP32 device is currently connected (sending data)."""
    latest = (
        db.query(IoTOsmoseurReading)
        .order_by(IoTOsmoseurReading.created_at.desc())
        .first()
    )

    if not latest:
        return IoTOsmoseurStatusResponse(status="DISCONNECTED", last_seen=None)

    now = datetime.utcnow()
    last_seen = latest.created_at
    # Ensure we compare naive datetimes
    if last_seen.tzinfo is not None:
        last_seen = last_seen.replace(tzinfo=None)

    diff = (now - last_seen).total_seconds()

    return IoTOsmoseurStatusResponse(
        status="CONNECTED" if diff < 5 else "DISCONNECTED",
        last_seen=latest.created_at,
    )
