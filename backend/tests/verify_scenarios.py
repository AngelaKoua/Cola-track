import pandas as pd
from sqlalchemy import create_engine
from app.database import engine
import sys

def verify_scenarios():
    with open("verify_result.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")

        log("Verifying seeded data scenarios...")
        
        # Load data into Pandas
        query_remp = "SELECT * FROM remplisseuse_readings ORDER BY created_at"
        df_remp = pd.read_sql(query_remp, engine)
        
        query_osmo = "SELECT * FROM osmoseur_readings ORDER BY created_at"
        df_osmo = pd.read_sql(query_osmo, engine)
        
        log(f"Loaded {len(df_remp)} Remplisseuse records and {len(df_osmo)} Osmoseur records.")

        # Ensure created_at is datetime
        df_remp['created_at'] = pd.to_datetime(df_remp['created_at'], utc=True)
        df_osmo['created_at'] = pd.to_datetime(df_osmo['created_at'], utc=True)

        # ----------------------------------------------------------------
        # VERIFY SCENARIO A: Vibration Creep (Day 10-18)
        # ----------------------------------------------------------------
        log("\n--- Checking Scenario A: Vibration Creep ---")
        # Add a 'day_index' for easier grouping (assuming 30 days history)
        df_remp['day_index'] = (df_remp['created_at'] - df_remp['created_at'].min()).dt.days
        
        # We expect vibrations to rise from day 10 to 18
        # Let's get average vibration per day
        daily_vib = df_remp.groupby('day_index')['vibrations'].mean()
        
        vib_start = daily_vib.get(10, 0)
        vib_end = daily_vib.get(18, 0)
        
        log(f"Avg Vibration Day 10: {vib_start:.2f}")
        log(f"Avg Vibration Day 18: {vib_end:.2f}")
        
        if vib_end > vib_start + 3.0: # Expect meaningful increase
            log("✅ SUCCESS: Vibration creep detected.")
        else:
            log("❌ FAILURE: Vibration creep NOT detected or too subtle.")

        # Check for breakdown on Day 19
        stops_day_19 = df_remp[df_remp['day_index'] == 19]['heures_arret'].mean()
        log(f"Avg Stops Day 19: {stops_day_19:.2f} hours")
        if stops_day_19 > 5.0:
            log("✅ SUCCESS: Breakdown on Day 19 detected.")
        else:
            log("❌ FAILURE: Breakdown on Day 19 NOT detected.")

        # ----------------------------------------------------------------
        # VERIFY SCENARIO B: Membrane Fouling (Day 5-25)
        # ----------------------------------------------------------------
        log("\n--- Checking Scenario B: Membrane Fouling ---")
        df_osmo['day_index'] = (df_osmo['created_at'] - df_osmo['created_at'].min()).dt.days
        
        daily_flow = df_osmo.groupby('day_index')['debit_permeat'].mean()
        daily_cond = df_osmo.groupby('day_index')['conductivite_permeat'].mean()
        
        flow_start = daily_flow.get(5, 0)
        flow_end = daily_flow.get(25, 0)
        
        log(f"Avg Flow Day 5: {flow_start:.2f}")
        log(f"Avg Flow Day 25: {flow_end:.2f}")
        
        if flow_start > flow_end * 1.1: # Expect >10% drop
            log("✅ SUCCESS: Flow rate drop detected.")
        else:
            log("❌ FAILURE: Flow rate drop NOT detected.")
            
        cond_start = daily_cond.get(5, 0)
        cond_end = daily_cond.get(25, 0)
        log(f"Avg Cond Day 5: {cond_start:.2f}")
        log(f"Avg Cond Day 25: {cond_end:.2f}")

        if cond_end > cond_start * 1.2: # Expect >20% rise
            log("✅ SUCCESS: Conductivity rise detected.")
        else:
            log("❌ FAILURE: Conductivity rise NOT detected.")

if __name__ == "__main__":
    verify_scenarios()

