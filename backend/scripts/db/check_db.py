import psycopg2
import traceback

from app.config import settings
DSN = settings.DATABASE_URL

try:
    print(f"Connecting to {DSN}...")
    conn = psycopg2.connect(DSN)
    print("✅ Connected to 'postgres' database successfully!")
    
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='ctrack_db'")
    exists = cur.fetchone()
    
    if not exists:
        print("Database 'ctrack_db' does not exist. Creating it...")
        # Postgres cannot run CREATE DATABASE inside a transaction block
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur.execute("CREATE DATABASE ctrack_db")
        print("✅ Database 'ctrack_db' created successfully!")
    else:
        print("✅ Database 'ctrack_db' already exists!")
        
    cur.close()
    conn.close()

except Exception:
    with open("db_error.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    print("❌ Error logged to db_error.txt")

