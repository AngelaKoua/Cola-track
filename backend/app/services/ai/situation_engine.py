"""
Layer 1 — Situation Awareness Engine.

Aggregates the raw ML model outputs into a unified situation report.
Answers: "What is happening right now?"
"""
import numpy as np
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SituationEngine:
    """
    Computes the overall machine situation from ML model outputs
    and raw telemetry data, including degradation velocity.
    """

    def evaluate(
        self,
        health_index: float,
        failure_prob_24h: float,
        is_anomaly: bool,
        quality_risk: Optional[float],
        alert_level: int,
        reason: str,
        health_history: List[float]
    ) -> Dict[str, Any]:
        """
        Build a complete situation report.

        Args:
            health_index: Current health index (0-100)
            failure_prob_24h: 24h failure probability (0-1)
            is_anomaly: Isolation Forest result
            quality_risk: Quality risk probability (Remplisseuse only)
            alert_level: Hybrid rule engine alert level (0-3)
            reason: Text reason from hybrid engine
            health_history: List of recent health index values (oldest first)

        Returns:
            Situation report dict
        """
        # Calculate degradation velocity (points per reading interval)
        velocity = self._compute_velocity(health_history)

        # Estimate time to critical threshold (health = 50)
        estimated_rul_hours = self._estimate_rul(health_index, velocity, critical_threshold=50)

        # Overall status label
        status = self._determine_status(health_index, failure_prob_24h, alert_level)

        return {
            "health_index": round(health_index, 2),
            "failure_probability_24h": round(failure_prob_24h, 3),
            "quality_risk": round(quality_risk, 3) if quality_risk is not None else None,
            "is_anomaly": is_anomaly,
            "alert_level": alert_level,
            "reason": reason,
            "degradation_velocity": round(velocity, 3),
            "velocity_label": self._velocity_label(velocity),
            "estimated_rul_hours": estimated_rul_hours,
            "status": status
        }

    def _compute_velocity(self, health_history: List[float]) -> float:
        """
        Compute degradation velocity in points/interval.
        Negative = degrading, Positive = improving, 0 = stable.
        """
        if not health_history or len(health_history) < 2:
            return 0.0

        # Use weighted linear regression on last N points
        n = len(health_history)
        x = np.arange(n)
        y = np.array(health_history)
        weights = np.linspace(0.5, 1.0, n)  # Recent points weighted more

        w_sum = np.sum(weights)
        wx_mean = np.sum(weights * x) / w_sum
        wy_mean = np.sum(weights * y) / w_sum

        numerator = np.sum(weights * (x - wx_mean) * (y - wy_mean))
        denominator = np.sum(weights * (x - wx_mean) ** 2)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return float(slope)

    def _estimate_rul(self, current_health: float, velocity: float, critical_threshold: float = 50) -> Optional[float]:
        """
        Estimate Remaining Useful Life in hours.
        Assumes each reading interval = 5 minutes.
        """
        if velocity >= 0:
            return None  # Machine is stable or improving

        remaining_points = current_health - critical_threshold
        if remaining_points <= 0:
            return 0.0

        intervals_remaining = remaining_points / abs(velocity)
        hours_remaining = (intervals_remaining * 5) / 60  # 5 min per interval
        return round(hours_remaining, 1)

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

    def _determine_status(self, health: float, failure_prob: float, alert_level: int) -> str:
        if alert_level >= 3:
            return "CRITICAL"
        if alert_level >= 2 or failure_prob > 0.7:
            return "WARNING"
        if alert_level >= 1 or health < 70:
            return "CAUTION"
        return "NOMINAL"
