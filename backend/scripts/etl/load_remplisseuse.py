from app.database import SessionLocal
from datawarehouse.etl_dw import DataWarehouseETL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SessionLocal()

try:
    logger.info("=" * 70)
    logger.info("LOADING REMPLISSEUSE FACT TABLE")
    logger.info("=" * 70)
    
    etl = DataWarehouseETL(db)
    etl.load_fact_remplisseuse()
    
    db.commit()
    
    logger.info("")
    logger.info("SUCCESS: Remplisseuse data loaded!")
    logger.info("")
    
    # Verify
    from sqlalchemy import text
    count = db.execute(text("SELECT COUNT(*) FROM dw.fact_remplisseuse_hourly")).scalar()
    logger.info(f"Total rows in fact_remplisseuse_hourly: {count}")
    
except Exception as e:
    logger.error(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
