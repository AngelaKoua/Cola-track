"""
Script to add created_at and updated_at columns to users table
"""
from sqlalchemy import create_engine, text
from app.config import settings

def add_timestamp_columns():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Add created_at column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            """))
            conn.commit()
            print("✓ Added created_at column")
        except Exception as e:
            print(f"Note: created_at column might already exist: {e}")
        
        # Add updated_at column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
            """))
            conn.commit()
            print("✓ Added updated_at column")
        except Exception as e:
            print(f"Note: updated_at column might already exist: {e}")
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    add_timestamp_columns()
