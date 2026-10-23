# Backend Analytics Layer

Ce module expose des endpoints optimisés pour la Business Intelligence (BI), interrogeant exclusivement le Data Warehouse via le schéma `dw`.

## Base URL
`/analytics`

## Endpoints

### 1. KPIs Globaux
**GET** `/analytics/kpi/global`
Récupère les indicateurs macro pour une période donnée.
- **Params**: `start_date`, `end_date` (YYYY-MM-DD)
- **Source**: `dw.fact_osmoseur_hourly`, `dw.fact_remplisseuse_hourly`
- **Exemple de réponse** :
```json
{
  "osmoseur": { "avg_recovery_rate": 75.3 },
  "remplisseuse": { "avg_efficiency": 92.1 }
}
```

### 2. Séries Temporelles (Graphiques)
**GET** `/analytics/series`
Données formatées pour les courbes d'évolution.
- **Params**: 
  - `metric`: Nom de la mesure (`taux_recuperation`, `rendement`, etc.)
  - `start_date`, `end_date`
  - `granularity`: `day` (défaut), `hour`, `month`
- **Source**: Jointure `fact` + `dim_time`
- **Usage frontend**: Idéal pour Recharts / Chart.js

### 3. Comparaison Techniciens
**GET** `/analytics/technician/comparison`
Classement des performances par opérateur.
- **Params**: `start_date`, `end_date`
- **Source**: Jointure `fact` + `dim_technician`

### 4. Corrélations
**GET** `/analytics/correlations`
Analyse statistique simple (Fonction SQL `CORR`).
- **Exemple**: Impact de la température sur le rendement.

## Dépendances
- Requiert que l'ETL (`/admin/run-dw-etl`) ait été exécuté au moins une fois.
- Utilise des requêtes SQL natives pour la performance OLAP.
