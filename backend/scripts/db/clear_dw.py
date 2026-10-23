from app.database import SessionLocal
from sqlalchemy import text

def clear_dw_facts():
    db = SessionLocal()
    try:
        print("Clearing data warehouse fact tables...")
        # We delete from facts. Dimensions can stay as they just store metadata, but facts have the bulk data.
        db.execute(text("DELETE FROM dw.fact_osmoseur_hourly"))
        db.execute(text("DELETE FROM dw.fact_remplisseuse_hourly"))
        db.commit()
        print("Successfully cleared dw.fact_osmoseur_hourly and dw.fact_remplisseuse_hourly.")
    except Exception as e:
        print(f"Error clearing DW facts: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_dw_facts()
