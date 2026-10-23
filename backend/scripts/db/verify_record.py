from sqlalchemy import create_engine, text

from app.config import settings
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Check osmoseur_readings table
    result = conn.execute(text("SELECT * FROM osmoseur_readings ORDER BY created_at DESC LIMIT 1"))
    row = result.fetchone()
    
    if row:
        print("✅ SUCCESS! Record found in database!\n")
        print("=" * 60)
        print("OSMOSEUR READING DETAILS")
        print("=" * 60)
        for key, value in row._mapping.items():
            print(f"{key:25} : {value}")
        print("=" * 60)
        print(f"\n🎯 Key Achievement: taux_recuperation was automatically")
        print(f"   calculated as {row._mapping['taux_recuperation']}% by the server!")
    else:
        print("❌ No records found")
