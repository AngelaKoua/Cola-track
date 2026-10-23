"""
Layer 4 — Prognostic Engine.

Forecasts individual sensor parameters and estimates RUL.
Answers: "What WILL happen in the future?"
"""
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PrognosticEngine:
    """
    Provides:
    - Per-parameter forecasting using weighted linear regression
    - Multi-horizon failure probability (conceptual)
    - RUL estimation based on degradation velocity
    """

    # Parameters to forecast for each machine type
    FORECAST_PARAMS = {
        "osmoseur": [
            "debit_permeat", "conductivite_permeat", "tds", "taux_recuperation"
        ],
        "remplisseuse": [
            "vibrations", "volume_remplissage", "temperature_remplissage", "carbonation"
        ]
    }

    def forecast_parameters(
        self,
        history_data: List[Dict[str, float]],
        machine_type: str,
        horizons_intervals: List[int] = [12, 72, 288]  # 1h, 6h, 24h at 5-min intervals
    ) -> List[Dict[str, Any]]:
        """
        Forecast each critical parameter at multiple horizons.

        Returns list of parameter forecasts.
        """
        params = self.FORECAST_PARAMS.get(machine_type, [])
        forecasts = []

        for param in params:
            values = [h.get(param) for h in history_data if param in h and h.get(param) is not None]

            if len(values) < 3:
                continue

            forecast_result = self._weighted_linear_forecast(values, horizons_intervals)

            forecasts.append({
                "parameter": param,
                "current_value": round(values[-1], 3),
                "trend_slope": forecast_result["slope"],
                "trend_direction": "rising" if forecast_result["slope"] > 0.001 else "falling" if forecast_result["slope"] < -0.001 else "stable",
                "forecasts": forecast_result["predictions"]
            })

        return forecasts

    def estimate_rul(
        self,
        current_health: float,
        health_history: List[float],
        critical_threshold: float = 50.0,
        warning_threshold: float = 70.0
    ) -> Dict[str, Any]:
        """
        Estimate Remaining Useful Life based on health index degradation trend.
        """
        velocity = self._compute_degradation_velocity(health_history)

        # Time to warning threshold
        time_to_warning = None
        if velocity < 0 and current_health > warning_threshold:
            remaining = current_health - warning_threshold
            intervals = remaining / abs(velocity)
            time_to_warning = round((intervals * 5) / 60, 1)  # hours

        # Time to critical threshold
        time_to_critical = None
        if velocity < 0 and current_health > critical_threshold:
            remaining = current_health - critical_threshold
            intervals = remaining / abs(velocity)
            time_to_critical = round((intervals * 5) / 60, 1)  # hours

        return {
            "current_health": round(current_health, 2),
            "degradation_velocity_per_hour": round(velocity * 12, 3),  # Convert per-interval to per-hour
            "hours_to_warning": time_to_warning,
            "hours_to_critical": time_to_critical,
            "risk_level": self._classify_rul_risk(time_to_critical),
            "velocity_label": self._velocity_label(velocity)
        }

    def _weighted_linear_forecast(
        self,
        values: List[float],
        horizons: List[int]
    ) -> Dict[str, Any]:
        """
        Weighted linear regression where recent values have more weight.
        """
        n = len(values)
        X = np.arange(n)
        y = np.array(values)
        weights = np.linspace(0.3, 1.0, n)

        # Weighted OLS
        w_sum = np.sum(weights)
        wx_mean = np.sum(weights * X) / w_sum
        wy_mean = np.sum(weights * y) / w_sum

        numerator = np.sum(weights * (X - wx_mean) * (y - wy_mean))
        denominator = np.sum(weights * (X - wx_mean) ** 2)

        if denominator == 0:
            slope = 0.0
            intercept = wy_mean
        else:
            slope = numerator / denominator
            intercept = wy_mean - slope * wx_mean

        predictions = {}
        for horizon in horizons:
            future_x = n + horizon
            predicted_value = intercept + slope * future_x
            label = f"T+{(horizon * 5) // 60}h" if horizon >= 12 else f"T+{horizon * 5}min"
            predictions[label] = round(float(predicted_value), 3)

        return {
            "slope": round(float(slope), 6),
            "intercept": round(float(intercept), 3),
            "predictions": predictions
        }

    def _compute_degradation_velocity(self, health_history: List[float]) -> float:
        """Points per 5-min interval (negative = degrading)."""
        if len(health_history) < 2:
            return 0.0

        n = len(health_history)
        X = np.arange(n)
        y = np.array(health_history)
        weights = np.linspace(0.5, 1.0, n)

        w_sum = np.sum(weights)
        wx_mean = np.sum(weights * X) / w_sum
        wy_mean = np.sum(weights * y) / w_sum

        num = np.sum(weights * (X - wx_mean) * (y - wy_mean))
        den = np.sum(weights * (X - wx_mean) ** 2)

        return float(num / den) if den != 0 else 0.0

    def _classify_rul_risk(self, hours_to_critical: Optional[float]) -> str:
        if hours_to_critical is None:
            return "stable"
        if hours_to_critical <= 6:
            return "imminent"
        if hours_to_critical <= 24:
            return "high"
        if hours_to_critical <= 72:
            return "moderate"
        return "low"

    def _velocity_label(self, velocity: float) -> str:
        if velocity >= 0.1:
            return "improving"
        elif velocity >= -0.05:
            return "stable"
        elif velocity >= -0.3:
            return "slow_degradation"
        elif velocity >= -1.0:
            return "degrading"
        else:
            return "rapid_degradation"
