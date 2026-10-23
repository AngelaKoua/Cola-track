#!/usr/bin/env python3
"""
ETL Execution Script for Colatrack Data Warehouse
=================================================

This script executes the ETL pipeline to populate the data warehouse
from the application database.

Usage:
    python run_etl.py

The script will:
1. Create a database session
2. Execute the DataWarehouseETL
3. Display results and any errors
"""

import sys
import logging
from datetime import datetime

from app.database import SessionLocal
from datawarehouse.etl_dw import DataWarehouseETL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Execute the ETL pipeline."""
    logger.info("=" * 70)
    logger.info("COLATRACK DATA WAREHOUSE ETL")
    logger.info("=" * 70)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    db = SessionLocal()
    results = {"dimensions": {}, "facts": {}}
    
    try:
        # Load Dimensions
        logger.info("Phase 1: Loading Dimensions")
        logger.info("-" * 50)
        
        # Dimension: Technician
        try:
            etl = DataWarehouseETL(db)
            etl.load_dim_technician()
            db.commit()
            results["dimensions"]["technician"] = "OK"
            logger.info("[OK] dim_technician loaded")
        except Exception as e:
            db.rollback()
            results["dimensions"]["technician"] = f"ERROR: {str(e)}"
            logger.error(f"[ERROR] dim_technician failed: {e}")
        
        # Dimension: Time
        try:
            etl = DataWarehouseETL(db)
            etl.load_dim_time()
            db.commit()
            results["dimensions"]["time"] = "OK"
            logger.info("[OK] dim_time loaded")
        except Exception as e:
            db.rollback()
            results["dimensions"]["time"] = f"ERROR: {str(e)}"
            logger.error(f"[ERROR] dim_time failed: {e}")
        
        logger.info("")
        logger.info("Phase 2: Loading Facts")
        logger.info("-" * 50)
        
        # Fact: Osmoseur
        try:
            etl = DataWarehouseETL(db)
            etl.load_fact_osmoseur()
            db.commit()
            results["facts"]["osmoseur"] = "OK"
            logger.info("[OK] fact_osmoseur_hourly loaded")
        except Exception as e:
            db.rollback()
            results["facts"]["osmoseur"] = f"ERROR: {str(e)}"
            logger.error(f"[ERROR] fact_osmoseur_hourly failed: {e}")
        
        # Fact: Remplisseuse
        try:
            etl = DataWarehouseETL(db)
            etl.load_fact_remplisseuse()
            db.commit()
            results["facts"]["remplisseuse"] = "OK"
            logger.info("[OK] fact_remplisseuse_hourly loaded")
        except Exception as e:
            db.rollback()
            results["facts"]["remplisseuse"] = f"ERROR: {str(e)[:100]}"
            logger.error(f"[ERROR] fact_remplisseuse_hourly failed: {e}")
        
        # Fact: Incidents
        try:
            etl = DataWarehouseETL(db)
            etl.load_fact_incident()
            db.commit()
            results["facts"]["incident"] = "OK"
            logger.info("[OK] fact_incident loaded")
        except Exception as e:
            db.rollback()
            results["facts"]["incident"] = f"ERROR: {str(e)[:100]}"
            logger.error(f"[ERROR] fact_incident failed: {e}")
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("ETL EXECUTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        logger.info("Results:")
        for category, items in results.items():
            logger.info(f"\n  {category.upper()}:")
            for name, status in items.items():
                logger.info(f"    {name:20} {status}")
        
        # Check if at least dimensions + osmoseur worked
        success_count = sum(1 for v in results["dimensions"].values() if v == "OK")
        success_count += sum(1 for v in results["facts"].values() if v == "OK")
        
        if success_count >= 3:  # At least dimensions + 1 fact
            logger.info("")
            logger.info("[PARTIAL SUCCESS] Data warehouse partially populated")
            logger.info("Next steps:")
            logger.info("  1. Check data: python -c \"from app.database import SessionLocal; from sqlalchemy import text; db = SessionLocal(); print('Osmoseur:', db.execute(text('SELECT COUNT(*) FROM dw.fact_osmoseur_hourly')).scalar()); print('Remplisseuse:', db.execute(text('SELECT COUNT(*) FROM dw.fact_remplisseuse_hourly')).scalar())\"")
            logger.info("  2. Test analytics endpoints at http://localhost:8000/docs")
            logger.info("  3. Check dashboard at http://localhost:3000/dashboard")
            logger.info("")
            return 0
        else:
            logger.error("")
            logger.error("[FAILED] Too many errors occurred")
            return 1
        
    except Exception as e:
        logger.error("")
        logger.error("=" * 70)
        logger.error("ETL FAILED - UNEXPECTED ERROR")
        logger.error("=" * 70)
        logger.error(f"Error: {str(e)}")
        logger.exception("Full traceback:")
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
