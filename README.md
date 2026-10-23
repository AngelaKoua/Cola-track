# Colatrack (CTrack)

Plateforme de supervision industrielle et de maintenance prédictive pour une ligne
d'embouteillage Coca-Cola. Elle suit deux machines :

- **Osmoseur** : traitement de l'eau par osmose inverse
- **Remplisseuse** : remplissage des bouteilles

Fonctionnalités : saisie et suivi des mesures, monitoring IoT, gestion des incidents
et des techniciens, notifications temps réel, prédictions ML (anomalies, panne à 24 h,
indice de santé, qualité), assistant IA (Gemini) et tableaux de bord BI.

## Organisation du projet

```text
Cola-track/
├── frontend/        → Application web Next.js (React, TypeScript, Tailwind)
├── backend/         → API FastAPI (Python, PostgreSQL, moteur IA, data warehouse)
├── data-science/    → Génération du dataset, analyse exploratoire, entraînement des modèles ML
├── docs/            → Rapports (EDA, feature engineering) et support de présentation
└── _archive/        → Logs de debug et doublons mis de côté (ignoré par git, supprimable)
```

| Dossier | Contenu | Documentation |
| --- | --- | --- |
| [frontend/](frontend/) | Pages (`src/app/`), composants (`src/components/`), appels API (`src/services/`, `src/lib/`) | [frontend/README.md](frontend/README.md) |
| [backend/](backend/) | API (`app/`), BI (`analytics/`), ETL (`datawarehouse/`), scripts utilitaires (`scripts/`) | [backend/README.md](backend/README.md) |
| [data-science/](data-science/) | Pipeline dataset → EDA → entraînement des modèles | [data-science/README.md](data-science/README.md) |
| [docs/](docs/) | Rapports Markdown/PDF | — |

## Architecture

```text
 Navigateur ──► frontend (Next.js :3000)
                    │  REST + WebSocket
                    ▼
               backend (FastAPI :8000) ──► PostgreSQL
                    │                        ├─ tables opérationnelles (osmoseur, remplisseuse, incidents…)
                    │                        ├─ schéma iot   (lectures capteurs)
                    │                        └─ schéma dw    (data warehouse en étoile, alimenté par l'ETL)
                    ├─► modèles ML (backend/app/ml_models/*.joblib)
                    └─► API Gemini (chatbot ColaAssist)

 data-science/train_models.py ──► écrit les modèles dans backend/app/ml_models/
```

## Démarrage rapide

Prérequis : Node.js ≥ 22, Python ≥ 3.10, PostgreSQL.

```bash
# 1. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/Mac : source .venv/bin/activate)
pip install -r requirements.txt
copy env.example .env           # puis renseigner DATABASE_URL, SECRET_KEY, GEMINI_API_KEY

# 2. Frontend
cd ../frontend
npm install

# 3. Lancer les deux en même temps (depuis frontend/)
npm run dev
```

- Application : <http://localhost:3000>
- Documentation de l'API : <http://localhost:8000/docs>

Le backend se lance aussi seul avec `uvicorn app.main:app --reload` depuis `backend/`.
