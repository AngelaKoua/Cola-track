from app.database import SessionLocal
from datawarehouse.etl_dw import DataWarehouseETL
import traceback

db = SessionLocal()
etl = DataWarehouseETL(db)

try:
    print('Loading Remplisseuse facts...')
    etl.load_fact_remplisseuse()
    db.commit()
    print('✓ Remplisseuse loaded successfully')
except Exception as e:
    print(f'ERROR: {e}')
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
