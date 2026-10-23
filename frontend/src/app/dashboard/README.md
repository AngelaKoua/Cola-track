# Dashboard de Management

## Vue d'Ensmeble
Le **Dashboard Manager** (`/dashboard`) est la vue principale pour le pilotage de l'usine. Il centralise les données issues du Data Warehouse.

## Fonctionnalités Clés

### 1. Filtrage Global
- Sélecteur de date (Début / Fin) en haut à droite.
- Impacte tous les KPIs et graphiques de la page.
- Bouton "Refresh" pour recharger les données depuis l'API.

### 2. Sections
- **KPI Cards** : Indicateurs macro (Rendement, Production, Arrêts).
- **Graphiques Temporels** : 
  - Courbe de rendement (Remplisseuse).
  - Courbe de taux de récupération (Osmoseur).
- **Analyse Avancée** :
  - Corrélation (ex: Température vs Rendement).
  - Qualité Eau (Osmoseur).
- **Classement Équipes** : Tableau des techniciens trié par efficacité.

## Architecture Technique
- **Source de données** : API Analytics (`/analytics/*`).
- **Composants** :
  - `components/DashboardCharts.tsx` : Graphiques Recharts encapsulés.
  - `components/TechnicianTable.tsx` : Tableau de performance.
  - `analytics/components/KPICard.tsx` : Cartes de KPI.

## Maintenance
Pour ajouter un nouveau graphique :
1. Créer le endpoint correspondant dans `backend/analytics/router.py`.
2. Ajouter le fetch dans `dashboard/page.tsx`.
3. Utiliser `TimeSeriesChart` ou créer un nouveau composant dans `DashboardCharts.tsx`.
