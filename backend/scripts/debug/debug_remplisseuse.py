from app.database import SessionLocal
from sqlalchemy import text
import traceback

db = SessionLocal()

try:
    print("=" * 70)
    print("DEBUGGING REMPLISSEUSE ETL ERROR")
    print("=" * 70)
    
    # Check source data exists
    print("\n1. Checking source data...")
    count = db.execute(text("SELECT COUNT(*) FROM remplisseuse_readings")).scalar()
    print(f"   remplisseuse_readings: {count} rows")
    
    if count == 0:
        print("   ERROR: No source data!")
        exit(1)
    
    # Check sample data
    print("\n2. Sample source data:")
    sample = db.execute(text("""
        SELECT id, technician_name, created_at 
        FROM remplisseuse_readings 
        LIMIT 3
    """)).fetchall()
    for row in sample:
        print(f"   ID: {row[0]}, Tech: {row[1]}, Date: {row[2]}")
    
    # Check if technicians exist in dim_technician
    print("\n3. Checking dim_technician...")
    tech_count = db.execute(text("SELECT COUNT(*) FROM dw.dim_technician")).scalar()
    print(f"   dim_technician: {tech_count} rows")
    
    # Try the extraction query from ETL
    print("\n4. Testing ETL extraction query...")
    sql_extract = text("""
        SELECT 
            to_char(r.created_at AT TIME ZONE 'UTC', 'YYYYMMDDHH24')::bigint as time_id,
            dt.technician_id,
            AVG(r.unites_produites_conformes) as unites_conformes,
            AVG(r.heures_arret) as heures_arret,
            AVG(r.rendement) as rendement,
            AVG(r.mtbf) as mtbf,
            AVG(r.temperature_remplissage) as temperature,
            AVG(r.volume_remplissage) as volume,
            AVG(r.carbonation) as carbonation,
            AVG(r.conso_air_co2) as conso_air_co2,
            AVG(r.vibrations) as vibrations
        FROM remplisseuse_readings r
        JOIN dw.dim_technician dt ON dt.original_name = r.technician_name
        GROUP BY 1, 2
        LIMIT 5
    """)
    
    rows = db.execute(sql_extract).fetchall()
    print(f"   Query returned {len(rows)} rows")
    
    if len(rows) > 0:
        print("\n5. Sample aggregated data:")
        for i, row in enumerate(rows[:3]):
            print(f"   Row {i+1}: time_id={row[0]}, tech_id={row[1]}, unites={row[2]}, rendement={row[4]}")
        
        # Try to insert one row
        print("\n6. Testing insert of first row...")
        first_row = rows[0]
        
        sql_delete = text("""
            DELETE FROM dw.fact_remplisseuse_hourly 
            WHERE time_id = :tid AND technician_id = :tech_id
        """)
        
        sql_insert = text("""
            INSERT INTO dw.fact_remplisseuse_hourly (
                time_id, technician_id,
                unites_conformes, heures_arret, rendement, mtbf,
                temperature, volume, carbonation, conso_air_co2, vibrations
            ) VALUES (
                :tid, :tech_id,
                :uc, :ha, :rend, :mtbf,
                :temp, :vol, :carb, :conso, :vib
            )
        """)
        
        db.execute(sql_delete, {"tid": first_row[0], "tech_id": first_row[1]})
        
        db.execute(sql_insert, {
            "tid": first_row[0],
            "tech_id": first_row[1],
            "uc": first_row[2],
            "ha": first_row[3],
            "rend": first_row[4],
            "mtbf": first_row[5],
            "temp": first_row[6],
            "vol": first_row[7],
            "carb": first_row[8],
            "conso": first_row[9],
            "vib": first_row[10]
        })
        
        db.commit()
        print("   SUCCESS: Test row inserted!")
        
        # Check if it's in the table
        final_count = db.execute(text("SELECT COUNT(*) FROM dw.fact_remplisseuse_hourly")).scalar()
        print(f"   fact_remplisseuse_hourly now has {final_count} rows")
        
    else:
        print("   ERROR: Extraction query returned 0 rows!")
        print("\n   Checking JOIN condition...")
        
        # Check if technician names match
        source_techs = db.execute(text("""
            SELECT DISTINCT technician_name 
            FROM remplisseuse_readings 
            ORDER BY technician_name
        """)).fetchall()
        
        dim_techs = db.execute(text("""
            SELECT original_name 
            FROM dw.dim_technician 
            ORDER BY original_name
        """)).fetchall()
        
        print(f"\n   Source technicians ({len(source_techs)}):")
        for t in source_techs:
            print(f"     - '{t[0]}'")
        
        print(f"\n   Dimension technicians ({len(dim_techs)}):")
        for t in dim_techs:
            print(f"     - '{t[0]}'")

except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 70)
