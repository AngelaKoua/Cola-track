"""
Layer 2 — Anomaly Detection Engine.

Provides per-parameter anomaly detection using Z-Score and drift detection.
Answers: "Which specific parameters are behaving abnormally?"
"""
import numpy as np
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AnomalyEngine:
    """
    Detects anomalies at the individual parameter level using:
    1. Z-Score against a dynamic baseline (healthy state statistics)
    2. Simple drift detection (consecutive readings moving in one direction)
    """

    # Theoretical baselines (mean, std) for each machine type
    # In production, these should be computed from healthy historical data.
    BASELINES = {
        "osmoseur": {
            "debit_permeat": {"mean": 1150.0, "std": 120.0, "unit": "L/h"},
            "debit_concentrat": {"mean": 450.0, "std": 80.0, "unit": "L/h"},
            "taux_recuperation": {"mean": 75.0, "std": 3.0, "unit": "%"},
            "conductivite_permeat": {"mean": 20.0, "std": 8.0, "unit": "µS/cm"},
            "ph_entree": {"mean": 7.2, "std": 0.3, "unit": "pH"},
            "ph_sortie": {"mean": 7.0, "std": 0.4, "unit": "pH"},
            "turbidite": {"mean": 0.5, "std": 0.2, "unit": "NTU"},
            "chlore_libre": {"mean": 0.05, "std": 0.03, "unit": "mg/L"},
            "tds": {"mean": 200.0, "std": 50.0, "unit": "ppm"},
            "durete_totale": {"mean": 1.0, "std": 0.5, "unit": "°f"},
        },
        "remplisseuse": {
            "vibrations": {"mean": 1.2, "std": 0.5, "unit": "mm/s"},
            "volume_remplissage": {"mean": 0.500, "std": 0.008, "unit": "L"},
            "temperature_remplissage": {"mean": 4.5, "std": 1.0, "unit": "°C"},
            "carbonation": {"mean": 6.5, "std": 0.3, "unit": "g/L"},
            "mtbf": {"mean": 95.0, "std": 15.0, "unit": "h"},
            "rendement": {"mean": 95.0, "std": 3.0, "unit": "%"},
            "conso_air_co2": {"mean": 110.0, "std": 15.0, "unit": "m³/h"},
        }
    }

    Z_SCORE_THRESHOLD = 2.5  # Standard deviations to flag

    def evaluate(self, t0_data: Dict[str, float], machine_type: str) -> Dict[str, Any]:
        """
        Evaluate all parameters of the current reading against baselines.

        Returns:
            {
                "total_anomalies": int,
                "parameters": [
                    {"name": ..., "value": ..., "z_score": ..., "is_anomalous": ..., "unit": ..., ...}
                ]
            }
        """
        baselines = self.BASELINES.get(machine_type, {})
        results = []
        anomaly_count = 0

        for param_name, baseline in baselines.items():
            value = t0_data.get(param_name)
            if value is None:
                continue

            mean = baseline["mean"]
            std = baseline["std"]
            unit = baseline["unit"]

            z_score = (value - mean) / std if std > 0 else 0.0
            is_anomalous = abs(z_score) > self.Z_SCORE_THRESHOLD

            if is_anomalous:
                anomaly_count += 1

            # Determine direction
            if z_score > 0.5:
                direction = "above_normal"
            elif z_score < -0.5:
                direction = "below_normal"
            else:
                direction = "normal"

            results.append({
                "name": param_name,
                "value": round(value, 3),
                "z_score": round(z_score, 2),
                "is_anomalous": is_anomalous,
                "direction": direction,
                "baseline_mean": mean,
                "baseline_std": std,
                "unit": unit,
                "deviation_pct": round(((value - mean) / mean) * 100, 1) if mean != 0 else 0.0
            })

        # Sort by absolute z-score descending (most anomalous first)
        results.sort(key=lambda x: abs(x["z_score"]), reverse=True)

        return {
            "total_anomalies": anomaly_count,
            "parameters": results
        }

    def detect_drift(self, history_values: List[float], window: int = 6) -> Dict[str, Any]:
        """
        Simple drift detection: checks if the last `window` readings
        are monotonically increasing or decreasing.

        Returns:
            {"is_drifting": bool, "direction": "rising"|"falling"|"stable", "strength": float}
        """
        if len(history_values) < window:
            return {"is_drifting": False, "direction": "stable", "strength": 0.0}

        recent = history_values[-window:]
        diffs = np.diff(recent)
        rising = np.sum(diffs > 0)
        falling = np.sum(diffs < 0)

        total = len(diffs)
        if rising >= total * 0.8:
            return {
                "is_drifting": True,
                "direction": "rising",
                "strength": round(rising / total, 2)
            }
        elif falling >= total * 0.8:
            return {
                "is_drifting": True,
                "direction": "falling",
                "strength": round(falling / total, 2)
            }

        return {"is_drifting": False, "direction": "stable", "strength": 0.0}
