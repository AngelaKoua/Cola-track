# Colatrack — Frontend

Application web Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS 4 · Recharts.

## Lancer

```bash
npm install
npm run dev            # frontend (:3000) + backend (:8000) en parallèle
npm run dev:frontend   # frontend seul
npm run build && npm start
npm run lint
```

L'API est attendue sur `http://127.0.0.1:8000` (voir [src/lib/api.ts](src/lib/api.ts)).

## Structure

```text
frontend/
├── public/                  # Images statiques (logo, écran de connexion)
└── src/
    ├── app/                 # Routes (App Router)
    │   ├── page.tsx         # Page d'accueil / connexion
    │   └── dashboard/       # Espace connecté
    │       ├── page.tsx     # Tableau de bord principal
    │       ├── energy/      # Performance énergétique
    │       ├── incidents/   # Gestion des incidents
    │       ├── input/       # Saisie des mesures machines
    │       ├── iot-monitoring/
    │       ├── predictions/ # Prédictions ML et diagnostics
    │       ├── profile/
    │       └── technicians/ # Gestion des techniciens (components/, hooks/, services/ propres)
    ├── components/          # Composants réutilisables, rangés par domaine
    │   ├── layout/          # Sidebar, Header, DashboardLayout
    │   ├── ui/              # Button, Card, Input, Modal
    │   ├── dashboard/  incidents/  predictions/  forms/  notifications/  data-table/
    │   └── colaassist/      # Chatbot IA
    ├── context/             # État global (AuthContext, DataContext)
    ├── hooks/               # Hooks partagés
    ├── lib/                 # Client API, utilitaires
    ├── services/            # Appels API par domaine
    └── types/               # Types TypeScript partagés
```

L'alias `@/` pointe vers `src/` (voir [tsconfig.json](tsconfig.json)).
