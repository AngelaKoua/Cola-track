import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker

from app.database import SessionLocal
from app.models.osmoseur import Osmoseur
from app.models.remplisseuse import Remplisseuse

TECHNICIANS = ["Jean Dupont", "Marie Currie", "Pierre Martin", "Sophie Germain"]

def seed_data_for_q1_2026():
    db = SessionLocal()
    try:
        print("Clearing existing data for a clean slate...")
        db.query(Osmoseur).delete()
        db.query(Remplisseuse).delete()
        db.commit()
        print("Data cleared.")

        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 3, 14, 23, 59, 59)
        total_days = (end_date - start_date).days + 1  # 73 days
        
        print(f"Seeding {total_days} days of realistic data from {start_date.date()} to {end_date.date()}...")
        
        for day in range(total_days):
            current_day_date = start_date + timedelta(days=day)
            
            # ----------------------------------------------------------------
            # SCENARIO CONFIGURATION FOR THIS DAY
            # ----------------------------------------------------------------
            
            # --- Remplisseuse Scenarios ---
            remp_vibration_base = 2.5
            remp_stops_base = 0.5
            remp_temp_base = 4.0
            
            # Jan 16 - Jan 25 (Days 15-24): Vibration creep
            # Jan 26 (Day 25): Breakdown
            if 15 <= day <= 24:
                progress = (day - 15) / 9.0
                remp_vibration_base = 2.5 + (progress * 6.5)
            elif day == 25:
                remp_vibration_base = 12.0
                remp_stops_base = 8.0
            
            # Feb 10 - Feb 24 (Days 40-54): Sporadic Temp spikes
            is_temp_spike = False
            if day in [42, 48, 53]: # Specific days
                is_temp_spike = True
                remp_temp_base = 8.5
                
            # Mar 1 - Mar 10 (Days 59-68): Gradual mechanical degradation
            if 59 <= day <= 68:
                progress = (day - 59) / 9.0
                remp_stops_base = 0.5 + (progress * 3.5) # Stops go up to 4.0
                remp_vibration_base = 2.5 + (progress * 3.0)

            # --- Osmoseur Scenarios ---
            osmo_flow_factor = 1.0
            osmo_cond_base = 15.0
            osmo_ph_entree = 7.2
            osmo_chlore_base = 0.03
            
            # Jan 11 - Jan 30 (Days 10-29): Membrane fouling
            if 10 <= day <= 29:
                progress = (day - 10) / 19.0
                osmo_flow_factor = 1.0 - (progress * 0.20) # Drops to 80%
                osmo_cond_base = 15.0 + (progress * 15.0)  # Rises to 30 uS/cm
            elif day > 29 and day < 45: # Post cleaning, back to normal until next event
                osmo_flow_factor = 1.0
                osmo_cond_base = 14.0
                
            # Feb 15 - Mar 1 (Days 45-59): Chlorination / pH issues
            if 45 <= day <= 59:
                progress = (day - 45) / 14.0
                osmo_chlore_base = 0.03 + (progress * 0.12) # Rises to 0.15 mg/L
                osmo_ph_entree = 7.2 + (progress * 0.8) # Rises to 8.0
                
            # Mar 2 - Mar 14 (Days 60-72): Accelerated membrane fouling critical
            if 60 <= day <= 72:
                progress = (day - 60) / 12.0
                osmo_flow_factor = 1.0 - (progress * 0.40) # Drops to 60%
                osmo_cond_base = 15.0 + (progress * 40.0) # Cond rises to 55 uS/cm

            # ----------------------------------------------------------------
            # GENERATE RECORDS FOR THE DAY
            # ----------------------------------------------------------------
            RECORDS_PER_DAY = 3
            for _ in range(RECORDS_PER_DAY):
                hour = random.choice([8, 11, 14, 16])
                record_time = current_day_date.replace(hour=hour, minute=random.randint(0, 59))
                
                # --- OSMOSEUR ---
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
                    ph_entree=round(osmo_ph_entree + random.uniform(-0.1, 0.1), 1),
                    ph_sortie=round((osmo_ph_entree - 0.5) + random.uniform(-0.1, 0.1), 1),
                    turbidite=round(random.uniform(0.1, 0.4), 2),
                    chlore_libre=round(osmo_chlore_base + random.uniform(-0.01, 0.01), 2),
                    durete_totale=round(random.uniform(0.1, 1.0), 1),
                    tds=round(conductivite * 0.6, 1),
                    created_at=record_time,
                    updated_at=record_time
                )
                db.add(osmo)

                # --- REMPLISSEUSE ---
                temp_noise = random.uniform(-0.5, 0.5)
                temp = remp_temp_base + temp_noise
                
                vib_noise = random.uniform(-0.2, 0.5)
                vibration = remp_vibration_base + vib_noise
                
                stops_noise = random.uniform(0, 0.5) if remp_stops_base < 1 else random.uniform(-1, 1)
                stops = max(0, remp_stops_base + stops_noise)
                
                carb_base = 8.0 - ((temp - 4.0) * 0.4) 
                carbonation = max(4.0, carb_base + random.uniform(-0.2, 0.2))
                
                rendement_base = 95.0 - (stops * 2.0) - (max(0, temp - 6.0) * 5.0)
                rendement = max(50.0, min(99.0, rendement_base + random.uniform(-1, 1)))

                remp = Remplisseuse(
                    technician_name=random.choice(TECHNICIANS),
                    temperature_remplissage=round(temp, 1),
                    volume_remplissage=round(random.uniform(1.49, 1.51), 3),
                    carbonation=round(carbonation, 1),
                    unites_produites_conformes=int(10000 * (rendement/100)),
                    heures_arret=round(stops, 1),
                    mtbf=round(max(10, 100 - (stops * 10) - (vibration * 2)), 1),
                    rendement=round(rendement, 1),
                    conso_air_co2=round(random.uniform(110, 130), 1),
                    vibrations=round(vibration, 1),
                    created_at=record_time,
                    updated_at=record_time
                )
                db.add(remp)

        db.commit()
        print("Successfully seeded realistic data for Q1 2026.")
        
    except Exception:
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data_for_q1_2026()
