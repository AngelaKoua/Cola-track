
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta, timezone
import logging
import traceback
from typing import List, Dict, Any

from app.database import SessionLocal
from app.models.osmoseur import Osmoseur
from app.models.remplisseuse import Remplisseuse
from app.models.incident import Incident

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DataWarehouseETL:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        """Main execution method for the ETL pipeline."""
        logger.info("Starting Data Warehouse ETL...")
        try:
            # 1. Load Dimensions
            self.load_dim_technician()
            self.load_dim_time() 
            
            # 2. Load Facts
            self.load_fact_osmoseur()
            self.load_fact_remplisseuse()
            self.load_fact_incident()
            
            self.db.commit()
            logger.info("ETL completed successfully.")
            return {"status": "success", "message": "ETL executed successfully"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"ETL failed: {str(e)}")
            traceback.print_exc()
            raise e

    def _generate_time_id(self, dt: datetime) -> int:
        """Converts datetime to YYYYMMDDHH format."""
        return int(dt.strftime("%Y%m%d%H"))

    def load_dim_technician(self):
        logger.info("Loading Dimension: Technician")
        
        sql_extract = text("""
            SELECT DISTINCT technician_name FROM osmoseur_readings
            UNION
            SELECT DISTINCT technician_name FROM remplisseuse_readings
            UNION
            SELECT DISTINCT responsable as technician_name FROM incidents
        """)
        
        sql_insert = text("""
            INSERT INTO dw.dim_technician (original_name, first_seen_at)
            VALUES (:name, NOW())
            ON CONFLICT (original_name) DO NOTHING
        """)
        
        techs = self.db.execute(sql_extract).fetchall()
        
        for (tech_name,) in techs:
            if tech_name:
                self.db.execute(sql_insert, {"name": tech_name})

    def load_dim_time(self):
        logger.info("Loading Dimension: Time")
        
        min_date_osmo = self.db.query(func.min(Osmoseur.created_at)).scalar()
        min_date_remp = self.db.query(func.min(Remplisseuse.created_at)).scalar()
        
        current_time = datetime.now(timezone.utc)
        
        # Handle case where DB is empty
        dates = [d for d in [min_date_osmo, min_date_remp] if d]
        if not dates:
            min_date = current_time
        else:
            min_date = min(dates + [current_time])
            
        max_date = current_time
        
        start_dt = min_date.replace(minute=0, second=0, microsecond=0)
        end_dt = max_date.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        current = start_dt
        
        sql_check = text("SELECT 1 FROM dw.dim_time WHERE time_id = :tid")
        sql_insert = text("""
            INSERT INTO dw.dim_time (
                time_id, full_timestamp, year, month, day, 
                hour, quarter, day_of_week, is_weekend
            ) VALUES (
                :tid, :ts, :yr, :mo, :dy, 
                :hr, :q, :dow, :is_we
            )
        """)
        
        while current < end_dt:
            time_id = self._generate_time_id(current)
            
            if not self.db.execute(sql_check, {"tid": time_id}).scalar():
                is_weekend = current.weekday() >= 5
                quarter = (current.month - 1) // 3 + 1
                
                self.db.execute(sql_insert, {
                    "tid": time_id,
                    "ts": current,
                    "yr": current.year,
                    "mo": current.month,
                    "dy": current.day,
                    "hr": current.hour,
                    "q": quarter,
                    "dow": current.weekday() + 1,
                    "is_we": is_weekend
                })
            
            current += timedelta(hours=1)

    def load_fact_osmoseur(self):
        logger.info("Loading Fact: Osmoseur (Hourly)")
        
        sql_extract = text("""
            SELECT 
                to_char(o.created_at, 'YYYYMMDDHH')::bigint as time_id,
                dt.technician_id,
                AVG(o.debit_permeat) as debit_permeat,
                AVG(o.debit_concentrat) as debit_concentrat,
                AVG(o.taux_recuperation) as taux_recuperation,
                AVG(o.conductivite_permeat) as conductivite_permeat,
                AVG(o.ph_entree) as ph_entree,
                AVG(o.ph_sortie) as ph_sortie,
                AVG(o.turbidite) as turbidite,
                AVG(o.chlore_libre) as chlore_libre,
                AVG(o.durete_totale) as durete_totale,
                AVG(o.tds) as tds
            FROM osmoseur_readings o
            JOIN dw.dim_technician dt ON dt.original_name = o.technician_name
            GROUP BY 1, 2
        """)
        
        sql_delete = text("""
            DELETE FROM dw.fact_osmoseur_hourly 
            WHERE time_id = :tid AND technician_id = :tech_id
        """)
        
        sql_insert = text("""
            INSERT INTO dw.fact_osmoseur_hourly (
                time_id, technician_id,
                debit_permeat, debit_concentrat, taux_recuperation,
                conductivite_permeat, ph_entree, ph_sortie,
                turbidite, chlore_libre, durete_totale, tds
            ) VALUES (
                :tid, :tech_id,
                :dp, :dc, :tr,
                :cp, :phe, :phs,
                :tur, :cl, :dt, :tds
            )
        """)
        
        rows = self.db.execute(sql_extract).fetchall()
        
        for row in rows:
            self.db.execute(sql_delete, {"tid": row.time_id, "tech_id": row.technician_id})
            
            self.db.execute(sql_insert, {
                "tid": row.time_id,
                "tech_id": row.technician_id,
                "dp": row.debit_permeat,
                "dc": row.debit_concentrat,
                "tr": row.taux_recuperation,
                "cp": row.conductivite_permeat,
                "phe": row.ph_entree,
                "phs": row.ph_sortie,
                "tur": row.turbidite,
                "cl": row.chlore_libre,
                "dt": row.durete_totale,
                "tds": row.tds
            })

    def load_fact_remplisseuse(self):
        logger.info("Loading Fact: Remplisseuse (Hourly)")
        
        sql_extract = text("""
            SELECT 
                to_char(r.created_at, 'YYYYMMDDHH')::bigint as time_id,
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
        
        rows = self.db.execute(sql_extract).fetchall()
        logger.info(f"Found {len(rows)} aggregated rows to process")
        
        success_count = 0
        error_count = 0
        
        for i, row in enumerate(rows):
            try:
                # Use nested transaction (savepoint) for each row
                with self.db.begin_nested():
                    self.db.execute(sql_delete, {"tid": row.time_id, "tech_id": row.technician_id})
                    
                    self.db.execute(sql_insert, {
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
                    })
                success_count += 1
                
            except Exception as e:
                error_count += 1
                logger.warning(f"Failed to insert row {i+1} (time_id={row.time_id}): {str(e)[:100]}")
                # Continue processing other rows
        
        logger.info(f"Remplisseuse ETL completed: {success_count} rows inserted, {error_count} errors")


    def load_fact_incident(self):
        logger.info("Loading Fact: Incidents")
        
        sql_extract = text("""
            SELECT
                to_char(i.date_declaration, 'YYYYMMDDHH')::bigint as time_id,
                dt.technician_id,
                i.id as incident_uuid,
                i.equipement,
                i.type_incident,
                i.criticite,
                i.statut,
                EXTRACT(EPOCH FROM i.temps_resolution)/3600 as temps_resolution_hours
            FROM incidents i
            JOIN dw.dim_technician dt ON dt.original_name = i.responsable
        """)
        
        sql_upsert = text("""
            INSERT INTO dw.fact_incident (
                time_id, technician_id, incident_uuid,
                equipement, type_incident, criticite, statut,
                temps_resolution_hours
            ) VALUES (
                :tid, :tech_id, :uuid,
                :equip, :type_inc, :crit, :statut,
                :resolution
            )
            ON CONFLICT (incident_uuid) DO UPDATE SET
                statut = EXCLUDED.statut,
                temps_resolution_hours = EXCLUDED.temps_resolution_hours,
                criticite = EXCLUDED.criticite
        """)
        
        rows = self.db.execute(sql_extract).fetchall()
        logger.info(f"Found {len(rows)} incidents to process")
        
        success_count = 0
        error_count = 0
        
        for i, row in enumerate(rows):
            try:
                with self.db.begin_nested():
                    self.db.execute(sql_upsert, {
                        "tid": row.time_id,
                        "tech_id": row.technician_id,
                        "uuid": row.incident_uuid,
                        "equip": row.equipement,
                        "type_inc": row.type_incident,
                        "crit": row.criticite,
                        "statut": row.statut,
                        "resolution": row.temps_resolution_hours
                    })
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.warning(f"Failed to upsert incident {row.incident_uuid}: {str(e)[:100]}")
        
        logger.info(f"Incident ETL completed: {success_count} rows processed, {error_count} errors")
