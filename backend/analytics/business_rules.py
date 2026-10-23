"""
Business Rules for Colatrack Dashboard.
Centralizes KPI targets, thresholds, and alert generation logic.
"""

from typing import List, Dict, Any
from datetime import datetime

# ============================================================================
# KPI TARGETS & THRESHOLDS
# ============================================================================

KPI_RULES = {
    "rendement": {
        "target": 85.0,
        "warning_threshold": 80.0,
        "critical_threshold": 75.0,
        "unit": "%",
        "higher_is_better": True
    },
    "taux_recuperation": {
        "target": 75.0,
        "warning_threshold": 70.0,
        "critical_threshold": 65.0,
        "unit": "%",
        "higher_is_better": True
    },
    "temps_arret": {
        "target": 1.2,
        "warning_threshold": 1.5,
        "critical_threshold": 2.0,
        "unit": "h",
        "higher_is_better": False
    },
    "production": {
        "target": 30000,
        "warning_threshold": 25000,
        "critical_threshold": 20000,
        "unit": "unités",
        "higher_is_better": True
    },
    "conductivite": {
        "target": 25.0,
        "warning_threshold": 30.0,
        "critical_threshold": 35.0,
        "unit": "µS/cm",
        "higher_is_better": False
    }
}


# ============================================================================
# STATUS CALCULATION
# ============================================================================

def calculate_status(value: float, kpi_name: str) -> str:
    """
    Determine status (success/warning/danger) based on KPI rules.
    
    Args:
        value: Current KPI value
        kpi_name: Name of the KPI
        
    Returns:
        Status string: "success", "warning", or "danger"
    """
    if kpi_name not in KPI_RULES:
        return "neutral"
    
    rules = KPI_RULES[kpi_name]
    higher_is_better = rules["higher_is_better"]
    
    if higher_is_better:
        if value >= rules["target"]:
            return "success"
        elif value >= rules["warning_threshold"]:
            return "warning"
        else:
            return "danger"
    else:
        if value <= rules["target"]:
            return "success"
        elif value <= rules["warning_threshold"]:
            return "warning"
        else:
            return "danger"


# ============================================================================
# ALERT GENERATION
# ============================================================================

def generate_alerts(kpis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate alerts based on KPI values and business rules.
    
    Args:
        kpis: Dictionary of KPI data with structure {kpi_name: {value, status, ...}}
        
    Returns:
        List of alert dictionaries
    """
    alerts = []
    alert_id_counter = 1
    
    # Check rendement
    if "rendement_global" in kpis:
        rendement_data = kpis["rendement_global"]
        if rendement_data.get("status") == "danger":
            alerts.append({
                "id": f"ALERT-{alert_id_counter:03d}",
                "severity": "critical",
                "equipment": "Remplisseuse",
                "message": f"Rendement critique: {rendement_data['value']:.1f}% (objectif: {KPI_RULES['rendement']['target']}%)",
                "timestamp": datetime.utcnow().isoformat()
            })
            alert_id_counter += 1
        elif rendement_data.get("status") == "warning":
            alerts.append({
                "id": f"ALERT-{alert_id_counter:03d}",
                "severity": "warning",
                "equipment": "Remplisseuse",
                "message": f"Rendement sous objectif: {rendement_data['value']:.1f}% (objectif: {KPI_RULES['rendement']['target']}%)",
                "timestamp": datetime.utcnow().isoformat()
            })
            alert_id_counter += 1
    
    # Check temps d'arrêt
    if "temps_arret" in kpis:
        arret_data = kpis["temps_arret"]
        if arret_data.get("status") == "danger":
            alerts.append({
                "id": f"ALERT-{alert_id_counter:03d}",
                "severity": "critical",
                "equipment": "Remplisseuse",
                "message": f"Temps d'arrêt excessif: {arret_data['value']:.1f}h (limite: {KPI_RULES['temps_arret']['critical_threshold']}h)",
                "timestamp": datetime.utcnow().isoformat()
            })
            alert_id_counter += 1
    
    # Check qualité eau
    if "qualite_eau" in kpis:
        qualite_data = kpis["qualite_eau"]
        if qualite_data.get("status") == "danger":
            alerts.append({
                "id": f"ALERT-{alert_id_counter:03d}",
                "severity": "critical",
                "equipment": "Osmoseur",
                "message": f"Qualité eau dégradée: conductivité {qualite_data['value']:.1f} µS/cm",
                "timestamp": datetime.utcnow().isoformat()
            })
            alert_id_counter += 1
    
    return alerts


# ============================================================================
# TREND CALCULATION
# ============================================================================

def calculate_trend(current: float, previous: float) -> str:
    """
    Calculate trend direction.
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        Trend string: "up", "down", or "neutral"
    """
    if previous == 0:
        return "neutral"
    
    change_pct = ((current - previous) / previous) * 100
    
    if abs(change_pct) < 2:
        return "neutral"
    elif change_pct > 0:
        return "up"
    else:
        return "down"


def calculate_change_percentage(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        Percentage change (can be negative)
    """
    if previous == 0:
        return 0.0
    
    return ((current - previous) / previous) * 100
