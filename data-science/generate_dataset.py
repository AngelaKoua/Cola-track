"""
=============================================================================
  INDUSTRIAL IoT SYNTHETIC DATASET GENERATOR
  Coca-Cola Bottling Plant Simulation
  Machines: 1 Osmoseur + 1 Remplisseuse
  Duration: 6 months @ 5-minute intervals
=============================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import truncnorm
import random
import os

# ─── Reproducibility ────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ─── Constants ──────────────────────────────────────────────────────────────
START_DATE = datetime(2026, 1, 1, 0, 0, 0)
DURATION_DAYS = 183  # ~6 months
INTERVAL_MINUTES = 5
TOTAL_STEPS = (DURATION_DAYS * 24 * 60) // INTERVAL_MINUTES  # 52,704
INCIDENTS_PER_MONTH_RANGE = (2, 6)

OSMOSEUR_ID = "OSM-001"
REMPLISSEUSE_ID = "RMP-001"

# ─── Incident definitions ──────────────────────────────────────────────────
OSMOSEUR_INCIDENTS = [
    {"type": "membrane_fouling",   "affected": ["pression_membrane_bar", "conductivite_permeat_uscm", "debit_permeat_lh"], "drift_dir": [1, 1, -1]},
    {"type": "pompe_defaillante",  "affected": ["pression_membrane_bar", "debit_permeat_lh", "debit_concentrat_lh"],      "drift_dir": [-1, -1, -1]},
    {"type": "contamination_eau",  "affected": ["conductivite_permeat_uscm", "turbidite_ntu", "tds_ppm"],                 "drift_dir": [1, 1, 1]},
    {"type": "capteur_defectueux", "affected": ["conductivite_permeat_uscm", "ph_sortie"],                                "drift_dir": [1, 1]},
]

REMPLISSEUSE_INCIDENTS = [
    {"type": "panne_moteur",       "affected": ["vibrations_moteur_mms", "mtbf_h"],                                       "drift_dir": [1, -1]},
    {"type": "desalignement",      "affected": ["vibrations_moteur_mms", "volume_remplissage_l"],                          "drift_dir": [1, -1]},
    {"type": "sous_remplissage",   "affected": ["volume_remplissage_l", "vibrations_moteur_mms"],                          "drift_dir": [-1, 1]},
    {"type": "fuite_air",          "affected": ["conso_air_co_m3h", "carbonation_co_gl"],                                  "drift_dir": [1, -1]},
    {"type": "blocage_convoyeur",  "affected": ["vibrations_moteur_mms", "unites_produites"],                              "drift_dir": [1, -1]},
]


# ─── Utility functions ─────────────────────────────────────────────────────

def trunc_normal(mean, std, low, high, size=1):
    """Sample from a truncated normal distribution."""
    a, b = (low - mean) / std, (high - mean) / std
    return truncnorm.rvs(a, b, loc=mean, scale=std, size=size)


def get_shift(hour):
    """Determine work shift from hour."""
    if 6 <= hour < 14:
        return "matin"
    elif 14 <= hour < 22:
        return "apres-midi"
    else:
        return "nuit"


def seasonal_temperature(step, total_steps):
    """Simulate ambient temperature with daily + seasonal cycles."""
    day_frac = (step % 288) / 288.0  # 288 = steps per day
    season_frac = step / total_steps
    daily = 5 * np.sin(2 * np.pi * (day_frac - 0.25))       # peak at ~14h
    seasonal = 8 * np.sin(2 * np.pi * (season_frac - 0.1))   # warmer mid-year
    return 20 + daily + seasonal + np.random.normal(0, 0.5)


def seasonal_humidity(temp):
    """Humidity inversely correlated with temperature."""
    return np.clip(70 - 0.8 * (temp - 15) + np.random.normal(0, 3), 30, 95)


# ─── Incident Scheduler ────────────────────────────────────────────────────

def schedule_incidents(total_steps, incidents_defs, machine_id, machine_type):
    """Schedule 2-6 incidents per month across the simulation period."""
    incidents = []
    steps_per_month = (30 * 24 * 60) // INTERVAL_MINUTES  # ~8640
    num_months = DURATION_DAYS // 30

    for month in range(num_months):
        n_incidents = random.randint(*INCIDENTS_PER_MONTH_RANGE)
        month_start = month * steps_per_month
        month_end = min((month + 1) * steps_per_month, total_steps)

        for _ in range(n_incidents):
            inc_def = random.choice(incidents_defs)
            severity = random.randint(1, 5)
            downtime_hours = round(severity * random.uniform(0.5, 1.5), 1)
            # Pre-incident drift window: 24-72h before → 288-864 steps
            drift_steps = random.randint(288, 864)
            incident_step = random.randint(month_start + drift_steps + 50, max(month_end - 50, month_start + drift_steps + 51))

            if incident_step < total_steps:
                incidents.append({
                    "step": incident_step,
                    "drift_start": incident_step - drift_steps,
                    "type": inc_def["type"],
                    "affected": inc_def["affected"],
                    "drift_dir": inc_def["drift_dir"],
                    "severity": severity,
                    "downtime_hours": downtime_hours,
                    "machine_id": machine_id,
                    "machine_type": machine_type,
                    "drift_steps": drift_steps,
                })

    incidents.sort(key=lambda x: x["step"])
    return incidents


# ─── Drift & Recovery Engine ───────────────────────────────────────────────

def compute_drift_multiplier(step, incidents, col_name):
    """
    For a given step and column, return the drift multiplier.
    Drift ramps up linearly during drift window, spikes at incident,
    then decays exponentially during recovery.
    """
    drift = 0.0
    for inc in incidents:
        if col_name not in inc["affected"]:
            continue
        idx = inc["affected"].index(col_name)
        direction = inc["drift_dir"][idx]
        severity_factor = inc["severity"] / 5.0

        drift_start = inc["drift_start"]
        incident_step = inc["step"]
        drift_steps = inc["drift_steps"]
        recovery_steps = int(inc["downtime_hours"] * 12 + 100)  # recovery window

        if drift_start <= step < incident_step:
            # Linear ramp-up during drift window
            progress = (step - drift_start) / drift_steps
            drift += direction * severity_factor * progress * 0.6

        elif incident_step <= step < incident_step + recovery_steps:
            # Exponential decay after incident (post-maintenance)
            elapsed = step - incident_step
            drift += direction * severity_factor * 0.6 * np.exp(-elapsed / (recovery_steps * 0.3))

    return drift


# ─── OSMOSEUR Generator ────────────────────────────────────────────────────

def generate_osmoseur(total_steps, timestamps):
    """Generate all osmoseur sensor columns."""
    print("  [OSM-001] Generating osmoseur data...")
    incidents = schedule_incidents(total_steps, OSMOSEUR_INCIDENTS, OSMOSEUR_ID, "osmoseur")

    # Base values
    data = {
        "debit_permeat_lh":        np.zeros(total_steps),
        "debit_concentrat_lh":     np.zeros(total_steps),
        "conductivite_permeat_uscm": np.zeros(total_steps),
        "ph_entree":               np.zeros(total_steps),
        "ph_sortie":               np.zeros(total_steps),
        "turbidite_ntu":           np.zeros(total_steps),
        "chlore_libre_mgl":        np.zeros(total_steps),
        "durete_totale_f":         np.zeros(total_steps),
        "tds_ppm":                 np.zeros(total_steps),
        "pression_membrane_bar":   np.zeros(total_steps),
        "temperature_eau_c":       np.zeros(total_steps),
    }

    # Slow global drift (membrane aging)
    global_aging = np.linspace(0, 0.15, total_steps)

    for i in range(total_steps):
        hour = timestamps[i].hour
        shift_factor = 1.0 if 6 <= hour < 22 else 0.7  # lower at night

        # Pression membrane (base)
        pression_base = 12.0 + global_aging[i] * 10
        pression_drift = compute_drift_multiplier(i, incidents, "pression_membrane_bar")
        pression = pression_base + pression_drift * 6 + np.random.normal(0, 0.15)
        data["pression_membrane_bar"][i] = np.clip(pression, 6, 22)

        # Débit perméat — inversely correlated with pression above normal
        pression_excess = max(0, data["pression_membrane_bar"][i] - 14)
        debit_base = 1150 * shift_factor - pression_excess * 40
        debit_drift = compute_drift_multiplier(i, incidents, "debit_permeat_lh")
        debit = debit_base + debit_drift * 300 + np.random.normal(0, 15)
        data["debit_permeat_lh"][i] = np.clip(debit, 400, 1800)

        # Débit concentrat
        concentrat_base = 400 * shift_factor
        concentrat_drift = compute_drift_multiplier(i, incidents, "debit_concentrat_lh")
        concentrat = concentrat_base + concentrat_drift * 150 + np.random.normal(0, 10)
        data["debit_concentrat_lh"][i] = np.clip(concentrat, 100, 800)

        # Conductivité perméat
        cond_base = 20 + global_aging[i] * 80
        cond_drift = compute_drift_multiplier(i, incidents, "conductivite_permeat_uscm")
        cond = cond_base + cond_drift * 40 + np.random.normal(0, 1.5)
        data["conductivite_permeat_uscm"][i] = np.clip(cond, 2, 120)

        # pH entrée / sortie
        data["ph_entree"][i] = np.clip(7.0 + np.random.normal(0, 0.15), 6.3, 7.7)
        ph_drift = compute_drift_multiplier(i, incidents, "ph_sortie")
        data["ph_sortie"][i] = np.clip(7.0 + ph_drift * 0.4 + np.random.normal(0, 0.08), 6.5, 7.8)

        # Turbidité
        turb_base = 0.15 + global_aging[i] * 0.3
        turb_drift = compute_drift_multiplier(i, incidents, "turbidite_ntu")
        turb = turb_base + turb_drift * 0.8 + np.random.normal(0, 0.02)
        data["turbidite_ntu"][i] = np.clip(turb, 0.01, 3.0)

        # Chlore libre
        data["chlore_libre_mgl"][i] = np.clip(0.15 + np.random.normal(0, 0.05), 0, 0.6)

        # Dureté totale
        data["durete_totale_f"][i] = np.clip(12 + global_aging[i] * 10 + np.random.normal(0, 1.0), 3, 35)

        # TDS
        tds_drift = compute_drift_multiplier(i, incidents, "tds_ppm")
        data["tds_ppm"][i] = np.clip(200 + global_aging[i] * 200 + tds_drift * 150 + np.random.normal(0, 10), 30, 800)

        # Température eau (correlated with ambient)
        data["temperature_eau_c"][i] = np.clip(18 + np.random.normal(0, 1.5), 8, 35)

    return data, incidents


# ─── REMPLISSEUSE Generator ────────────────────────────────────────────────

def generate_remplisseuse(total_steps, timestamps):
    """Generate all remplisseuse sensor columns."""
    print("  [RMP-001] Generating remplisseuse data...")
    incidents = schedule_incidents(total_steps, REMPLISSEUSE_INCIDENTS, REMPLISSEUSE_ID, "remplisseuse")

    data = {
        "temperature_remplissage_c": np.zeros(total_steps),
        "volume_remplissage_l":      np.zeros(total_steps),
        "carbonation_co_gl":         np.zeros(total_steps),
        "unites_produites":          np.zeros(total_steps),
        "heures_arret_h":            np.zeros(total_steps),
        "mtbf_h":                    np.zeros(total_steps),
        "conso_air_co_m3h":          np.zeros(total_steps),
        "vibrations_moteur_mms":     np.zeros(total_steps),
    }

    # Slow global wear
    global_wear = np.linspace(0, 0.2, total_steps)

    for i in range(total_steps):
        hour = timestamps[i].hour
        shift_factor = 1.0 if 6 <= hour < 22 else 0.6

        # Vibrations moteur
        vib_base = 1.8 + global_wear[i] * 3
        vib_drift = compute_drift_multiplier(i, incidents, "vibrations_moteur_mms")
        vib = vib_base + vib_drift * 4 + np.random.normal(0, 0.1)
        data["vibrations_moteur_mms"][i] = np.clip(vib, 0.2, 12)

        # MTBF — inversely correlated with vibrations
        vib_val = data["vibrations_moteur_mms"][i]
        mtbf_base = 150 - global_wear[i] * 100 - max(0, vib_val - 3) * 15
        mtbf_drift = compute_drift_multiplier(i, incidents, "mtbf_h")
        mtbf = mtbf_base + mtbf_drift * 50 + np.random.normal(0, 3)
        data["mtbf_h"][i] = np.clip(mtbf, 5, 250)

        # Volume remplissage
        vol_base = 0.500
        vol_drift = compute_drift_multiplier(i, incidents, "volume_remplissage_l")
        vol = vol_base + vol_drift * 0.02 + global_wear[i] * (-0.005) + np.random.normal(0, 0.002)
        data["volume_remplissage_l"][i] = round(np.clip(vol, 0.44, 0.56), 4)

        # Température remplissage
        temp_base = 4.5
        temp = temp_base + np.random.normal(0, 0.5) + (0.5 if hour >= 12 and hour <= 16 else 0)
        data["temperature_remplissage_c"][i] = np.clip(temp, 1, 10)

        # Carbonation CO2 — affected by temperature
        temp_val = data["temperature_remplissage_c"][i]
        carb_base = 6.5 - max(0, temp_val - 5) * 0.2
        carb_drift = compute_drift_multiplier(i, incidents, "carbonation_co_gl")
        carb = carb_base + carb_drift * 1.5 + np.random.normal(0, 0.15)
        data["carbonation_co_gl"][i] = np.clip(carb, 3, 10)

        # Unités produites (per 5-min interval → normalize from daily)
        # Daily range 25000-32000 → per 5 min = daily/288
        prod_base = 28000 * shift_factor / 288
        prod_drift = compute_drift_multiplier(i, incidents, "unites_produites")
        prod = prod_base + prod_drift * 15 + np.random.normal(0, 2)
        data["unites_produites"][i] = max(0, round(prod))

        # Heures arrêt (accumulated per 5-min window → small increments)
        arret_base = 0.0
        # Check if in downtime window after any incident
        for inc in incidents:
            dt_steps = int(inc["downtime_hours"] * 12)  # 12 steps per hour
            if inc["step"] <= i < inc["step"] + dt_steps:
                arret_base = INTERVAL_MINUTES / 60.0
                break
        data["heures_arret_h"][i] = round(arret_base, 4)

        # Consommation air comprimé
        air_base = 90 * shift_factor
        air_drift = compute_drift_multiplier(i, incidents, "conso_air_co_m3h")
        air = air_base + air_drift * 40 + np.random.normal(0, 3)
        data["conso_air_co_m3h"][i] = np.clip(air, 20, 220)

    return data, incidents


# ─── AI-Ready Columns ──────────────────────────────────────────────────────

def compute_ai_columns(df, all_incidents, total_steps, timestamps):
    """Compute anomaly_score, health_index, failure windows, etc."""
    print("  Computing AI-ready columns...")

    anomaly_score = np.zeros(total_steps)
    health_index = np.full(total_steps, 95.0)
    failure_24h = np.zeros(total_steps, dtype=int)
    failure_72h = np.zeros(total_steps, dtype=int)
    quality_risk = np.zeros(total_steps)
    maintenance_needed = np.zeros(total_steps, dtype=int)

    for inc in all_incidents:
        step = inc["step"]
        drift_start = inc["drift_start"]
        severity = inc["severity"]
        drift_steps = inc["drift_steps"]

        # failure_within_24h: 288 steps = 24h
        for s in range(max(0, step - 288), step):
            failure_24h[s] = 1

        # failure_within_72h: 864 steps = 72h
        for s in range(max(0, step - 864), step):
            failure_72h[s] = 1

        # anomaly_score ramps up during drift
        for s in range(max(0, drift_start), min(step, total_steps)):
            progress = (s - drift_start) / max(drift_steps, 1)
            score = progress * (severity / 5.0) * 0.9
            anomaly_score[s] = max(anomaly_score[s], score)

        # Spike at incident
        spike_range = range(step, min(step + 36, total_steps))  # 3h spike
        for s in spike_range:
            anomaly_score[s] = max(anomaly_score[s], 0.85 + severity * 0.03)

        # Health index drop
        health_drop = severity * 8
        recovery_steps = int(inc["downtime_hours"] * 12 + 200)
        for s in range(max(0, drift_start), min(step + recovery_steps, total_steps)):
            if s < step:
                progress = (s - drift_start) / max(drift_steps, 1)
                health_index[s] = min(health_index[s], 95 - health_drop * progress)
            else:
                elapsed = s - step
                remaining = health_drop * np.exp(-elapsed / (recovery_steps * 0.4))
                health_index[s] = min(health_index[s], 95 - remaining)

        # maintenance_needed: flag during drift period
        for s in range(max(0, drift_start + drift_steps // 2), min(step + 10, total_steps)):
            maintenance_needed[s] = 1

    # Add baseline noise
    anomaly_score += np.random.uniform(0, 0.05, total_steps)
    anomaly_score = np.clip(anomaly_score, 0, 1)

    health_index += np.random.normal(0, 1.0, total_steps)
    health_index = np.clip(health_index, 0, 100)

    # Quality risk based on anomaly score + some sensor deviation
    quality_risk = anomaly_score * 0.7 + np.random.uniform(0, 0.1, total_steps)
    quality_risk = np.clip(quality_risk, 0, 1)

    return {
        "anomaly_score": np.round(anomaly_score, 4),
        "health_index": np.round(health_index, 2),
        "failure_within_24h": failure_24h,
        "failure_within_72h": failure_72h,
        "quality_risk_score": np.round(quality_risk, 4),
        "maintenance_needed": maintenance_needed,
    }


# ─── Incidents CSV Builder ─────────────────────────────────────────────────

def build_incidents_df(all_incidents, timestamps):
    """Build the incidents DataFrame."""
    rows = []
    for idx, inc in enumerate(all_incidents):
        rows.append({
            "incident_id": f"INC-{idx+1:04d}",
            "timestamp": timestamps[min(inc["step"], len(timestamps)-1)].strftime("%Y-%m-%dT%H:%M:%S"),
            "machine_id": inc["machine_id"],
            "machine_type": inc["machine_type"],
            "incident_type": inc["type"],
            "severity": inc["severity"],
            "downtime_hours": inc["downtime_hours"],
            "root_cause": inc["type"].replace("_", " ").title(),
        })
    return pd.DataFrame(rows)


# ─── Main Generator ────────────────────────────────────────────────────────

def generate_industrial_dataset():
    """
    Generate the complete industrial IoT dataset.
    Returns: (timeseries_df, incidents_df)
    """
    print("=" * 70)
    print("  INDUSTRIAL IoT DATASET GENERATOR")
    print("  Coca-Cola Bottling Plant Simulation")
    print("=" * 70)

    # ── Timestamps ──────────────────────────────────────────────────────
    print(f"\n▶ Generating {TOTAL_STEPS:,} timestamps ({DURATION_DAYS} days @ {INTERVAL_MINUTES}min)...")
    timestamps = [START_DATE + timedelta(minutes=INTERVAL_MINUTES * i) for i in range(TOTAL_STEPS)]

    # ── Common columns ──────────────────────────────────────────────────
    print("▶ Computing ambient environment...")
    ambient_temp = np.array([seasonal_temperature(i, TOTAL_STEPS) for i in range(TOTAL_STEPS)])
    ambient_hum = np.array([seasonal_humidity(t) for t in ambient_temp])
    shifts = [get_shift(ts.hour) for ts in timestamps]
    production_days = [(ts - START_DATE).days + 1 for ts in timestamps]

    # ── Osmoseur ────────────────────────────────────────────────────────
    print("▶ Simulating Osmoseur (OSM-001)...")
    osm_data, osm_incidents = generate_osmoseur(TOTAL_STEPS, timestamps)

    osm_rows = {
        "timestamp": [ts.strftime("%Y-%m-%dT%H:%M:%S") for ts in timestamps],
        "machine_id": [OSMOSEUR_ID] * TOTAL_STEPS,
        "machine_type": ["osmoseur"] * TOTAL_STEPS,
        "shift": shifts,
        "production_day": production_days,
        "ambient_temperature": np.round(ambient_temp, 2),
        "ambient_humidity": np.round(ambient_hum, 2),
    }
    osm_rows.update({k: np.round(v, 4) for k, v in osm_data.items()})

    # Remplisseuse columns set to NaN for osmoseur rows
    for col in ["temperature_remplissage_c", "volume_remplissage_l", "carbonation_co_gl",
                "unites_produites", "heures_arret_h", "mtbf_h", "conso_air_co_m3h", "vibrations_moteur_mms"]:
        osm_rows[col] = [np.nan] * TOTAL_STEPS

    # ── Remplisseuse ────────────────────────────────────────────────────
    print("▶ Simulating Remplisseuse (RMP-001)...")
    rmp_data, rmp_incidents = generate_remplisseuse(TOTAL_STEPS, timestamps)

    rmp_rows = {
        "timestamp": [ts.strftime("%Y-%m-%dT%H:%M:%S") for ts in timestamps],
        "machine_id": [REMPLISSEUSE_ID] * TOTAL_STEPS,
        "machine_type": ["remplisseuse"] * TOTAL_STEPS,
        "shift": shifts,
        "production_day": production_days,
        "ambient_temperature": np.round(ambient_temp, 2),
        "ambient_humidity": np.round(ambient_hum, 2),
    }
    # Osmoseur columns set to NaN for remplisseuse rows
    for col in ["debit_permeat_lh", "debit_concentrat_lh", "conductivite_permeat_uscm",
                "ph_entree", "ph_sortie", "turbidite_ntu", "chlore_libre_mgl",
                "durete_totale_f", "tds_ppm", "pression_membrane_bar", "temperature_eau_c"]:
        rmp_rows[col] = [np.nan] * TOTAL_STEPS
    rmp_rows.update({k: np.round(v, 4) for k, v in rmp_data.items()})

    # ── Combine ─────────────────────────────────────────────────────────
    print("▶ Combining datasets...")
    osm_df = pd.DataFrame(osm_rows)
    rmp_df = pd.DataFrame(rmp_rows)

    # Ensure same column order
    all_cols = list(osm_df.columns)
    for c in rmp_df.columns:
        if c not in all_cols:
            all_cols.append(c)
    osm_df = osm_df.reindex(columns=all_cols)
    rmp_df = rmp_df.reindex(columns=all_cols)

    timeseries_df = pd.concat([osm_df, rmp_df], ignore_index=True)
    timeseries_df.sort_values("timestamp", inplace=True)
    timeseries_df.reset_index(drop=True, inplace=True)

    # ── AI Columns ──────────────────────────────────────────────────────
    print("▶ Computing AI-ready columns...")
    all_incidents = osm_incidents + rmp_incidents
    all_incidents.sort(key=lambda x: x["step"])

    # Compute per-machine AI columns then merge
    osm_ai = compute_ai_columns(osm_df, osm_incidents, TOTAL_STEPS, timestamps)
    rmp_ai = compute_ai_columns(rmp_df, rmp_incidents, TOTAL_STEPS, timestamps)

    # Build AI columns aligned to the combined df
    ai_cols = {k: np.zeros(len(timeseries_df)) for k in osm_ai.keys()}
    osm_mask = timeseries_df["machine_type"] == "osmoseur"
    rmp_mask = timeseries_df["machine_type"] == "remplisseuse"

    for k in osm_ai:
        ai_cols[k][osm_mask.values] = osm_ai[k]
        ai_cols[k][rmp_mask.values] = rmp_ai[k]

    for k, v in ai_cols.items():
        timeseries_df[k] = v

    # ── Incidents DataFrame ─────────────────────────────────────────────
    print("▶ Building incidents table...")
    incidents_df = build_incidents_df(all_incidents, timestamps)

    # ── Summary ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"  ✅ GENERATION COMPLETE")
    print(f"  Timeseries rows  : {len(timeseries_df):,}")
    print(f"  Incidents count  : {len(incidents_df):,}")
    print(f"  Columns          : {len(timeseries_df.columns)}")
    print(f"  Date range       : {timeseries_df['timestamp'].iloc[0]} → {timeseries_df['timestamp'].iloc[-1]}")
    print(f"  Machines         : {timeseries_df['machine_id'].unique().tolist()}")
    print(f"{'=' * 70}")

    return timeseries_df, incidents_df


# ─── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    timeseries_df, incidents_df = generate_industrial_dataset()

    # Save to CSV
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    ts_path = os.path.join(output_dir, "industrial_iot_timeseries.csv")
    inc_path = os.path.join(output_dir, "industrial_incidents.csv")

    print(f"\n▶ Saving to {ts_path}...")
    timeseries_df.to_csv(ts_path, index=False, sep=',')
    print(f"▶ Saving to {inc_path}...")
    incidents_df.to_csv(inc_path, index=False, sep=',')

    print("\n🏁 Done! Files saved successfully.")
    print(f"   📄 {ts_path}  ({os.path.getsize(ts_path) / 1024 / 1024:.1f} MB)")
    print(f"   📄 {inc_path}  ({os.path.getsize(inc_path) / 1024:.1f} KB)")
