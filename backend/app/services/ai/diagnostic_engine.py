"""
Layer 3 — Root Cause Analysis / Diagnostic Engine.

Pattern-based fault identification with confidence scoring.
Answers: "WHY is this happening?"
"""
import numpy as np
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DiagnosticEngine:
    """
    Matches current sensor patterns against known failure signatures.
    Each diagnosis gets a confidence score based on how many conditions are met.
    """

    OSMOSEUR_PATTERNS = [
        {
            "name": "Colmatage Membrane",
            "description": "Les membranes se bouchent progressivement, réduisant le débit et augmentant la conductivité.",
            "conditions": {
                "debit_permeat": "falling",
                "conductivite_permeat": "rising",
                "taux_recuperation": "falling"
            },
            "action": "Nettoyage chimique CIP ou remplacement membrane",
            "rul_impact": "Arrêt sous 3-7 jours sans intervention",
            "severity": "high"
        },
        {
            "name": "Dégradation Chimique Eau d'Entrée",
            "description": "La qualité de l'eau source se dégrade, affectant le perméat produit.",
            "conditions": {
                "ph_sortie": "falling",
                "tds": "rising",
                "conductivite_permeat": "rising"
            },
            "action": "Vérifier dosage antiscalant, analyser qualité eau entrée",
            "rul_impact": "Qualité perméat non conforme sous 12h",
            "severity": "high"
        },
        {
            "name": "Chute de Rendement Osmose",
            "description": "Le taux de récupération chute, indiquant un dysfonctionnement du système.",
            "conditions": {
                "taux_recuperation": "falling",
                "debit_concentrat": "rising"
            },
            "action": "Vérifier les vannes de régulation et le circuit concentrat",
            "rul_impact": "Surconsommation d'eau et perte d'efficacité sous 24-48h",
            "severity": "high"
        },
        {
            "name": "Contamination Chlore",
            "description": "Le chlore libre dépasse les seuils acceptables, risquant d'endommager les membranes.",
            "conditions": {
                "chlore_libre": "rising",
                "turbidite": "rising"
            },
            "action": "Vérifier le dosage du déchlorinateur en amont",
            "rul_impact": "Dégradation irréversible des membranes sous 24h",
            "severity": "critical"
        }
    ]

    REMPLISSEUSE_PATTERNS = [
        {
            "name": "Usure Roulements Moteur",
            "description": "Les vibrations augmentent progressivement, signe d'usure mécanique du moteur principal.",
            "conditions": {
                "vibrations": "rising",
                "mtbf": "falling"
            },
            "action": "Remplacement roulements ou lubrification moteur",
            "rul_impact": "Casse moteur possible sous 5-14 jours",
            "severity": "high"
        },
        {
            "name": "Dérive Volume (Sous-remplissage)",
            "description": "Le volume de remplissage diminue, produisant des bouteilles non conformes.",
            "conditions": {
                "volume_remplissage": "falling",
                "rendement": "falling"
            },
            "action": "Recalibrer vannes de dosage volumétrique",
            "rul_impact": "Non-conformité produit immédiate",
            "severity": "critical"
        },
        {
            "name": "Perte de Carbonatation",
            "description": "Le CO2 dissous chute, produisant un produit plat.",
            "conditions": {
                "carbonation": "falling",
                "temperature_remplissage": "rising"
            },
            "action": "Vérifier circuit CO2, température de refroidissement, et pression de saturation",
            "rul_impact": "Produit plat sous 2-4h",
            "severity": "critical"
        },
        {
            "name": "Surchauffe Ligne de Remplissage",
            "description": "La température augmente anormalement, pouvant affecter la qualité produit.",
            "conditions": {
                "temperature_remplissage": "rising",
                "carbonation": "falling"
            },
            "action": "Vérifier système de refroidissement, échangeur thermique",
            "rul_impact": "Dégradation qualité sous 1-6h",
            "severity": "high"
        }
    ]

    def evaluate(
        self,
        t0_data: Dict[str, float],
        history_data: List[Dict[str, float]],
        machine_type: str
    ) -> List[Dict[str, Any]]:
        """
        For each failure pattern, evaluate how many conditions match.
        Returns a sorted list of possible diagnoses with confidence scores.
        """
        patterns = self.OSMOSEUR_PATTERNS if machine_type == "osmoseur" else self.REMPLISSEUSE_PATTERNS
        results = []

        for pattern in patterns:
            matched = 0
            total = len(pattern["conditions"])
            evidence = []

            for param, expected_trend in pattern["conditions"].items():
                actual_trend = self._compute_trend(param, history_data)
                is_match = actual_trend == expected_trend

                if is_match:
                    matched += 1

                evidence.append({
                    "parameter": param,
                    "expected": expected_trend,
                    "actual": actual_trend,
                    "match": is_match,
                    "current_value": t0_data.get(param, None)
                })

            confidence = round((matched / total) * 100) if total > 0 else 0

            if confidence > 0:  # Only include if at least one condition matches
                results.append({
                    "diagnosis": pattern["name"],
                    "description": pattern["description"],
                    "confidence": confidence,
                    "matched_conditions": matched,
                    "total_conditions": total,
                    "severity": pattern["severity"],
                    "recommended_action": pattern["action"],
                    "rul_impact": pattern["rul_impact"],
                    "evidence": evidence
                })

        # Sort by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def _compute_trend(self, param: str, history: List[Dict[str, float]]) -> str:
        """
        Determines if a parameter is rising, falling, or stable
        based on the recent history.
        """
        if len(history) < 3:
            return "stable"

        values = [h.get(param, 0) for h in history if param in h]
        if len(values) < 3:
            return "stable"

        # Use last 6 values (30 min window at 5-min intervals)
        recent = values[-6:] if len(values) >= 6 else values
        diffs = np.diff(recent)

        rising = np.sum(diffs > 0)
        falling = np.sum(diffs < 0)
        total = len(diffs)

        if rising >= total * 0.6:
            # Check magnitude for "fast" detection
            avg_change = np.mean(np.abs(diffs))
            if avg_change > np.std(values) * 0.5:
                return "rising"
            return "rising"
        elif falling >= total * 0.6:
            return "falling"

        return "stable"
