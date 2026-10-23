
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from datawarehouse.etl_dw import DataWarehouseETL
from app.routers.auth import require_manager

# Every admin route requires an authenticated manager
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_manager)]
)

@router.post("/run-dw-etl", status_code=status.HTTP_200_OK)
def run_data_warehouse_etl(db: Session = Depends(get_db)):
    """
    Trigger the ETL pipeline to populate the Data Warehouse.
    
    This process:
    1. Loads Dimension tables (Time, Technician)
    2. Loads Fact tables (Osmoseur, Remplisseuse) from source data
    
    Returns:
        JSON response with execution status.
    """
    try:
        etl = DataWarehouseETL(db)
        result = etl.run()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ETL execution failed: {str(e)}"
        )
