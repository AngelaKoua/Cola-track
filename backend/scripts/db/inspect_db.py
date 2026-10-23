from sqlalchemy import create_engine, text, inspect

from app.config import settings
engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

print("=== Tables in database ===")
tables = inspector.get_table_names()
for table in tables:
    print(f"\n📋 Table: {table}")
    columns = inspector.get_columns(table)
    print("Columns:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")

# Check if there's any data
with engine.connect() as conn:
    for table in tables:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
        print(f"\n{table}: {count} records")
