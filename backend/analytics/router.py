
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Literal, Optional
from datetime import datetime, timedelta
from app.database import get_db
from analytics.business_rules import (
    calculate_status,
    generate_alerts,
    calculate_trend,
    calculate_change_percentage,
    KPI_RULES
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# ============================================================================
# 0. UNIFIED DASHBOARD OVERVIEW
# ============================================================================

@router.get("/dashboard/overview")
def get_dashboard_overview(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    equipment: str = Query("all", description="Equipment filter: all, osmoseur, remplisseuse"),
    db: Session = Depends(get_db)
):
    """
    Unified dashboard endpoint returning all data in one call.
    
    Returns:
    - KPIs with dynamic status, trends, comparisons
    - Time series data
    - Alerts
    - Technician performance
    - Correlations
    """
    try:
        start_id = int(start_date.replace("-", "") + "00")
        end_id = int(end_date.replace("-", "") + "23")
        
        # Calculate previous period dates for comparison
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        period_days = (end_dt - start_dt).days + 1
        
        prev_end_dt = start_dt - timedelta(days=1)
        prev_start_dt = prev_end_dt - timedelta(days=period_days - 1)
        period_hours = period_days * 24
        
        prev_start_id = int(prev_start_dt.strftime("%Y%m%d") + "00")
        prev_end_id = int(prev_end_dt.strftime("%Y%m%d") + "23")
        
        # --- FETCH CURRENT PERIOD DATA ---
        
        # Determine which data to fetch based on equipment filter
        fetch_osmo = equipment in ["all", "osmoseur"]
        fetch_remp = equipment in ["all", "remplisseuse"]
        
        # Initialize default values
        osmo_current = {"avg_recovery": 0, "avg_conductivity": 0}
        osmo_previous = {"avg_recovery": 0, "avg_conductivity": 0}
        remp_current = {"avg_efficiency": 0, "total_production": 0, "total_downtime": 0}
        remp_previous = {"avg_efficiency": 0, "total_production": 0, "total_downtime": 0}
        
        # Osmoseur current
        if fetch_osmo:
            sql_osmo_current = text("""
                SELECT 
                    AVG(taux_recuperation) as avg_recovery,
                    AVG(conductivite_permeat) as avg_conductivity
                FROM dw.fact_osmoseur_hourly
                WHERE time_id BETWEEN :start AND :end
            """)
            osmo_current = db.execute(sql_osmo_current, {"start": start_id, "end": end_id}).mappings().first()
            
            # Osmoseur previous
            osmo_previous = db.execute(sql_osmo_current, {"start": prev_start_id, "end": prev_end_id}).mappings().first()
        
        # Remplisseuse current
        if fetch_remp:
            sql_remp_current = text("""
                SELECT 
                    AVG(rendement) as avg_efficiency,
                    SUM(unites_conformes) as total_production,
                    SUM(heures_arret) as total_downtime
                FROM dw.fact_remplisseuse_hourly
                WHERE time_id BETWEEN :start AND :end
            """)
            remp_current = db.execute(sql_remp_current, {"start": start_id, "end": end_id}).mappings().first()
            
            # Remplisseuse previous
            remp_previous = db.execute(sql_remp_current, {"start": prev_start_id, "end": prev_end_id}).mappings().first()
        
        # --- BUILD KPI STRUCTURE ---
        
        rendement_val = remp_current.get("avg_efficiency") or 0
        rendement_prev = remp_previous.get("avg_efficiency") or 0
        
        taux_recup_val = osmo_current.get("avg_recovery") or 0
        taux_recup_prev = osmo_previous.get("avg_recovery") or 0
        
        production_val = remp_current.get("total_production") or 0
        production_prev = remp_previous.get("total_production") or 0
        
        arret_val = remp_current.get("total_downtime") or 0
        arret_prev = remp_previous.get("total_downtime") or 0
        
        conductivite_val = osmo_current.get("avg_conductivity") or 0
        conductivite_prev = osmo_previous.get("avg_conductivity") or 0
        
        # Build KPIs based on equipment filter
        kpis = {}
        
        # Remplisseuse KPIs (shown for "all" and "remplisseuse")
        if fetch_remp:
            kpis["rendement_global"] = {
                "value": round(rendement_val, 1),
                "previous": round(rendement_prev, 1),
                "target": KPI_RULES["rendement"]["target"],
                "status": calculate_status(rendement_val, "rendement"),
                "trend": calculate_trend(rendement_val, rendement_prev),
                "change": round(calculate_change_percentage(rendement_val, rendement_prev), 1),
                "unit": "%"
            }
            # Dynamic targets: production target is per hour, temps_arret target is per day
            production_target = KPI_RULES["production"]["target"] * period_hours
            production_warning = KPI_RULES["production"]["warning_threshold"] * period_hours
            production_critical = KPI_RULES["production"]["critical_threshold"] * period_hours
            
            arret_target = KPI_RULES["temps_arret"]["target"] * period_days
            arret_warning = KPI_RULES["temps_arret"]["warning_threshold"] * period_days
            arret_critical = KPI_RULES["temps_arret"]["critical_threshold"] * period_days
            
            # Production status with dynamic thresholds
            if production_val >= production_target:
                production_status = "success"
            elif production_val >= production_warning:
                production_status = "warning"
            else:
                production_status = "danger"
            
            # Downtime status with dynamic thresholds (lower is better)
            if arret_val <= arret_target:
                arret_status = "success"
            elif arret_val <= arret_warning:
                arret_status = "warning"
            else:
                arret_status = "danger"
            
            kpis["production_totale"] = {
                "value": int(production_val),
                "previous": int(production_prev),
                "target": int(production_target),
                "status": production_status,
                "trend": calculate_trend(production_val, production_prev),
                "change": round(calculate_change_percentage(production_val, production_prev), 1),
                "unit": "unités"
            }
            kpis["temps_arret"] = {
                "value": round(arret_val, 1),
                "previous": round(arret_prev, 1),
                "target": round(arret_target, 1),
                "status": arret_status,
                "trend": calculate_trend(arret_val, arret_prev),
                "change": round(calculate_change_percentage(arret_val, arret_prev), 1),
                "unit": "h"
            }
        
        # Osmoseur KPIs (shown for "all" and "osmoseur")
        if fetch_osmo:
            kpis["taux_recuperation_osmoseur"] = {
                "value": round(taux_recup_val, 1),
                "previous": round(taux_recup_prev, 1),
                "target": KPI_RULES["taux_recuperation"]["target"],
                "status": calculate_status(taux_recup_val, "taux_recuperation"),
                "trend": calculate_trend(taux_recup_val, taux_recup_prev),
                "change": round(calculate_change_percentage(taux_recup_val, taux_recup_prev), 1),
                "unit": "%"
            }
            kpis["qualite_eau"] = {
                "value": round(conductivite_val, 1),
                "previous": round(conductivite_prev, 1),
                "target": KPI_RULES["conductivite"]["target"],
                "status": calculate_status(conductivite_val, "conductivite"),
                "trend": calculate_trend(conductivite_val, conductivite_prev),
                "change": round(calculate_change_percentage(conductivite_val, conductivite_prev), 1),
                "unit": "µS/cm"
            }
        
        # --- TIME SERIES ---
        
        timeseries = {}
        
        # Remplisseuse timeseries
        if fetch_remp:
            sql_ts_rendement = text("""
                SELECT 
                    make_date(year, month, day) as date_label,
                    AVG(rendement) as value
                FROM dw.fact_remplisseuse_hourly f
                JOIN dw.dim_time t ON f.time_id = t.time_id
                WHERE f.time_id BETWEEN :start AND :end
                GROUP BY year, month, day
                ORDER BY year, month, day
            """)
            
            ts_rendement = db.execute(sql_ts_rendement, {"start": start_id, "end": end_id}).mappings().all()
            timeseries["rendement"] = [{"date": str(row.date_label), "value": round(row.value or 0, 2)} for row in ts_rendement]
        
        # Osmoseur timeseries
        if fetch_osmo:
            sql_ts_taux_recup = text("""
                SELECT 
                    make_date(year, month, day) as date_label,
                    AVG(taux_recuperation) as value
                FROM dw.fact_osmoseur_hourly f
                JOIN dw.dim_time t ON f.time_id = t.time_id
                WHERE f.time_id BETWEEN :start AND :end
                GROUP BY year, month, day
                ORDER BY year, month, day
            """)
            
            ts_taux_recup = db.execute(sql_ts_taux_recup, {"start": start_id, "end": end_id}).mappings().all()
            timeseries["taux_recuperation"] = [{"date": str(row.date_label), "value": round(row.value or 0, 2)} for row in ts_taux_recup]
        
        
        # --- ALERTS ---
        
        alerts = generate_alerts(kpis)
        
        # --- TECHNICIANS ---
        
        sql_tech = text("""
            SELECT 
                t.original_name,
                COUNT(f.fact_id) as intervention_count,
                AVG(f.rendement) as avg_efficiency
            FROM dw.fact_remplisseuse_hourly f
            JOIN dw.dim_technician t ON f.technician_id = t.technician_id
            WHERE f.time_id BETWEEN :start AND :end
            GROUP BY t.original_name
            ORDER BY avg_efficiency DESC
        """)
        
        technicians = [dict(row) for row in db.execute(sql_tech, {"start": start_id, "end": end_id}).mappings().all()]
        
        # --- CORRELATIONS ---
        
        sql_corr = text("""
            SELECT 
                CORR(temperature, rendement) as corr_temp_eff,
                CORR(vibrations, rendement) as corr_vib_eff
            FROM dw.fact_remplisseuse_hourly
            WHERE time_id BETWEEN :start AND :end
        """)
        
        corr_res = db.execute(sql_corr, {"start": start_id, "end": end_id}).mappings().first()
        
        correlations = {
            "temperature_vs_efficiency": round(corr_res.corr_temp_eff or 0, 3),
            "vibration_vs_efficiency": round(corr_res.corr_vib_eff or 0, 3),
            "interpretation": "Values close to 1/-1 indicate strong correlation. Near 0 means no correlation."
        }
        
        return {
            "kpis": kpis,
            "timeseries": timeseries,
            "alerts": alerts,
            "technicians": technicians,
            "correlations": correlations,
            "period": {
                "start": start_date,
                "end": end_date,
                "equipment": equipment
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 1. GLOBAL KPIs
# ============================================================================

@router.get("/kpi/global")
def get_global_kpis(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get global aggregated KPIs for the selected period.
    
    Query Logic:
    - AVG aggregation on Fact tables
    - Filtered by dim_time range
    """
    try:
        # Convert dates to time_id range (YYYYMMDD00 -> YYYYMMDD23)
        start_id = int(start_date.replace("-", "") + "00")
        end_id = int(end_date.replace("-", "") + "23")
        
        # Osmoseur KPIs
        sql_osmo = text("""
            SELECT 
                AVG(taux_recuperation) as avg_recovery,
                AVG(conductivite_permeat) as avg_conductivity
            FROM dw.fact_osmoseur_hourly
            WHERE time_id BETWEEN :start AND :end
        """)
        osmo_res = db.execute(sql_osmo, {"start": start_id, "end": end_id}).mappings().first()
        
        # Remplisseuse KPIs
        sql_remp = text("""
            SELECT 
                AVG(rendement) as avg_efficiency,
                SUM(unites_conformes) as total_production,
                SUM(heures_arret) as total_downtime
            FROM dw.fact_remplisseuse_hourly
            WHERE time_id BETWEEN :start AND :end
        """)
        remp_res = db.execute(sql_remp, {"start": start_id, "end": end_id}).mappings().first()
        
        return {
            "period": {"start": start_date, "end": end_date},
            "osmoseur": {
                "avg_recovery_rate": round(osmo_res.avg_recovery or 0, 2),
                "avg_conductivity": round(osmo_res.avg_conductivity or 0, 2)
            },
            "remplisseuse": {
                "avg_efficiency": round(remp_res.avg_efficiency or 0, 2),
                "total_production": int(remp_res.total_production or 0),
                "total_downtime": round(remp_res.total_downtime or 0, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 2. TIME SERIES
# ============================================================================

@router.get("/series")
def get_time_series(
    metric: str = Query(..., description="Metric to retrieve (e.g., 'taux_recuperation', 'rendement')"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    granularity: Literal["hour", "day", "month"] = Query("day"),
    db: Session = Depends(get_db)
):
    """
    Get time series data for charts.
    
    Query Logic:
    - Dynamic column selection based on metric
    - Date truncation via dim_time attributes
    """
    try:
        start_id = int(start_date.replace("-", "") + "00")
        end_id = int(end_date.replace("-", "") + "23")
        
        # Determine table and column safety
        allowed_metrics = {
            "taux_recuperation": ("dw.fact_osmoseur_hourly", "taux_recuperation"),
            "conductivite_permeat": ("dw.fact_osmoseur_hourly", "conductivite_permeat"),
            "rendement": ("dw.fact_remplisseuse_hourly", "rendement"),
            "unites_conformes": ("dw.fact_remplisseuse_hourly", "unites_conformes"),
            "heures_arret": ("dw.fact_remplisseuse_hourly", "heures_arret")
        }
        
        if metric not in allowed_metrics:
            raise HTTPException(status_code=400, detail="Invalid metric")
            
        table, col = allowed_metrics[metric]
        
        # Build Group By clause based on granularity (using dim_time columns)
        if granularity == "hour":
            date_build = "full_timestamp"
            group_by = "full_timestamp"
            order_by = "full_timestamp"
        elif granularity == "day":
            date_build = "make_date(year, month, day)"
            group_by = "year, month, day"
            order_by = "year, month, day"
        elif granularity == "month":
            date_build = "make_date(year, month, 1)"
            group_by = "year, month"
            order_by = "year, month"
            
        sql = text(f"""
            SELECT 
                {date_build} as date_label,
                AVG({col}) as value
            FROM {table} f
            JOIN dw.dim_time t ON f.time_id = t.time_id
            WHERE f.time_id BETWEEN :start AND :end
            GROUP BY {group_by}
            ORDER BY {order_by}
        """)
        
        results = db.execute(sql, {"start": start_id, "end": end_id}).mappings().all()
        
        return [
            {"date": row.date_label, "value": round(row.value or 0, 2)}
            for row in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 3. TECHNICIAN COMPARISON
# ============================================================================

@router.get("/technician/comparison")
def compare_technicians(
    start_date: str = Query(..., description="Start date"),
    end_date: str = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """
    Compare technicians performance.
    """
    try:
        start_id = int(start_date.replace("-", "") + "00")
        end_id = int(end_date.replace("-", "") + "23")
        
        sql = text("""
            SELECT 
                t.original_name,
                COUNT(f.fact_id) as intervention_count,
                AVG(f.rendement) as avg_efficiency
            FROM dw.fact_remplisseuse_hourly f
            JOIN dw.dim_technician t ON f.technician_id = t.technician_id
            WHERE f.time_id BETWEEN :start AND :end
            GROUP BY t.original_name
            ORDER BY avg_efficiency DESC
        """)
        
        results = db.execute(sql, {"start": start_id, "end": end_id}).mappings().all()
        
        return [dict(row) for row in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 4. CORRELATIONS
# ============================================================================

@router.get("/correlations")
def get_correlations(
    db: Session = Depends(get_db)
):
    """
    Simple correlation analysis (e.g., Temperature vs Efficiency).
    Uses PostgreSQL CORR function.
    """
    try:
        # Temperature vs Rendement (Remplisseuse)
        sql = text("""
            SELECT 
                CORR(temperature, rendement) as corr_temp_eff,
                CORR(vibrations, rendement) as corr_vib_eff
            FROM dw.fact_remplisseuse_hourly
        """)
        
        res = db.execute(sql).mappings().first()
        
        return {
            "temperature_vs_efficiency": round(res.corr_temp_eff or 0, 3),
            "vibration_vs_efficiency": round(res.corr_vib_eff or 0, 3),
            "interpretation": "Values close to 1/-1 indicate strong correlation. Near 0 means no correlation."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
