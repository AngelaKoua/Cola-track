"""
=============================================================================
  EXPLORATORY DATA ANALYSIS (EDA)
  Industrial IoT Dataset — Coca-Cola Bottling Plant
  Reads ./data/ and generates all charts into ./outputs/eda/
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ─── Config ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs" / "eda"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="darkgrid", palette="deep")
plt.rcParams.update({
    "figure.figsize": (14, 6),
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.3,
})

COLORS = {
    "osmoseur": "#1f77b4",
    "remplisseuse": "#2ca02c",
    "incident": "#d62728",
    "warning": "#ff7f0e",
    "ok": "#2ca02c",
}


def load_data():
    """Load timeseries and incidents CSVs."""
    print("▶ Loading data...")
    ts = pd.read_csv(DATA_DIR / "industrial_iot_timeseries.csv", parse_dates=["timestamp"])
    inc = pd.read_csv(DATA_DIR / "industrial_incidents.csv", parse_dates=["timestamp"])
    print(f"  Timeseries: {len(ts):,} rows × {len(ts.columns)} columns")
    print(f"  Incidents:  {len(inc):,} records")
    return ts, inc


def save_fig(name):
    """Save current figure."""
    path = OUTPUT_DIR / f"{name}.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✅ Saved: {path}")


# ═══════════════════════════════════════════════════════════════════════════
# 1. OVERVIEW & BASIC STATISTICS
# ═══════════════════════════════════════════════════════════════════════════

def section_overview(ts, inc):
    """Print dataset overview and save stats."""
    print("\n" + "=" * 70)
    print("  1. DATASET OVERVIEW")
    print("=" * 70)

    # Basic info
    print(f"\n  Date range: {ts.timestamp.min()} → {ts.timestamp.max()}")
    print(f"  Duration: {(ts.timestamp.max() - ts.timestamp.min()).days} days")
    print(f"  Machines: {ts.machine_id.unique().tolist()}")
    print(f"  Total rows: {len(ts):,}")

    # Missing values summary
    missing = ts.isnull().sum()
    missing_pct = (missing / len(ts) * 100).round(1)
    missing_df = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
    missing_df = missing_df[missing_df.missing_count > 0].sort_values("missing_pct", ascending=False)
    print(f"\n  Columns with missing values (expected — machine-specific columns):")
    for col, row in missing_df.iterrows():
        print(f"    {col}: {row['missing_pct']}%")

    # Descriptive stats
    osm = ts[ts.machine_type == "osmoseur"]
    rmp = ts[ts.machine_type == "remplisseuse"]

    osm_cols = ["debit_permeat_lh", "debit_concentrat_lh", "conductivite_permeat_uscm",
                "ph_entree", "ph_sortie", "turbidite_ntu", "chlore_libre_mgl",
                "durete_totale_f", "tds_ppm", "pression_membrane_bar", "temperature_eau_c"]

    rmp_cols = ["temperature_remplissage_c", "volume_remplissage_l", "carbonation_co_gl",
                "unites_produites", "heures_arret_h", "mtbf_h", "conso_air_co_m3h",
                "vibrations_moteur_mms"]

    stats_osm = osm[osm_cols].describe().T
    stats_rmp = rmp[rmp_cols].describe().T

    stats_osm.to_csv(OUTPUT_DIR / "stats_osmoseur.csv")
    stats_rmp.to_csv(OUTPUT_DIR / "stats_remplisseuse.csv")
    print(f"\n  ✅ Saved: {OUTPUT_DIR / 'stats_osmoseur.csv'}")
    print(f"  ✅ Saved: {OUTPUT_DIR / 'stats_remplisseuse.csv'}")

    return osm, rmp, osm_cols, rmp_cols


# ═══════════════════════════════════════════════════════════════════════════
# 2. DISTRIBUTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def section_distributions(osm, rmp, osm_cols, rmp_cols):
    """Plot histograms for all sensor columns."""
    print("\n" + "=" * 70)
    print("  2. DISTRIBUTION ANALYSIS")
    print("=" * 70)

    # Osmoseur distributions
    fig, axes = plt.subplots(3, 4, figsize=(20, 14))
    fig.suptitle("OSMOSEUR — Distributions des Capteurs", fontsize=16, fontweight="bold", y=1.01)
    axes = axes.flatten()
    for i, col in enumerate(osm_cols):
        ax = axes[i]
        data = osm[col].dropna()
        ax.hist(data, bins=60, color=COLORS["osmoseur"], alpha=0.7, edgecolor="white", linewidth=0.5)
        ax.set_title(col.replace("_", " ").title(), fontsize=10)
        ax.axvline(data.mean(), color="red", linestyle="--", linewidth=1, label=f"μ={data.mean():.1f}")
        ax.legend(fontsize=8)
    # Hide extra subplot
    axes[-1].set_visible(False)
    plt.tight_layout()
    save_fig("02a_osmoseur_distributions")

    # Remplisseuse distributions
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle("REMPLISSEUSE — Distributions des Capteurs", fontsize=16, fontweight="bold", y=1.01)
    axes = axes.flatten()
    for i, col in enumerate(rmp_cols):
        ax = axes[i]
        data = rmp[col].dropna()
        ax.hist(data, bins=60, color=COLORS["remplisseuse"], alpha=0.7, edgecolor="white", linewidth=0.5)
        ax.set_title(col.replace("_", " ").title(), fontsize=10)
        ax.axvline(data.mean(), color="red", linestyle="--", linewidth=1, label=f"μ={data.mean():.1f}")
        ax.legend(fontsize=8)
    plt.tight_layout()
    save_fig("02b_remplisseuse_distributions")


# ═══════════════════════════════════════════════════════════════════════════
# 3. CORRELATION MATRICES
# ═══════════════════════════════════════════════════════════════════════════

def section_correlations(osm, rmp, osm_cols, rmp_cols):
    """Heatmap correlation matrices."""
    print("\n" + "=" * 70)
    print("  3. CORRELATION ANALYSIS")
    print("=" * 70)

    # Osmoseur
    fig, ax = plt.subplots(figsize=(12, 10))
    corr_osm = osm[osm_cols].corr()
    mask = np.triu(np.ones_like(corr_osm, dtype=bool))
    sns.heatmap(corr_osm, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                square=True, linewidths=0.5, ax=ax, vmin=-1, vmax=1,
                cbar_kws={"shrink": 0.8})
    ax.set_title("OSMOSEUR — Matrice de Corrélation", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    save_fig("03a_osmoseur_correlations")

    # Remplisseuse
    fig, ax = plt.subplots(figsize=(10, 8))
    corr_rmp = rmp[rmp_cols].corr()
    mask = np.triu(np.ones_like(corr_rmp, dtype=bool))
    sns.heatmap(corr_rmp, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                square=True, linewidths=0.5, ax=ax, vmin=-1, vmax=1,
                cbar_kws={"shrink": 0.8})
    ax.set_title("REMPLISSEUSE — Matrice de Corrélation", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    save_fig("03b_remplisseuse_correlations")

    # Print key correlations
    print("\n  Key Osmoseur correlations:")
    for c1, c2 in [("pression_membrane_bar", "debit_permeat_lh"),
                    ("conductivite_permeat_uscm", "tds_ppm"),
                    ("turbidite_ntu", "conductivite_permeat_uscm")]:
        if c1 in corr_osm.columns and c2 in corr_osm.columns:
            print(f"    {c1} ↔ {c2}: {corr_osm.loc[c1, c2]:.3f}")

    print("\n  Key Remplisseuse correlations:")
    for c1, c2 in [("vibrations_moteur_mms", "mtbf_h"),
                    ("vibrations_moteur_mms", "conso_air_co_m3h"),
                    ("temperature_remplissage_c", "carbonation_co_gl")]:
        if c1 in corr_rmp.columns and c2 in corr_rmp.columns:
            print(f"    {c1} ↔ {c2}: {corr_rmp.loc[c1, c2]:.3f}")


# ═══════════════════════════════════════════════════════════════════════════
# 4. TIME SERIES TRENDS
# ═══════════════════════════════════════════════════════════════════════════

def section_timeseries(osm, rmp, inc):
    """Plot time series of key sensors with incident markers."""
    print("\n" + "=" * 70)
    print("  4. TIME SERIES TRENDS")
    print("=" * 70)

    osm_inc = inc[inc.machine_type == "osmoseur"]
    rmp_inc = inc[inc.machine_type == "remplisseuse"]

    # -- Osmoseur: Pression + Débit over time (dual axis) --
    fig, ax1 = plt.subplots(figsize=(18, 6))
    # Resample to hourly for cleaner plot
    osm_h = osm.set_index("timestamp").resample("1h").mean(numeric_only=True)

    ax1.plot(osm_h.index, osm_h["pression_membrane_bar"], color="#1f77b4", alpha=0.8, linewidth=0.8, label="Pression (bar)")
    ax1.set_ylabel("Pression Membrane (bar)", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")

    ax2 = ax1.twinx()
    ax2.plot(osm_h.index, osm_h["debit_permeat_lh"], color="#ff7f0e", alpha=0.8, linewidth=0.8, label="Débit (L/h)")
    ax2.set_ylabel("Débit Perméat (L/h)", color="#ff7f0e")
    ax2.tick_params(axis="y", labelcolor="#ff7f0e")

    # Mark incidents
    for _, row in osm_inc.iterrows():
        ax1.axvline(row.timestamp, color="red", alpha=0.5, linestyle="--", linewidth=1)

    ax1.set_title("OSMOSEUR — Pression vs Débit + Incidents", fontsize=14, fontweight="bold")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    fig.autofmt_xdate()
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    save_fig("04a_osmoseur_pression_debit")

    # -- Osmoseur: Conductivité + TDS --
    fig, ax1 = plt.subplots(figsize=(18, 6))
    ax1.plot(osm_h.index, osm_h["conductivite_permeat_uscm"], color="#9467bd", alpha=0.8, linewidth=0.8, label="Conductivité (μS/cm)")
    ax1.set_ylabel("Conductivité (μS/cm)", color="#9467bd")
    ax2 = ax1.twinx()
    ax2.plot(osm_h.index, osm_h["tds_ppm"], color="#8c564b", alpha=0.8, linewidth=0.8, label="TDS (ppm)")
    ax2.set_ylabel("TDS (ppm)", color="#8c564b")
    for _, row in osm_inc.iterrows():
        ax1.axvline(row.timestamp, color="red", alpha=0.5, linestyle="--", linewidth=1)
    ax1.set_title("OSMOSEUR — Conductivité & TDS (dérive progressive)", fontsize=14, fontweight="bold")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    fig.autofmt_xdate()
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    save_fig("04b_osmoseur_conductivite_tds")

    # -- Remplisseuse: Vibrations + MTBF --
    fig, ax1 = plt.subplots(figsize=(18, 6))
    rmp_h = rmp.set_index("timestamp").resample("1h").mean(numeric_only=True)

    ax1.plot(rmp_h.index, rmp_h["vibrations_moteur_mms"], color="#2ca02c", alpha=0.8, linewidth=0.8, label="Vibrations (mm/s)")
    ax1.set_ylabel("Vibrations (mm/s)", color="#2ca02c")
    ax1.tick_params(axis="y", labelcolor="#2ca02c")

    ax2 = ax1.twinx()
    ax2.plot(rmp_h.index, rmp_h["mtbf_h"], color="#d62728", alpha=0.8, linewidth=0.8, label="MTBF (h)")
    ax2.set_ylabel("MTBF (h)", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")

    for _, row in rmp_inc.iterrows():
        ax1.axvline(row.timestamp, color="red", alpha=0.5, linestyle="--", linewidth=1)

    ax1.set_title("REMPLISSEUSE — Vibrations vs MTBF + Incidents", fontsize=14, fontweight="bold")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    fig.autofmt_xdate()
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    save_fig("04c_remplisseuse_vibrations_mtbf")

    # -- Remplisseuse: Volume remplissage --
    fig, ax = plt.subplots(figsize=(18, 5))
    ax.plot(rmp_h.index, rmp_h["volume_remplissage_l"], color="#17becf", alpha=0.8, linewidth=0.8)
    ax.axhline(0.50, color="green", linestyle="--", alpha=0.5, label="Target 0.50 L")
    ax.axhline(0.49, color="orange", linestyle=":", alpha=0.5, label="Lower spec")
    ax.axhline(0.51, color="orange", linestyle=":", alpha=0.5, label="Upper spec")
    for _, row in rmp_inc.iterrows():
        ax.axvline(row.timestamp, color="red", alpha=0.4, linestyle="--", linewidth=1)
    ax.set_title("REMPLISSEUSE — Volume de Remplissage", fontsize=14, fontweight="bold")
    ax.set_ylabel("Volume (L)")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate()
    plt.tight_layout()
    save_fig("04d_remplisseuse_volume")

    return osm_h, rmp_h


# ═══════════════════════════════════════════════════════════════════════════
# 5. INCIDENT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def section_incidents(inc):
    """Analyze incident distribution."""
    print("\n" + "=" * 70)
    print("  5. INCIDENT ANALYSIS")
    print("=" * 70)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("ANALYSE DES INCIDENTS", fontsize=16, fontweight="bold", y=1.01)

    # 5a. Incidents by type
    ax = axes[0, 0]
    type_counts = inc.incident_type.value_counts()
    bars = ax.barh(type_counts.index, type_counts.values, color=sns.color_palette("Set2", len(type_counts)))
    ax.set_title("Incidents par Type")
    ax.set_xlabel("Nombre")
    for bar, val in zip(bars, type_counts.values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, str(val),
                va="center", fontsize=10, fontweight="bold")

    # 5b. Severity distribution
    ax = axes[0, 1]
    sev_counts = inc.severity.value_counts().sort_index()
    colors_sev = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c", "#8e44ad"]
    ax.bar(sev_counts.index, sev_counts.values, color=colors_sev, edgecolor="white", linewidth=1.5)
    ax.set_title("Distribution de la Sévérité")
    ax.set_xlabel("Niveau de Sévérité")
    ax.set_ylabel("Nombre")
    ax.set_xticks([1, 2, 3, 4, 5])

    # 5c. Downtime by machine
    ax = axes[1, 0]
    dt_by_machine = inc.groupby("machine_type")["downtime_hours"].sum()
    ax.pie(dt_by_machine.values, labels=dt_by_machine.index,
           autopct="%1.1f%%", colors=[COLORS["osmoseur"], COLORS["remplisseuse"]],
           startangle=90, textprops={"fontsize": 12})
    ax.set_title("Downtime Total par Machine")

    # 5d. Downtime vs Severity scatter
    ax = axes[1, 1]
    for mt in inc.machine_type.unique():
        subset = inc[inc.machine_type == mt]
        ax.scatter(subset.severity, subset.downtime_hours, s=80, alpha=0.7,
                   color=COLORS[mt], label=mt, edgecolors="white", linewidth=0.5)
    ax.set_title("Downtime vs Sévérité")
    ax.set_xlabel("Sévérité")
    ax.set_ylabel("Downtime (h)")
    ax.legend()

    plt.tight_layout()
    save_fig("05_incident_analysis")

    # Incidents timeline
    fig, ax = plt.subplots(figsize=(18, 5))
    for mt in inc.machine_type.unique():
        subset = inc[inc.machine_type == mt]
        ax.scatter(subset.timestamp, subset.severity, s=subset.downtime_hours * 30 + 20,
                   alpha=0.7, color=COLORS[mt], label=mt, edgecolors="black", linewidth=0.5)
    ax.set_title("CHRONOLOGIE DES INCIDENTS (taille = downtime)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Sévérité")
    ax.set_xlabel("Date")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate()
    plt.tight_layout()
    save_fig("05b_incidents_timeline")


# ═══════════════════════════════════════════════════════════════════════════
# 6. AI-READY COLUMNS ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def section_ai_columns(ts, inc):
    """Analyze AI-ready prediction columns."""
    print("\n" + "=" * 70)
    print("  6. AI-READY COLUMNS")
    print("=" * 70)

    fig, axes = plt.subplots(3, 2, figsize=(18, 16))
    fig.suptitle("COLONNES AI — Distributions & Patterns", fontsize=16, fontweight="bold", y=1.01)

    ai_cols = ["anomaly_score", "health_index", "failure_within_24h",
               "failure_within_72h", "quality_risk_score", "maintenance_needed"]

    for i, col in enumerate(ai_cols):
        ax = axes[i // 2, i % 2]
        data = ts[col].dropna()

        if col in ["failure_within_24h", "failure_within_72h", "maintenance_needed"]:
            # Binary columns — bar chart
            counts = data.value_counts().sort_index()
            colors_bin = ["#2ecc71", "#e74c3c"]
            ax.bar(counts.index.astype(str), counts.values, color=colors_bin[:len(counts)],
                   edgecolor="white", linewidth=1.5)
            ax.set_title(col.replace("_", " ").title())
            for j, v in enumerate(counts.values):
                pct = v / len(data) * 100
                ax.text(j, v + 100, f"{pct:.1f}%", ha="center", fontsize=11, fontweight="bold")
        else:
            # Continuous — histogram
            ax.hist(data, bins=60, color="#3498db", alpha=0.7, edgecolor="white")
            ax.set_title(col.replace("_", " ").title())
            ax.axvline(data.mean(), color="red", linestyle="--", label=f"μ={data.mean():.2f}")
            ax.legend()

    plt.tight_layout()
    save_fig("06_ai_columns_distributions")

    # Health Index & Anomaly Score over time
    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)

    for mt in ["osmoseur", "remplisseuse"]:
        sub = ts[ts.machine_type == mt].set_index("timestamp").resample("1h").mean(numeric_only=True)
        axes[0].plot(sub.index, sub["health_index"], alpha=0.7, linewidth=0.8,
                     color=COLORS[mt], label=mt)
        axes[1].plot(sub.index, sub["anomaly_score"], alpha=0.7, linewidth=0.8,
                     color=COLORS[mt], label=mt)

    # Mark incidents
    for _, row in inc.iterrows():
        axes[0].axvline(row.timestamp, color="red", alpha=0.3, linestyle="--", linewidth=0.8)
        axes[1].axvline(row.timestamp, color="red", alpha=0.3, linestyle="--", linewidth=0.8)

    axes[0].set_title("HEALTH INDEX — Évolution Temporelle", fontsize=14, fontweight="bold")
    axes[0].set_ylabel("Health Index (0-100)")
    axes[0].legend()
    axes[1].set_title("ANOMALY SCORE — Évolution Temporelle", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("Anomaly Score (0-1)")
    axes[1].legend()
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate()
    plt.tight_layout()
    save_fig("06b_health_anomaly_timeline")

    # Class balance
    print("\n  Class balance:")
    for col in ["failure_within_24h", "failure_within_72h", "maintenance_needed"]:
        pos = (ts[col] == 1).sum()
        neg = (ts[col] == 0).sum()
        print(f"    {col}: {pos:,} positif ({pos / len(ts) * 100:.1f}%) / {neg:,} négatif ({neg / len(ts) * 100:.1f}%)")


# ═══════════════════════════════════════════════════════════════════════════
# 7. SHIFT & SEASONALITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def section_shift_analysis(ts):
    """Analyze patterns by shift and time of day."""
    print("\n" + "=" * 70)
    print("  7. SHIFT & SEASONALITY ANALYSIS")
    print("=" * 70)

    osm = ts[ts.machine_type == "osmoseur"].copy()
    rmp = ts[ts.machine_type == "remplisseuse"].copy()

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("ANALYSE PAR SHIFT & SAISONNALITÉ", fontsize=16, fontweight="bold", y=1.01)

    # 7a. Osmoseur débit by shift
    ax = axes[0, 0]
    shift_order = ["matin", "apres-midi", "nuit"]
    sns.boxplot(data=osm, x="shift", y="debit_permeat_lh", order=shift_order, ax=ax,
                palette=["#f39c12", "#3498db", "#2c3e50"])
    ax.set_title("OSM — Débit Perméat par Shift")

    # 7b. Remplisseuse vibrations by shift
    ax = axes[0, 1]
    sns.boxplot(data=rmp, x="shift", y="vibrations_moteur_mms", order=shift_order, ax=ax,
                palette=["#f39c12", "#3498db", "#2c3e50"])
    ax.set_title("RMP — Vibrations par Shift")

    # 7c. Ambient temperature over time
    ax = axes[1, 0]
    ts_daily = ts.set_index("timestamp").resample("1D")["ambient_temperature"].mean()
    ax.plot(ts_daily.index, ts_daily.values, color="#e74c3c", linewidth=1.5)
    ax.fill_between(ts_daily.index, ts_daily.values, alpha=0.15, color="#e74c3c")
    ax.set_title("Température Ambiante (moyenne journalière)")
    ax.set_ylabel("°C")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # 7d. Production by hour of day (remplisseuse)
    ax = axes[1, 1]
    rmp_copy = rmp.copy()
    rmp_copy["hour"] = rmp_copy.timestamp.dt.hour
    hourly_prod = rmp_copy.groupby("hour")["unites_produites"].mean()
    ax.bar(hourly_prod.index, hourly_prod.values, color="#2ca02c", alpha=0.8, edgecolor="white")
    ax.set_title("RMP — Production Moyenne par Heure")
    ax.set_xlabel("Heure")
    ax.set_ylabel("Unités / 5 min")

    plt.tight_layout()
    save_fig("07_shift_seasonality")


# ═══════════════════════════════════════════════════════════════════════════
# 8. PRE-INCIDENT PATTERN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def section_pre_incident(ts, inc):
    """Analyze sensor behavior before incidents."""
    print("\n" + "=" * 70)
    print("  8. PRE-INCIDENT PATTERN ANALYSIS")
    print("=" * 70)

    # Pick a few representative incidents to plot
    osm_inc = inc[inc.machine_type == "osmoseur"].head(3)
    rmp_inc = inc[inc.machine_type == "remplisseuse"].head(3)

    if len(osm_inc) > 0:
        fig, axes = plt.subplots(len(osm_inc), 2, figsize=(18, 5 * len(osm_inc)))
        if len(osm_inc) == 1:
            axes = axes.reshape(1, -1)
        fig.suptitle("OSMOSEUR — Patterns Pré-Incident (72h avant)", fontsize=16, fontweight="bold", y=1.01)

        osm = ts[ts.machine_type == "osmoseur"].copy().set_index("timestamp")

        for i, (_, row) in enumerate(osm_inc.iterrows()):
            t_inc = row.timestamp
            t_start = t_inc - pd.Timedelta(hours=80)
            t_end = t_inc + pd.Timedelta(hours=12)
            window = osm.loc[t_start:t_end]

            if len(window) == 0:
                continue

            axes[i, 0].plot(window.index, window["pression_membrane_bar"], color="#1f77b4", linewidth=1)
            axes[i, 0].axvline(t_inc, color="red", linewidth=2, linestyle="--", label="INCIDENT")
            axes[i, 0].set_title(f"Pression — [{row.incident_type}] sév.{row.severity}")
            axes[i, 0].legend()

            axes[i, 1].plot(window.index, window["conductivite_permeat_uscm"], color="#9467bd", linewidth=1)
            axes[i, 1].axvline(t_inc, color="red", linewidth=2, linestyle="--", label="INCIDENT")
            axes[i, 1].set_title(f"Conductivité — [{row.incident_type}] sév.{row.severity}")
            axes[i, 1].legend()

        plt.tight_layout()
        save_fig("08a_osmoseur_pre_incident")

    if len(rmp_inc) > 0:
        fig, axes = plt.subplots(len(rmp_inc), 2, figsize=(18, 5 * len(rmp_inc)))
        if len(rmp_inc) == 1:
            axes = axes.reshape(1, -1)
        fig.suptitle("REMPLISSEUSE — Patterns Pré-Incident (72h avant)", fontsize=16, fontweight="bold", y=1.01)

        rmp = ts[ts.machine_type == "remplisseuse"].copy().set_index("timestamp")

        for i, (_, row) in enumerate(rmp_inc.iterrows()):
            t_inc = row.timestamp
            t_start = t_inc - pd.Timedelta(hours=80)
            t_end = t_inc + pd.Timedelta(hours=12)
            window = rmp.loc[t_start:t_end]

            if len(window) == 0:
                continue

            axes[i, 0].plot(window.index, window["vibrations_moteur_mms"], color="#2ca02c", linewidth=1)
            axes[i, 0].axvline(t_inc, color="red", linewidth=2, linestyle="--", label="INCIDENT")
            axes[i, 0].set_title(f"Vibrations — [{row.incident_type}] sév.{row.severity}")
            axes[i, 0].legend()

            axes[i, 1].plot(window.index, window["mtbf_h"], color="#d62728", linewidth=1)
            axes[i, 1].axvline(t_inc, color="red", linewidth=2, linestyle="--", label="INCIDENT")
            axes[i, 1].set_title(f"MTBF — [{row.incident_type}] sév.{row.severity}")
            axes[i, 1].legend()

        plt.tight_layout()
        save_fig("08b_remplisseuse_pre_incident")


# ═══════════════════════════════════════════════════════════════════════════
# 9. KEY SCATTER PLOTS (Industrial correlations)
# ═══════════════════════════════════════════════════════════════════════════

def section_scatter_correlations(osm, rmp):
    """Key industrial correlation scatter plots."""
    print("\n" + "=" * 70)
    print("  9. KEY INDUSTRIAL CORRELATIONS")
    print("=" * 70)

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle("CORRÉLATIONS INDUSTRIELLES CLÉS", fontsize=16, fontweight="bold", y=1.01)

    # OSM: Pression vs Débit
    ax = axes[0, 0]
    sample = osm.sample(min(3000, len(osm)), random_state=42)
    ax.scatter(sample["pression_membrane_bar"], sample["debit_permeat_lh"],
               alpha=0.3, s=5, color=COLORS["osmoseur"])
    ax.set_xlabel("Pression Membrane (bar)")
    ax.set_ylabel("Débit Perméat (L/h)")
    ax.set_title("OSM: Pression → Débit")

    # OSM: Conductivité vs TDS
    ax = axes[0, 1]
    ax.scatter(sample["conductivite_permeat_uscm"], sample["tds_ppm"],
               alpha=0.3, s=5, color="#9467bd")
    ax.set_xlabel("Conductivité (μS/cm)")
    ax.set_ylabel("TDS (ppm)")
    ax.set_title("OSM: Conductivité → TDS")

    # OSM: Turbidité vs Conductivité
    ax = axes[0, 2]
    ax.scatter(sample["turbidite_ntu"], sample["conductivite_permeat_uscm"],
               alpha=0.3, s=5, color="#e67e22")
    ax.set_xlabel("Turbidité (NTU)")
    ax.set_ylabel("Conductivité (μS/cm)")
    ax.set_title("OSM: Turbidité → Conductivité")

    # RMP: Vibrations vs MTBF
    ax = axes[1, 0]
    sample_r = rmp.sample(min(3000, len(rmp)), random_state=42)
    ax.scatter(sample_r["vibrations_moteur_mms"], sample_r["mtbf_h"],
               alpha=0.3, s=5, color=COLORS["remplisseuse"])
    ax.set_xlabel("Vibrations (mm/s)")
    ax.set_ylabel("MTBF (h)")
    ax.set_title("RMP: Vibrations → MTBF")

    # RMP: Temperature vs Carbonation
    ax = axes[1, 1]
    ax.scatter(sample_r["temperature_remplissage_c"], sample_r["carbonation_co_gl"],
               alpha=0.3, s=5, color="#e74c3c")
    ax.set_xlabel("Température (°C)")
    ax.set_ylabel("Carbonation (CO₂ g/L)")
    ax.set_title("RMP: Température → Carbonation")

    # RMP: Vibrations vs Conso Air
    ax = axes[1, 2]
    ax.scatter(sample_r["vibrations_moteur_mms"], sample_r["conso_air_co_m3h"],
               alpha=0.3, s=5, color="#17becf")
    ax.set_xlabel("Vibrations (mm/s)")
    ax.set_ylabel("Conso Air (m³/h)")
    ax.set_title("RMP: Vibrations → Conso Air")

    plt.tight_layout()
    save_fig("09_scatter_correlations")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  EXPLORATORY DATA ANALYSIS — Industrial IoT Dataset")
    print("=" * 70)

    ts, inc = load_data()
    osm, rmp, osm_cols, rmp_cols = section_overview(ts, inc)
    section_distributions(osm, rmp, osm_cols, rmp_cols)
    section_correlations(osm, rmp, osm_cols, rmp_cols)
    section_timeseries(osm, rmp, inc)
    section_incidents(inc)
    section_ai_columns(ts, inc)
    section_shift_analysis(ts)
    section_pre_incident(ts, inc)
    section_scatter_correlations(osm, rmp)

    print("\n" + "=" * 70)
    print(f"  🏁 EDA COMPLETE — All charts saved to: {OUTPUT_DIR.absolute()}")
    print(f"  Total files: {len(list(OUTPUT_DIR.glob('*.png')))}")
    print("=" * 70)


if __name__ == "__main__":
    main()
