# Colatrack — Data Science

Pipeline qui produit les données synthétiques et les modèles de maintenance prédictive
utilisés par le backend.

## Pipeline

À lancer dans cet ordre (depuis n'importe quel dossier, les chemins sont relatifs au script) :

| Étape | Script | Entrée | Sortie |
| --- | --- | --- | --- |
| 1. Génération du dataset | [generate_dataset.py](generate_dataset.py) | — | `data/industrial_iot_timeseries.csv`, `data/industrial_incidents.csv` |
| 2. Analyse exploratoire | [eda_analysis.py](eda_analysis.py) | `data/` | `outputs/eda/*.png`, `outputs/eda/stats_*.csv` |
| 3. Rapport PDF de l'EDA | [generate_pdf_report.py](generate_pdf_report.py) | `outputs/eda/`, `assets/dejavu-fonts/` | `../docs/Rapport_Phase1_EDA_Colatrack.pdf` |
| 4. Entraînement des modèles | [train_models.py](train_models.py) | `data/` | `../backend/app/ml_models/*.joblib`, `outputs/reports/ml_metrics.json` |
| 5. Test de l'inférence | [inference_engine.py](inference_engine.py) | `../backend/app/ml_models/` | affichage console |

Les modèles sont écrits **directement dans le backend** (`backend/app/ml_models/`) : c'est
l'unique copie, chargée par l'API au démarrage.

## Modèles

| Modèle | Rôle |
| --- | --- |
| Isolation Forest (+ scaler) | Détection d'anomalies, par machine |
| XGBoost | Probabilité de panne à 24 h, par machine |
| Gradient Boosting Regressor | Indice de santé, par machine |
| Random Forest / Régression logistique (+ scaler) | Risque qualité (remplisseuse) |

## Structure

```text
data-science/
├── data/              # Datasets CSV générés
├── outputs/
│   ├── eda/           # Graphiques et statistiques de l'EDA
│   └── reports/       # Métriques des modèles (ml_metrics.json)
├── assets/
│   └── dejavu-fonts/  # Polices utilisées pour le rapport PDF
└── *.py               # Scripts du pipeline
```

## Dépendances

```bash
pip install pandas numpy scipy matplotlib seaborn scikit-learn xgboost imbalanced-learn joblib fpdf2
```
