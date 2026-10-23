import sys
import logging
from app.database import SessionLocal
from sqlalchemy import text

# Capture detailed errors
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

db = SessionLocal()

try:
    print("=" * 70)
    print("TESTING REMPLISSEUSE ETL STEP BY STEP")
    print("=" * 70)
    
    # Step 1: Extract query
    print("\nStep 1: Running extraction query...")
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
    """)
    
    rows = db.execute(sql_extract).fetchall()
    print(f"   Found {len(rows)} aggregated rows to insert")
    
    if len(rows) == 0:
        print("ERROR: No rows to insert!")
        sys.exit(1)
    
    # Step 2: Process each row
    print("\nStep 2: Inserting rows one by one...")
    
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
    
    success_count = 0
    error_count = 0
    
    for i, row in enumerate(rows):
        try:
            # Delete existing
            db.execute(sql_delete, {"tid": row.time_id, "tech_id": row.technician_id})
            
            # Insert new
            params = {
                "tid": row.time_id,
                "tech_id": row.technician_id,
                "uc": row.unites_conformes,
                "ha": row.heures_arret,
                "rend": row.rendement,
                "mtbf": row.mtbf,
                "temp": row.temperature,
                "vol": row.volume,
                "carb": row.carbonation,
                "conso": row.conso_air_co2,
                "vib": row.vibrations
            }
            
            db.execute(sql_insert, params)
            success_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{len(rows)} rows...")
                
        except Exception as e:
            error_count += 1
            print(f"\n   ERROR on row {i + 1}:")
            print(f"   time_id={row.time_id}, tech_id={row.technician_id}")
            print(f"   Error: {e}")
            print(f"   Values: uc={row.unites_conformes}, ha={row.heures_arret}, rend={row.rendement}")
            print(f"           mtbf={row.mtbf}, temp={row.temperature}, vol={row.volume}")
            print(f"           carb={row.carbonation}, conso={row.conso_air_co2}, vib={row.vibrations}")
            
            if error_count > 5:
                print("\n   Too many errors, stopping...")
                break
    
    # Commit
    if error_count == 0:
        db.commit()
        print(f"\n✓ SUCCESS: All {success_count} rows inserted!")
    else:
        print(f"\n⚠ PARTIAL: {success_count} rows inserted, {error_count} errors")
        print("   Rolling back...")
        db.rollback()
    
    # Verify
    final_count = db.execute(text("SELECT COUNT(*) FROM dw.fact_remplisseuse_hourly")).scalar()
    print(f"\nFinal count in fact_remplisseuse_hourly: {final_count} rows")
    
except Exception as e:
    print(f"\nFATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 70)
