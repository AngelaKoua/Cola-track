"""
Layer 5 — Decision Support Engine.

Produces structured maintenance recommendations
with priority, deadline, justification, and impact assessment.
Answers: "What should we DO about it?"
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Transforms the outputs of Layers 1-4 into actionable,
    structured maintenance recommendations.
    """

    # Priority matrix: health_bucket × failure_prob_bucket → priority
    PRIORITY_MATRIX = {
        # (health_range, failure_range) → priority
        ("high_health", "low_risk"): "LOW",
        ("high_health", "medium_risk"): "MEDIUM",
        ("high_health", "high_risk"): "HIGH",
        ("medium_health", "low_risk"): "MEDIUM",
        ("medium_health", "medium_risk"): "HIGH",
        ("medium_health", "high_risk"): "CRITICAL",
        ("low_health", "low_risk"): "HIGH",
        ("low_health", "medium_risk"): "CRITICAL",
        ("low_health", "high_risk"): "CRITICAL",
    }

    ACTION_TEMPLATES = {
        "LOW": {
            "type": "surveillance",
            "action": "Poursuivre la surveillance normale. Planifier une inspection au prochain arrêt programmé.",
            "deadline_hours": 168,  # 7 days
            "impact_if_ignored": "Aucun impact immédiat. Risque de manquer une dégradation lente."
        },
        "MEDIUM": {
            "type": "inspection",
            "action": "Planifier une inspection détaillée par un technicien dans les 48 prochaines heures.",
            "deadline_hours": 48,
            "impact_if_ignored": "La dégradation pourrait s'accélérer. Risque de maintenance corrective non planifiée sous 7 jours."
        },
        "HIGH": {
            "type": "preventive",
            "action": "Engager une maintenance préventive immédiatement. Préparer les pièces de rechange.",
            "deadline_hours": 24,
            "impact_if_ignored": "Risque élevé d'arrêt non planifié sous 48-72h. Coût estimé 3-5x maintenance préventive."
        },
        "CRITICAL": {
            "type": "corrective",
            "action": "ARRÊT MACHINE RECOMMANDÉ. Engager la maintenance corrective immédiate.",
            "deadline_hours": 4,
            "impact_if_ignored": "Panne imminente. Risque de dommages matériels et de non-conformité produit. Coût estimé 10-15x maintenance préventive."
        }
    }

    def evaluate(
        self,
        health_index: float,
        failure_prob: float,
        alert_level: int,
        diagnoses: List[Dict[str, Any]],
        rul_hours: Optional[float],
        anomaly_count: int,
        velocity_label: str
    ) -> Dict[str, Any]:
        """
        Generate structured maintenance recommendation.
        """
        # 1. Determine priority from matrix
        health_bucket = self._health_bucket(health_index)
        risk_bucket = self._risk_bucket(failure_prob)
        priority = self.PRIORITY_MATRIX.get(
            (health_bucket, risk_bucket), "MEDIUM"
        )

        # Override to CRITICAL if alert level is 3
        if alert_level >= 3:
            priority = "CRITICAL"

        # 2. Get action template
        template = self.ACTION_TEMPLATES[priority]

        # 3. Build justification from diagnoses
        justification = self._build_justification(
            health_index, failure_prob, diagnoses, rul_hours, anomaly_count, velocity_label
        )

        # 4. Adapt action if specific diagnosis is available
        specific_action = template["action"]
        if diagnoses and diagnoses[0]["confidence"] >= 50:
            top_diag = diagnoses[0]
            specific_action = f"{top_diag['recommended_action']} — {template['action']}"

        # 5. Determine deadline (use RUL if available and shorter)
        deadline_hours = template["deadline_hours"]
        if rul_hours is not None and rul_hours < deadline_hours:
            deadline_hours = max(1, int(rul_hours * 0.5))  # Act at 50% of remaining time

        return {
            "priority": priority,
            "action_type": template["type"],
            "action": specific_action,
            "deadline_hours": deadline_hours,
            "deadline_label": self._format_deadline(deadline_hours),
            "justification": justification,
            "impact_if_ignored": template["impact_if_ignored"],
            "confidence": diagnoses[0]["confidence"] if diagnoses else None,
            "estimated_rul_hours": rul_hours
        }

    def _health_bucket(self, health: float) -> str:
        if health >= 75:
            return "high_health"
        elif health >= 50:
            return "medium_health"
        return "low_health"

    def _risk_bucket(self, failure_prob: float) -> str:
        if failure_prob < 0.3:
            return "low_risk"
        elif failure_prob < 0.6:
            return "medium_risk"
        return "high_risk"

    def _build_justification(
        self,
        health: float,
        failure_prob: float,
        diagnoses: List[Dict],
        rul_hours: Optional[float],
        anomaly_count: int,
        velocity_label: str
    ) -> str:
        parts = []
        parts.append(f"Health Index: {health:.1f}/100")
        parts.append(f"Probabilité de panne 24h: {failure_prob:.0%}")

        if velocity_label in ("degrading", "rapid_degradation"):
            parts.append(f"Tendance: dégradation {'rapide' if 'rapid' in velocity_label else 'active'}")

        if rul_hours is not None:
            parts.append(f"Temps estimé avant seuil critique: {rul_hours:.0f}h")

        if anomaly_count > 0:
            parts.append(f"{anomaly_count} paramètre(s) hors norme détecté(s)")

        if diagnoses:
            top = diagnoses[0]
            parts.append(f"Cause probable: {top['diagnosis']} (confiance: {top['confidence']}%)")

        return " | ".join(parts)

    def _format_deadline(self, hours: int) -> str:
        if hours < 1:
            return "Immédiat"
        elif hours < 24:
            return f"Sous {hours}h"
        elif hours < 48:
            return "Sous 24-48h"
        elif hours < 168:
            return f"Sous {hours // 24} jours"
        return "Sous 7 jours"
