#!/usr/bin/env python3
"""
Data Pipeline Verification Script for Colatrack
===============================================

This script verifies the complete analytics data pipeline:
- Source tables (application DB)
- Data warehouse tables
- Analytics endpoints

Usage:
    python verify_pipeline.py
"""

import sys
import requests
from datetime import datetime, timedelta
from sqlalchemy import text
from app.database import SessionLocal


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_source_tables(db):
    """Check row counts in source application tables."""
    print_section("1. SOURCE TABLES (Application Database)")
    
    queries = {
        "osmoseur_readings": "SELECT COUNT(*) FROM osmoseur_readings",
        "remplisseuse_readings": "SELECT COUNT(*) FROM remplisseuse_readings"
    }
    
    results = {}
    for table, query in queries.items():
        count = db.execute(text(query)).scalar()
        results[table] = count
        status = "[OK]" if count > 0 else "[EMPTY]"
        print(f"  {status} {table:30} {count:>10} rows")
    
    return all(count > 0 for count in results.values())


def check_warehouse_tables(db):
    """Check row counts in data warehouse tables."""
    print_section("2. DATA WAREHOUSE TABLES (dw schema)")
    
    queries = {
        "dim_technician": "SELECT COUNT(*) FROM dw.dim_technician",
        "dim_time": "SELECT COUNT(*) FROM dw.dim_time",
        "fact_osmoseur_hourly": "SELECT COUNT(*) FROM dw.fact_osmoseur_hourly",
        "fact_remplisseuse_hourly": "SELECT COUNT(*) FROM dw.fact_remplisseuse_hourly"
    }
    
    results = {}
    for table, query in queries.items():
        count = db.execute(text(query)).scalar()
        results[table] = count
        status = "[OK]" if count > 0 else "[EMPTY]"
        print(f"  {status} {table:30} {count:>10} rows")
    
    return all(count > 0 for count in results.values())


def check_date_ranges(db):
    """Check date ranges in source and warehouse."""
    print_section("3. DATE RANGES")
    
    # Source dates
    osmo_dates = db.execute(text("""
        SELECT MIN(created_at) as min_date, MAX(created_at) as max_date
        FROM osmoseur_readings
    """)).mappings().first()
    
    remp_dates = db.execute(text("""
        SELECT MIN(created_at) as min_date, MAX(created_at) as max_date
        FROM remplisseuse_readings
    """)).mappings().first()
    
    print("\n  Source Tables:")
    if osmo_dates and osmo_dates['min_date']:
        print(f"    Osmoseur:     {osmo_dates['min_date']} to {osmo_dates['max_date']}")
    else:
        print(f"    Osmoseur:     No data")
        
    if remp_dates and remp_dates['min_date']:
        print(f"    Remplisseuse: {remp_dates['min_date']} to {remp_dates['max_date']}")
    else:
        print(f"    Remplisseuse: No data")
    
    # Warehouse dates
    try:
        dw_dates = db.execute(text("""
            SELECT MIN(full_timestamp) as min_date, MAX(full_timestamp) as max_date
            FROM dw.dim_time
        """)).mappings().first()
        
        print("\n  Data Warehouse:")
        if dw_dates and dw_dates['min_date']:
            print(f"    dim_time:     {dw_dates['min_date']} to {dw_dates['max_date']}")
        else:
            print(f"    dim_time:     No data")
    except:
        print("\n  Data Warehouse: Error checking dates (likely empty)")


def check_analytics_endpoint():
    """Test analytics endpoint."""
    print_section("4. ANALYTICS API ENDPOINT")
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    url = "http://localhost:8000/analytics/dashboard/overview"
    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "equipment": "all"
    }
    
    print(f"\n  Testing: GET {url}")
    print(f"  Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n  [OK] Status: {response.status_code} OK")
            
            # Check KPIs
            kpis = data.get("kpis", {})
            rendement = kpis.get("rendement_global", {}).get("value", 0)
            production = kpis.get("production_totale", {}).get("value", 0)
            
            print(f"\n  Sample KPIs:")
            print(f"    Rendement Global: {rendement}%")
            print(f"    Production Total: {production} unités")
            
            # Check timeseries
            ts_rendement = data.get("timeseries", {}).get("rendement", [])
            print(f"\n  Time Series:")
            print(f"    Rendement data points: {len(ts_rendement)}")
            
            # Check technicians
            technicians = data.get("technicians", [])
            print(f"    Technicians: {len(technicians)}")
            
            if rendement > 0 or production > 0:
                print(f"\n  [OK] Endpoint returns meaningful data")
                return True
            else:
                print(f"\n  [WARN] Endpoint returns zero values")
                return False
        else:
            print(f"\n  [ERROR] Status: {response.status_code}")
            print(f"  Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n  [ERROR] Cannot connect to backend (is it running?)")
        print(f"    Start with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n  [ERROR] Error: {str(e)}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  COLATRACK ANALYTICS PIPELINE VERIFICATION")
    print("=" * 70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = SessionLocal()
    
    try:
        # Run checks
        source_ok = check_source_tables(db)
        warehouse_ok = check_warehouse_tables(db)
        check_date_ranges(db)
        api_ok = check_analytics_endpoint()
        
        # Summary
        print_section("SUMMARY")
        
        print(f"\n  Source Tables:    {'[OK]' if source_ok else '[EMPTY]'}")
        print(f"  Data Warehouse:   {'[OK]' if warehouse_ok else '[EMPTY]'}")
        print(f"  Analytics API:    {'[OK]' if api_ok else '[FAILED]'}")
        
        if source_ok and not warehouse_ok:
            print("\n" + "!" * 70)
            print("  ACTION REQUIRED: Run ETL to populate data warehouse")
            print("  Command: python run_etl.py")
            print("!" * 70)
            return 1
        elif warehouse_ok and not api_ok:
            print("\n" + "!" * 70)
            print("  WARNING: Data warehouse populated but API not responding")
            print("  Check that backend is running: uvicorn app.main:app --reload")
            print("!" * 70)
            return 1
        elif warehouse_ok and api_ok:
            print("\n" + "=" * 70)
            print("  SUCCESS: Pipeline is fully functional!")
            print("  Dashboard should display data at http://localhost:3000/dashboard")
            print("=" * 70)
            return 0
        else:
            print("\n" + "!" * 70)
            print("  ERROR: Multiple issues detected - review above")
            print("!" * 70)
            return 1
            
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
