from sqlalchemy import create_engine, text

from app.config import settings
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Check osmoseur_readings table
    result = conn.execute(text("SELECT * FROM osmoseur_readings ORDER BY created_at DESC LIMIT 1"))
    row = result.fetchone()
    
    if row:
        print("✅ Record found in database!")
        print("\nRecord details:")
        for key, value in row._mapping.items():
            print(f"  {key}: {value}")
    else:
        print("❌ No records found in osmoseur_readings table")
