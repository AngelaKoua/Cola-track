"""
Transversal — Explainability Module.

Provides SHAP-like feature importance analysis for ML predictions.
Since SHAP requires the shap library which may not be installed,
this module provides a lightweight alternative using built-in
feature importances from tree-based models.
"""
import numpy as np
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """
    Provides feature contribution analysis for ML model predictions.
    Uses built-in feature importance from tree-based models (XGBoost, RF, GBR).
    """

    FEATURE_LABELS_OSM = {
        "debit_permeat": "Débit Perméat (L/h)",
        "debit_concentrat": "Débit Concentrat (L/h)",
        "taux_recuperation": "Taux Récupération (%)",
        "conductivite_permeat": "Conductivité (µS/cm)",
        "ph_entree": "pH Entrée",
        "ph_sortie": "pH Sortie",
        "turbidite": "Turbidité (NTU)",
        "chlore_libre": "Chlore Libre (mg/L)",
        "tds": "TDS (ppm)",
        "durete_totale": "Dureté Totale (°f)",
        "debit_permeat_rolling_1h": "Débit Moy. 1h",
        "conductivite_permeat_rolling_1h": "Conductivité Moy. 1h",
        "conductivite_rate": "Variation Conductivité",
    }

    FEATURE_LABELS_RMP = {
        "vibrations": "Vibrations Moteur (mm/s)",
        "mtbf": "MTBF (heures)",
        "temperature_remplissage": "Température (°C)",
        "volume_remplissage": "Volume (L)",
        "carbonation": "Carbonatation (g/L)",
        "rendement": "Rendement (%)",
        "conso_air_co2": "Conso Air/CO2 (m³/h)",
        "vibrations_rate": "Variation Vibrations",
        "mtbf_rate": "Variation MTBF",
        "vibrations_rolling_1h": "Vibrations Moy. 1h",
        "mtbf_rolling_1h": "MTBF Moy. 1h",
        "volume_remplissage_rolling_1h": "Volume Moy. 1h",
    }

    def get_feature_importance(
        self,
        model,
        feature_names: List[str],
        machine_type: str,
        top_n: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Extract feature importance from a tree-based model.
        Works with XGBoost, RandomForest, and GradientBoosting.
        """
        labels = self.FEATURE_LABELS_OSM if machine_type == "osmoseur" else self.FEATURE_LABELS_RMP

        try:
            importances = model.feature_importances_
        except AttributeError:
            logger.warning("Model does not have feature_importances_ attribute.")
            return []

        if len(importances) != len(feature_names):
            logger.warning(
                f"Mismatch: {len(importances)} importances vs {len(feature_names)} features"
            )
            return []

        contributions = []
        for i, name in enumerate(feature_names):
            contributions.append({
                "feature": name,
                "label": labels.get(name, name),
                "importance": round(float(importances[i]), 4),
                "importance_pct": 0.0  # Will be computed below
            })

        total = sum(c["importance"] for c in contributions)
        if total > 0:
            for c in contributions:
                c["importance_pct"] = round((c["importance"] / total) * 100, 1)

        # Sort by importance descending
        contributions.sort(key=lambda x: x["importance"], reverse=True)

        return contributions[:top_n]

    def explain_prediction_context(
        self,
        feature_importances: List[Dict],
        anomalous_params: List[Dict],
        diagnoses: List[Dict]
    ) -> Dict[str, Any]:
        """
        Builds a human-readable explanation linking feature importance
        to detected anomalies and diagnoses.
        """
        # Find overlap between top important features and anomalous parameters
        important_features = {fi["feature"] for fi in feature_importances[:5]}
        anomalous_features = {ap["name"] for ap in anomalous_params if ap.get("is_anomalous")}

        overlap = important_features & anomalous_features
        
        explanation_lines = []

        if overlap:
            explanation_lines.append(
                f"Les paramètres les plus influents sur la prédiction ({', '.join(overlap)}) "
                f"sont actuellement en zone anormale, ce qui renforce la confiance du diagnostic."
            )

        if diagnoses and diagnoses[0]["confidence"] >= 50:
            top_diag = diagnoses[0]
            explanation_lines.append(
                f"Le diagnostic principal '{top_diag['diagnosis']}' est soutenu par "
                f"{top_diag['matched_conditions']}/{top_diag['total_conditions']} conditions vérifiées."
            )

        if not explanation_lines:
            explanation_lines.append(
                "Les indicateurs sont dans des plages modérées. Aucun facteur dominant identifié."
            )

        return {
            "key_features_anomalous": list(overlap),
            "explanation": " ".join(explanation_lines),
            "top_features": feature_importances[:5]
        }
