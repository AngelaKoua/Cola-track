import asyncio
import logging
from app.database import SessionLocal
from app.repositories.telemetry_repository import TelemetryRepository
from app.services.feature_service import FeatureService
from app.services.ml_service import MLService
from app.models.prediction import Prediction

logger = logging.getLogger(__name__)

# Usually, we'd query active machines dynamically, but for Phase 3 we mock the 2 known ones.
ACTIVE_MACHINES = ["OSM-001", "RMP-001"]

async def run_predictions_for_all_machines():
    """
    Core Background Job.
    Loops through all machines, runs inference, and writes results to the Prediction table.
    """
    logger.info("Scheduler: Starting background inference cycle...")
    db = SessionLocal()
    try:
        repo = TelemetryRepository(db)
        feat_service = FeatureService(repo)
        ml_service = MLService(feat_service)
        
        for machine_id in ACTIVE_MACHINES:
            logger.debug(f"Scheduler: Running inference for {machine_id}")
            result = ml_service.process_machine(machine_id)
            
            if result:
                # Save to database
                new_prediction = Prediction(
                    machine_id=result["machine_id"],
                    health_index=result["health_index"],
                    failure_probability_24h=result["failure_probability_24h"],
                    quality_risk=result["quality_risk"],
                    is_anomaly=result["is_anomaly"],
                    alert_level=result["alert_level"],
                    reason=result["reason"]
                )
                db.add(new_prediction)
                db.commit()
                logger.info(f"Scheduler: Saved prediction for {machine_id} (Level: {result['alert_level']})")
            else:
                logger.warning(f"Scheduler: Failed to compute prediction for {machine_id}. Missing telemetry?")
                
    except Exception as e:
        logger.error(f"Scheduler: Inference loop failed - {str(e)}")
        db.rollback()
    finally:
        db.close()

async def inference_worker(interval_seconds: int = 300):
    """
    Long-running background task simulating an industrial cron job.
    """
    logger.info(f"Background Inference Worker started. Interval: {interval_seconds}s")
    while True:
        await run_predictions_for_all_machines()
        await asyncio.sleep(interval_seconds)
