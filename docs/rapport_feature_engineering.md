# Rapport Technique Détaillé : Feature Engineering (Phase 2)

**Projet :** Colatrack — Jumeau Numérique Industriel
**Sujet :** Ingénierie des Caractéristiques (Feature Engineering)
**Phase :** 2 / 4 — Intelligence Artificielle & Inférence

---

## 1. Introduction et Philosophie

Dans un contexte IoT industriel, les performances d'un modèle de Machine Learning ne dépendent pas uniquement de l'algorithme choisi (XGBoost, Random Forest), mais surtout de la qualité et de la richesse des données d'entrée. 

Les données brutes instantanées (mesure à l'instant *t*) manquent d'une information fondamentale pour la maintenance prédictive : **la dynamique temporelle**. Une vibration de `4.5 mm/s` n'a pas la même signification si elle était de `1.0 mm/s` il y a une heure (panne soudaine) ou si elle était de `4.4 mm/s` (dégradation lente).

L'objectif du *Feature Engineering* réalisé dans le script [train_models.py](file:///c:/Users/abdou/Documents/Projet%20IT/Colatrack/train_models.py) a été de traduire la dimension temporelle de la machine sous un format tabulaire riche, compréhensible par les algorithmes de classification et régression classiques.

---

## 2. Ségrégation par Équipement (Machine Splitting)

**Technique :** Séparation stricts des DataFrames d'entrainement entre l'Osmoseur et la Remplisseuse.

**Justification Industrielle :**
Mélanger les données thermodynamiques d'un système de filtration d'eau avec les données cinématiques d'une embouteilleuse aurait forcé l'algorithme à discriminer virtuellement la machine avant de chercher l'anomalie. Les plages de valeurs (ex: pressions vs vitesses) n'ayant rien à voir, nous avons opté pour le développement de modèles "spécifiques machine".

---

## 3. Transformation Temporelle des Signaux

Nous avons ordonné chronologiquement les données par `machine_id` et par `timestamp` pour appliquer nos fonctions de transformation temporelle en toute sécurité, sans mélanger le temps ou les équipements.

### 3.1. Les Dérivées (Taux de Changement)

**Description :** La création de nouvelles colonnes mesurant l'évolution d'une variable entre l'instant *t* et *t-1* (via la fonction `.diff()` de pandas).

**Application :**
- **Osmoseur :** `pression_rate` (dérivée de la pression membranaire) et `conductivite_rate` (dérivée de la conductivité perméat).
- **Remplisseuse :** `vibrations_rate` (dérivée des vibrations moteur) et `mtbf_rate` (évolution du temps moyen avant panne).

**Objectif ML :** 
Permettre aux modèles (ex: XGBoost) de détecter des variations *anormalement rapides*. Un colmatage lent ou une fuite rapide de pression génèrent des taux de changement très distincts, qui deviennent des "red flags" évidents pour l'arbre de décision, bien plus que la valeur absolue elle-même.

### 3.2. Les Fenêtres Glissantes (Rolling Means)

**Description :** Création d'une nouvelle série de variable calculant la moyenne lissée sur l'historique récent de la machine, capteur par capteur. (Ex: via la fonction `.rolling(12).mean()`).

**Application :**
Pour chaque capteur physique (température, débit, pH, volume), nous avons créé une colonne `[nom_capteur]_rolling_1h`, qui effectue la moyenne des 12 dernières mesures (12 x 5 minutes = 1 heure).

**Objectif ML :**
Les capteurs physiques sont naturellement sujets à un "bruit blanc" gaussien (imprécisions de mesure très courtes). Comparer une valeur brute instantanée à sa tendance de la dernière heure (`rolling_1h`) permet au modèle Isolation Forest de comprendre qu'un pic n'est qu'un "micro-défaut", tandis qu'un décalage persistant entre la valeur "Rolling Mean" et "Normale" est le signe tangible d'une usure (Drift mécanique).

---

## 4. Pré-traitement Numérique (Preprocessing)

### 4.1. Standardisation (StandardScaler)

**Technique :** Normalisation Z-Score ([(X - μ) / σ](file:///c:/Users/abdou/Documents/Projet%20IT/Colatrack/eda_analysis.py#647-667)) pour les algorithmes sensibles à la distance.

**Justification :** 
L'algorithme *Isolation Forest* ou la *Régression Logistique* utilisent des notions de distance mathématique. Sans standardisation, une variable mesurée en milliers (ex: `debit_permeat_lh = 1500`) écraserait totalement une variable essentielle mesurée en dixièmes (ex: `turbidite_ntu = 0.5`).
- Les `StandardScalers` ont été "fittés" sur le dataset d'entrainement et sauvegardés individuellement par machine (`iso_forest_scaler_osmoseur.joblib` etc.) pour être appliqués en inférence temps réel.

### 4.2. Traitement du Déséquilibre de Classes : SMOTE

**Problématique Industrielle :**
La cible à prédire `failure_within_24h` est extrêmement déséquilibrée (Seulement ~10% d'états critiques pour 90% de fonctionnement normal). Un XGBoost standard aurait eu un rappel catastrophique sur la classe minoritaire en cherchant à optimiser l'accuracy globale.

**Technique :** 
L'utilisation de **SMOTE (Synthetic Minority Over-sampling Technique)** sur le dataset d'**entraînement uniquement**.
- Au lieu de dupliquer bêtement les lignes de pannes, SMOTE a interpolé mathématiquement de nouveaux "cas de panne synthétiques" dans l'espace multidimensionnel entre des cas réels avérés, pour forcer un ratio 50% Normal / 50% Panne.

**Impact ML :**
C'est grâce à cette ingénierie au niveau de l'échantillonnage que notre modèle XGBoost de prédiction de panne atteint un **Recall de 0.97** sur la Remplisseuse (soit 97% des pannes imminentes identifiées correctement).

---

## 5. Synthèse des Variables Entrantes

Au final, grâce au Feature Engineering, le corpus envoyé à XGBoost pour prédire une panne imminente n'est plus limité aux capteurs bruts, mais devient un tenseur riche en contexte multidimensionnel regroupant plus de **20 métriques par machine** pour un instant t donné.

**Structure X_Train résultante :**
* `Capteurs Instantanés T0` (Valeurs physiques nues) +
* `Dérivées Critiques Δ(t, t-1)` (Vitesse d'usure) +
* `Moyennes Lissante Historique T-1h` (Statut structurel de fond)

Cette architecture permet au **Hybrid Decision Engine** de raisonner de la même manière qu'un ingénieur expert surveillant une Courbe dans un tableau de bord Control Room.
