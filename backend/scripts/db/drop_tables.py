from sqlalchemy import create_engine, text

from app.config import settings
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    print("🗑️  Dropping existing tables...")
    
    # Drop tables in correct order (handle foreign keys)
    conn.execute(text("DROP TABLE IF EXISTS osmoseur_readings CASCADE"))
    print("  ✅ Dropped osmoseur_readings")
    
    conn.execute(text("DROP TABLE IF EXISTS remplisseuse_readings CASCADE"))
    print("  ✅ Dropped remplisseuse_readings")
    
    conn.execute(text("DROP TABLE IF EXISTS machines CASCADE"))
    print("  ✅ Dropped machines")
    
    conn.commit()
    print("\n✅ All old tables dropped successfully!")
    print("📝 The FastAPI server will auto-create new tables on next restart.")
