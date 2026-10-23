
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, SessionLocal
from app.models.osmoseur import Osmoseur
from app.models.remplisseuse import Remplisseuse

# Configuration
DAYS_HISTORY = 30
RECORDS_PER_DAY = 3 # ~90 records per machine
TECHNICIANS = ["Jean Dupont", "Marie Currie", "Pierre Martin", "Sophie Germain"]

def seed_osmoseur(db):
    print("Seeding Osmoseur readings...")
    
    start_date = datetime.utcnow() - timedelta(days=DAYS_HISTORY)
    
    for day in range(DAYS_HISTORY):
        for _ in range(RECORDS_PER_DAY):
            # Time distribution (morning, noon, afternoon)
            hour = random.choice([8, 10, 12, 14, 16])
            record_date = start_date + timedelta(days=day)
            record_date = record_date.replace(hour=hour, minute=random.randint(0, 59))
            
            # Realistic data generation
            # Efficiency drops slightly over time then recovers (simulating maintenance)
            efficiency_factor = 1.0 - ((day % 10) * 0.02) 
            
            debit_permeat = 15000 * efficiency_factor * random.uniform(0.95, 1.05)
            debit_concentrat = 5000 * random.uniform(0.9, 1.1)
            total_flow = debit_permeat + debit_concentrat
            taux_recuperation = (debit_permeat / total_flow) * 100
            
            reading = Osmoseur(
                technician_name=random.choice(TECHNICIANS),
                debit_permeat=round(debit_permeat, 2),
                debit_concentrat=round(debit_concentrat, 2),
                taux_recuperation=round(taux_recuperation, 2),
                conductivite_permeat=round(random.uniform(10, 25), 1),
                ph_entree=round(random.uniform(7.0, 7.8), 1),
                ph_sortie=round(random.uniform(6.5, 7.2), 1),
                turbidite=round(random.uniform(0.1, 0.5), 2),
                chlore_libre=round(random.uniform(0.01, 0.1), 2),
                durete_totale=round(random.uniform(0, 5), 1),
                tds=round(random.uniform(50, 150), 1),
                created_at=record_date,
                updated_at=record_date
            )
            db.add(reading)
    
    db.commit()
    print("Osmoseur seeded.")

def seed_remplisseuse(db):
    print("Seeding Remplisseuse readings...")
    
    start_date = datetime.utcnow() - timedelta(days=DAYS_HISTORY)
    
    for day in range(DAYS_HISTORY):
        for _ in range(RECORDS_PER_DAY):
            hour = random.choice([9, 11, 13, 15, 17])
            record_date = start_date + timedelta(days=day)
            record_date = record_date.replace(hour=hour, minute=random.randint(0, 59))
            
            # Correlation simulation: High Temp -> Lower Efficiency
            temp = random.uniform(2, 8)
            eff_hit = 0
            if temp > 6:
                eff_hit = random.uniform(5, 15)
                
            unites = 10000 * random.uniform(0.8, 1.0)
            stops = random.uniform(0, 2) + (temp > 6 and 1 or 0)
            
            # Simplified calculation
            theoretical = (24 - stops) * 500 # Just a base for ratio
            if theoretical <= 0: theoretical = 1
            rendement = min(98.0, (unites / theoretical * 400)) # Fake formula to get nice %
            rendement = max(60.0, rendement - eff_hit)
            
            reading = Remplisseuse(
                technician_name=random.choice(TECHNICIANS),
                temperature_remplissage=round(temp, 1),
                volume_remplissage=round(random.uniform(1.48, 1.52), 2),
                carbonation=round(random.uniform(7.8, 8.2), 1),
                unites_produites_conformes=int(unites),
                heures_arret=round(stops, 1),
                mtbf=round(random.uniform(40, 150), 1),
                rendement=round(rendement, 2),
                conso_air_co2=round(random.uniform(100, 140), 1),
                vibrations=round(random.uniform(1.5, 4.5), 1),
                created_at=record_date,
                updated_at=record_date
            )
            db.add(reading)
            
    db.commit()
    print("Remplisseuse seeded.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_osmoseur(db)
        seed_remplisseuse(db)
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
