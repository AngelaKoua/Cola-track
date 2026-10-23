import random
import uuid
from datetime import datetime, timedelta
import math

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, SessionLocal, engine
from app.models.osmoseur import Osmoseur
from app.models.remplisseuse import Remplisseuse

# Configuration
DAYS_HISTORY = 30
RECORDS_PER_DAY = 3  # Morning, Noon, Afternoon (approx)
TECHNICIANS = ["Jean Dupont", "Marie Currie", "Pierre Martin", "Sophie Germain"]

def seed_realistic_data():
    db = SessionLocal()
    try:
        print("Clearing existing data for a clean slate...")
        # Optional: Clear existing data to avoid duplicates/confusion
        db.query(Osmoseur).delete()
        db.query(Remplisseuse).delete()
        db.commit()
        print("Data cleared.")

        print(f"Seeding {DAYS_HISTORY} days of realistic data...")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=DAYS_HISTORY)

        for day in range(DAYS_HISTORY):
            current_day_date = start_date + timedelta(days=day)
            
            # ----------------------------------------------------------------
            # SCENARIO CONFIGURATION FOR THIS DAY
            # ----------------------------------------------------------------
            
            # Scenario A: Remplisseuse - Vibration Creep (Day 10-18), Breakdown (Day 19)
            # Normal: ~2.0 mm/s. Warning: >7.1. Breakdown: Spikes and Stop.
            remp_vibration_base = 2.5
            remp_stops_base = 0.5
            remp_temp_base = 4.0
            
            if 10 <= day <= 18:
                # Gradual increase from 2.5 to 9.0
                progress = (day - 10) / 8.0
                remp_vibration_base = 2.5 + (progress * 6.5) 
            elif day == 19:
                # Breakdown day!
                remp_vibration_base = 12.0 # High vibration
                remp_stops_base = 8.0     # 8 hours down
            else:
                # Normal or recovered
                remp_vibration_base = 2.5

            # Scenario B: Osmoseur - Membrane Fouling (Day 5-25)
            # Permeate flow drops, Conductivity rises.
            # Normal Flow: ~15000 L/h. Normal Cond: ~15 uS/cm.
            osmo_flow_factor = 1.0
            osmo_cond_base = 15.0
            
            if 5 <= day <= 25:
                # Gradual fouling
                progress = (day - 5) / 20.0
                osmo_flow_factor = 1.0 - (progress * 0.25) # Drops to 75%
                osmo_cond_base = 15.0 + (progress * 15.0)  # Rises to 30 uS/cm
            elif day > 25:
                # Cleaned/Replaced
                osmo_flow_factor = 1.0
                osmo_cond_base = 14.0 # Slightly better than old normal

            # Scenario C: Remplisseuse - Temp Spike (Random days)
            # Causes low carbonation and low efficiency
            is_temp_spike = False
            if day in [3, 14, 27]: # Specific "random" days
                is_temp_spike = True
                remp_temp_base = 8.5 # Too warm!
            

            # ----------------------------------------------------------------
            # GENERATE RECORDS FOR THE DAY
            # ----------------------------------------------------------------
            for _ in range(RECORDS_PER_DAY):
                hour = random.choice([8, 10, 12, 14, 16])
                record_time = current_day_date.replace(hour=hour, minute=random.randint(0, 59))
                
                # --- OSMOSEUR ---
                # Apply scenario factors with some noise
                flow_noise = random.uniform(0.98, 1.02)
                debit_permeat = 15000 * osmo_flow_factor * flow_noise
                debit_concentrat = 5000 * random.uniform(0.95, 1.05)
                total_flow = debit_permeat + debit_concentrat
                taux_recup = (debit_permeat / total_flow) * 100
                
                cond_noise = random.uniform(-1, 2)
                conductivite = osmo_cond_base + cond_noise
                
                osmo = Osmoseur(
                    technician_name=random.choice(TECHNICIANS),
                    debit_permeat=round(debit_permeat, 2),
                    debit_concentrat=round(debit_concentrat, 2),
                    taux_recuperation=round(taux_recup, 2),
                    conductivite_permeat=round(conductivite, 1),
                    ph_entree=round(random.uniform(7.0, 7.5), 1),
                    ph_sortie=round(random.uniform(6.5, 7.0), 1),
                    turbidite=round(random.uniform(0.1, 0.4), 2),
                    chlore_libre=round(random.uniform(0.01, 0.05), 2),
                    durete_totale=round(random.uniform(0.1, 1.0), 1),
                    tds=round(conductivite * 0.6, 1), # Rough estimation
                    created_at=record_time,
                    updated_at=record_time
                )
                db.add(osmo)

                # --- REMPLISSEUSE ---
                # Apply scenario factors
                temp_noise = random.uniform(-0.5, 0.5)
                temp = remp_temp_base + temp_noise
                
                vib_noise = random.uniform(-0.2, 0.5)
                vibration = remp_vibration_base + vib_noise
                
                stops_noise = random.uniform(0, 0.5) if remp_stops_base < 1 else random.uniform(-1, 1)
                stops = max(0, remp_stops_base + stops_noise)
                
                # Carbonation depends on temp (physics!)
                # Ideal is ~8g/L at 4C. Drops as temp rises.
                carb_base = 8.0 - ((temp - 4.0) * 0.4) 
                carbonation = max(4.0, carb_base + random.uniform(-0.2, 0.2))
                
                # Efficiency depends on stops and temp
                rendement_base = 95.0 - (stops * 2.0) - (max(0, temp - 6.0) * 5.0)
                rendement = max(50.0, min(99.0, rendement_base + random.uniform(-1, 1)))

                remp = Remplisseuse(
                    technician_name=random.choice(TECHNICIANS),
                    temperature_remplissage=round(temp, 1),
                    volume_remplissage=round(random.uniform(1.49, 1.51), 3),
                    carbonation=round(carbonation, 1),
                    unites_produites_conformes=int(10000 * (rendement/100)),
                    heures_arret=round(stops, 1),
                    mtbf=round(random.uniform(40, 100), 1), # Roughly constant unless calculated over time
                    rendement=round(rendement, 1),
                    conso_air_co2=round(random.uniform(110, 130), 1),
                    vibrations=round(vibration, 1),
                    created_at=record_time,
                    updated_at=record_time
                )
                db.add(remp)

        db.commit()
        print("Successfully seeded realistic data with failure scenarios.")
        
    except Exception:
        import traceback
        with open("final_error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("Error logged to final_error.log")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_realistic_data()
