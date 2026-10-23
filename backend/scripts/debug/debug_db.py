import sys
from app.config import settings
from sqlalchemy import create_engine, text

# Force UTF-8 encoding for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    print(f"DATABASE_URL repr: {repr(settings.DATABASE_URL)}")
    
    # Add client_encoding to settings-based connection
    engine = create_engine(settings.DATABASE_URL, connect_args={"client_encoding": "utf8"})
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Connection successful!")
        print(f"Result: {result.scalar()}")
        
except Exception as e:
    print("Connection failed!")
    try:
        print(f"Error: {e}")
    except:
        print(f"Error repr: {repr(e)}")
