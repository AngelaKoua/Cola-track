// ─────────────────────────────────────────────────────────────
// ColaAssist — Question / Answer data, structured by role and category
// ─────────────────────────────────────────────────────────────

export interface ColaAnswer {
    title: string;
    explanation: string;
    interpretation?: string;
    steps?: string[];
}

export interface ColaQuestion {
    id: string;
    label: string;
    answer: ColaAnswer;
}

export interface ColaCategory {
    id: string;
    name: string;
    icon: string;            // lucide icon name mapped in the component
    description: string;
    questions: ColaQuestion[];
}

export type ColaRole = "manager" | "technician";

// ─────────────────────────────────────────────────────────────
// SHARED categories (both roles can see these)
// ─────────────────────────────────────────────────────────────

const sharedCategories: ColaCategory[] = [
    {
        id: "indicators",
        name: "Comprendre les indicateurs",
        icon: "BarChart2",
        description: "Interprétation des KPIs et métriques affichées",
        questions: [
            {
                id: "health-index",
                label: "Comment interpréter le Health Index ?",
                answer: {
                    title: "Health Index (Indice de Santé)",
                    explanation:
                        "Le Health Index est un score global compris entre 0 et 100 qui reflète l'état de santé d'une machine. Plus le score est élevé, meilleur est l'état de la machine. Un score en dessous de 50 indique un état critique nécessitant une attention immédiate.",
                    interpretation:
                        "Sur le dashboard Prédictions, le Health Index apparaît dans la première carte de la section « État Global de la Machine ». Un badge coloré (vert, orange ou rouge) accompagne la valeur pour faciliter la lecture rapide.",
                    steps: [
                        "Aller dans le menu « Prédictions »",
                        "Sélectionner l'équipement souhaité (Osmoseur ou Remplisseuse)",
                        "Lire la carte « Health Index » dans la section « État Global de la Machine »",
                        "Vert (≥ 70) = bon état, Orange (40–69) = surveillance requise, Rouge (< 40) = intervention urgente",
                    ],
                },
            },
            {
                id: "failure-probability",
                label: "Que signifie la probabilité de panne (Failure Probability) ?",
                answer: {
                    title: "Failure Probability (Probabilité de panne à 24 h)",
                    explanation:
                        "Cet indicateur estime la probabilité qu'une panne survienne dans les 24 prochaines heures, exprimée en pourcentage. Il est calculé par le modèle IA à partir des tendances capteurs et de l'historique des incidents.",
                    interpretation:
                        "Visible dans la section « État Global de la Machine » du dashboard Prédictions. Une probabilité élevée (> 60 %) doit déclencher une inspection préventive.",
                    steps: [
                        "Naviguer vers « Prédictions »",
                        "Sélectionner l'équipement",
                        "Consulter la carte « Failure Probability »",
                        "Si la valeur est orange (> 30 %) ou rouge (> 60 %), envisager une action de maintenance",
                    ],
                },
            },
            {
                id: "quality-risk",
                label: "Comment lire le Quality Risk ?",
                answer: {
                    title: "Quality Risk (Risque Qualité)",
                    explanation:
                        "Le Quality Risk évalue la probabilité que la production en cours ne respecte pas les standards de qualité (pH, turbidité, TDS hors plage). Un risque élevé peut entraîner des rejets de lots.",
                    interpretation:
                        "Affiché dans la section « État Global » des Prédictions. Un niveau élevé signale que les paramètres physico-chimiques dérivent et que la qualité du produit est menacée.",
                },
            },
            {
                id: "alert-level",
                label: "Comment comprendre une alerte rouge (Alert Level) ?",
                answer: {
                    title: "Alert Level (Niveau d'Alerte)",
                    explanation:
                        "L'Alert Level synthétise l'ensemble des signaux (Health Index, probabilité de panne, risques qualité) en un seul niveau : Info, Warning ou Critical. Une alerte rouge (Critical) signifie que plusieurs indicateurs sont simultanément dégradés.",
                    interpretation:
                        "Carte présente dans « État Global de la Machine ». Lorsque le niveau est Critical, l'ensemble du bandeau passe en rouge pour attirer l'attention.",
                    steps: [
                        "Ouvrir « Prédictions »",
                        "Vérifier la carte « Alert Level »",
                        "Si Critical : examiner immédiatement les paramètres hors plage et les diagnostics de causes racines",
                    ],
                },
            },
            {
                id: "rul",
                label: "Que signifie le RUL (Remaining Useful Life) ?",
                answer: {
                    title: "RUL — Remaining Useful Life (Durée de Vie Utile Restante)",
                    explanation:
                        "Le RUL estime le nombre d'heures de fonctionnement restantes avant qu'une défaillance probable ne survienne. Il est calculé via un modèle prédictif basé sur les tendances de dégradation des capteurs.",
                    interpretation:
                        "Visible dans la section « Prévisions & Remaining Useful Life » du dashboard Prédictions. Utilisez cette valeur pour planifier les arrêts de maintenance préventive.",
                    steps: [
                        "Aller dans « Prédictions »",
                        "Descendre jusqu'à la section « Prévisions & Remaining Useful Life »",
                        "Lire la valeur en heures et le niveau de confiance associé",
                        "Planifier une intervention avant l'échéance estimée",
                    ],
                },
            },
            {
                id: "correlation-matrix",
                label: "Comment analyser la matrice de corrélation ?",
                answer: {
                    title: "Matrice de Corrélation",
                    explanation:
                        "La matrice de corrélation montre les liens statistiques entre les différents paramètres de production (rendement, taux de récupération, qualité de l'eau, etc.). Une corrélation forte (proche de 1 ou −1) indique que deux paramètres évoluent ensemble.",
                    interpretation:
                        "Présente sur le Dashboard principal (Pilotage), dans la section « Analyses et Tendances ». Cherchez les cellules les plus foncées pour identifier les paramètres qui s'influencent mutuellement.",
                    steps: [
                        "Aller dans « Dashboard » (Pilotage)",
                        "Descendre à la section « Analyses et Tendances »",
                        "Observer le graphique de corrélation à droite",
                        "Les couleurs intenses indiquent une forte corrélation",
                    ],
                },
            },
            {
                id: "out-of-bounds",
                label: "Comment identifier les paramètres hors plage ?",
                answer: {
                    title: "Paramètres Hors Plage (Out of Bounds)",
                    explanation:
                        "Le panneau 'Paramètres Hors Plage' liste tous les capteurs dont la valeur actuelle dépasse les seuils normaux définis. Cela permet de repérer rapidement les sources de dysfonctionnement.",
                    interpretation:
                        "Affiché dans la section « Événements & Paramètres Anormaux » du dashboard Prédictions. Chaque paramètre est comparé à sa valeur normale attendue.",
                    steps: [
                        "Ouvrir « Prédictions »",
                        "Consulter la section « Événements & Paramètres Anormaux »",
                        "Vérifier le panneau « Paramètres Hors Plage »",
                        "Agir sur les paramètres signalés en rouge",
                    ],
                },
            },
        ],
    },
    {
        id: "diagnostics",
        name: "Diagnostiquer un problème",
        icon: "Search",
        description: "Analyser les anomalies et identifier les causes",
        questions: [
            {
                id: "root-cause",
                label: "Comment utiliser l'analyse de causes racines ?",
                answer: {
                    title: "Analyse de Causes Racines (Root Cause Analysis)",
                    explanation:
                        "La section « Analyse causes racines » combine les diagnostics IA et l'importance des caractéristiques (Feature Importance) pour expliquer pourquoi la santé d'une machine se dégrade.",
                    interpretation:
                        "Accessible dans le dashboard Prédictions > section « Analyse causes racines ». Les cartes Diagnostic décrivent les problèmes détectés, tandis que le graphique Feature Importance montre quels paramètres pèsent le plus dans la prédiction.",
                    steps: [
                        "Ouvrir « Prédictions »",
                        "Descendre à « Analyse causes racines »",
                        "Lire les cartes de diagnostic à gauche (problèmes identifiés)",
                        "Consulter le graphique Feature Importance à droite (paramètres influents)",
                        "Croiser les deux pour comprendre la source du problème",
                    ],
                },
            },
            {
                id: "anomalies-table",
                label: "Comment lire la table des anomalies détectées ?",
                answer: {
                    title: "Table des Anomalies",
                    explanation:
                        "La table des anomalies liste les événements inhabituels détectés dans l'historique récent de la machine. Chaque ligne décrit le type d'anomalie, le paramètre concerné et l'horodatage.",
                    interpretation:
                        "Visible dans « Prédictions » > « Événements & Paramètres Anormaux ». Les anomalies récurrentes signalent un dysfonctionnement progressif.",
                    steps: [
                        "Naviguer vers « Prédictions »",
                        "Section « Événements & Paramètres Anormaux »",
                        "Consulter le tableau des anomalies",
                        "Si une anomalie se répète, prévoir une maintenance ciblée",
                    ],
                },
            },
            {
                id: "sensor-trends",
                label: "Comment interpréter les tendances capteurs ?",
                answer: {
                    title: "Tendances Capteurs (Sensor Trends)",
                    explanation:
                        "Les courbes de tendance montrent l'évolution des valeurs capteurs sur les dernières heures. Une dérive continue signale une dégradation progressive.",
                    interpretation:
                        "Accessible dans « Prédictions » > section « Tendances Capteurs & Dégradation ». Comparez les courbes au graphique RUL pour anticiper le moment critique.",
                    steps: [
                        "Ouvrir « Prédictions »",
                        "Descendre à « Tendances Capteurs & Dégradation »",
                        "Observer la direction des courbes",
                        "Une tendance montante ou descendante continue = dégradation à surveiller",
                    ],
                },
            },
            {
                id: "degradation-velocity",
                label: "Que signifie la Degradation Velocity ?",
                answer: {
                    title: "Degradation Velocity (Vitesse de Dégradation)",
                    explanation:
                        "Ce badge indique la vitesse à laquelle l'état de la machine se dégrade. Une vitesse élevée signifie que la machine approche rapidement d'un seuil critique.",
                    interpretation:
                        "Affiché juste sous les cartes « État Global de la Machine » dans les Prédictions. Combiné au RUL, il permet de prioriser l'urgence d'une intervention.",
                },
            },
        ],
    },
    {
        id: "incidents",
        name: "Gestion des incidents",
        icon: "ClipboardList",
        description: "Créer, suivre et résoudre les incidents",
        questions: [
            {
                id: "create-incident",
                label: "Comment ajouter un incident ?",
                answer: {
                    title: "Créer un Nouvel Incident",
                    explanation:
                        "La création d'incident permet de documenter un problème détecté sur un équipement afin d'en assurer le suivi et la résolution.",
                    steps: [
                        "Aller dans le menu « Incidents »",
                        "Cliquer sur le bouton « Nouvel incident » en haut à droite",
                        "Remplir le formulaire : sélectionner l'équipement, décrire le problème, définir la priorité",
                        "Cliquer sur « Enregistrer » pour valider",
                        "L'incident apparaît dans la liste avec le statut « Ouvert »",
                    ],
                },
            },
            {
                id: "resolve-incident",
                label: "Comment résoudre un incident ?",
                answer: {
                    title: "Résoudre un Incident",
                    explanation:
                        "Une fois le problème corrigé sur le terrain, l'incident doit être marqué comme résolu pour actualiser les KPIs de maintenance.",
                    steps: [
                        "Aller dans « Incidents »",
                        "Localiser l'incident dans le tableau",
                        "Cliquer sur le bouton « Résoudre » (icône check)",
                        "L'incident passe au statut « Résolu » et le MTTR est calculé automatiquement",
                    ],
                },
            },
            {
                id: "view-incident",
                label: "Comment consulter le détail d'un incident ?",
                answer: {
                    title: "Voir le Détail d'un Incident",
                    explanation:
                        "Chaque incident peut être ouvert en lecture seule pour consulter l'ensemble des informations sans risque de modification.",
                    steps: [
                        "Aller dans « Incidents »",
                        "Cliquer sur le bouton « Voir » sur la ligne de l'incident",
                        "Un modal s'ouvre avec tous les détails (équipement, description, priorité, dates)",
                        "Fermer le modal pour revenir à la liste",
                    ],
                },
            },
            {
                id: "filter-incidents",
                label: "Comment filtrer les incidents ?",
                answer: {
                    title: "Filtrer les Incidents",
                    explanation:
                        "La barre de filtres permet de restreindre la liste des incidents selon différents critères pour retrouver rapidement un incident spécifique.",
                    steps: [
                        "Aller dans « Incidents »",
                        "Utiliser la barre de filtres au-dessus du tableau",
                        "Filtrer par statut, priorité, équipement ou plage de dates",
                        "Les résultats se mettent à jour automatiquement",
                    ],
                },
            },
            {
                id: "incident-kpis",
                label: "Comment interpréter les KPIs des incidents (MTTR, Deadline) ?",
                answer: {
                    title: "KPIs de Gestion des Incidents",
                    explanation:
                        "Les 4 cartes KPI en haut de la page Incidents résument la performance de maintenance : Total Incidents, Incidents Ouverts, MTTR Moyen (Mean Time To Repair) et Respect Deadline.",
                    interpretation:
                        "Le MTTR mesure le temps moyen de résolution en heures. Le Respect Deadline indique le pourcentage d'incidents résolus dans les délais (objectif > 90 %). Un MTTR élevé ou un faible respect des deadlines signale un besoin de renfort ou de réorganisation.",
                },
            },
        ],
    },
    {
        id: "platform",
        name: "Utiliser la plateforme",
        icon: "Monitor",
        description: "Navigation, filtres et fonctionnalités générales",
        questions: [
            {
                id: "navigate",
                label: "Comment naviguer dans la plateforme ?",
                answer: {
                    title: "Navigation dans Colatrack",
                    explanation:
                        "La navigation principale se fait via la barre latérale (sidebar) à gauche. Les éléments du menu visibles dépendent de votre rôle (Manager ou Technicien).",
                    steps: [
                        "Sur ordinateur : la sidebar est toujours visible à gauche",
                        "Sur mobile : cliquer sur l'icône burger en haut à gauche pour ouvrir le menu",
                        "Cliquer sur un élément du menu pour accéder à la page correspondante",
                        "La page active est mise en surbrillance dans le menu",
                    ],
                },
            },
            {
                id: "filter-data",
                label: "Comment filtrer les données affichées ?",
                answer: {
                    title: "Filtrage des Données",
                    explanation:
                        "La plupart des dashboards proposent des filtres (dates, équipement, statut) pour affiner les données affichées.",
                    steps: [
                        "Sur le Dashboard principal : utiliser le sélecteur d'équipement et les champs de dates en haut de page",
                        "Sur la page Incidents : utiliser la barre de filtres (statut, priorité, dates)",
                        "Sur Saisie Données : utiliser le filtre par date dans la vue Tableau",
                        "Les données se mettent à jour automatiquement après chaque changement de filtre",
                    ],
                },
            },
            {
                id: "change-password",
                label: "Comment modifier mon mot de passe ?",
                answer: {
                    title: "Modification du Mot de Passe",
                    explanation:
                        "Vous pouvez modifier votre mot de passe depuis votre page de profil.",
                    steps: [
                        "Cliquer sur votre avatar ou nom d'utilisateur dans le header",
                        "Accéder à la page « Profil »",
                        "Remplir les champs Ancien mot de passe, Nouveau mot de passe, Confirmation",
                        "Cliquer sur « Enregistrer »",
                    ],
                },
            },
            {
                id: "logout",
                label: "Comment me déconnecter ?",
                answer: {
                    title: "Déconnexion",
                    explanation:
                        "Le bouton de déconnexion est accessible depuis la barre latérale.",
                    steps: [
                        "Cliquer sur le bouton « Déconnexion » en rouge en bas de la sidebar",
                        "Vous êtes redirigé vers la page de connexion",
                    ],
                },
            },
        ],
    },
];

// ─────────────────────────────────────────────────────────────
// TECHNICIAN-ONLY categories
// ─────────────────────────────────────────────────────────────

const technicianCategories: ColaCategory[] = [
    {
        id: "data-entry",
        name: "Saisie de données",
        icon: "PenLine",
        description: "Saisir et gérer les relevés de production",
        questions: [
            {
                id: "add-osmoseur",
                label: "Comment saisir un relevé Osmoseur ?",
                answer: {
                    title: "Saisie d'un Relevé Osmoseur",
                    explanation:
                        "Les techniciens saisissent quotidiennement les données de l'osmoseur (débits, conductivité, pH, etc.) via un formulaire dédié.",
                    steps: [
                        "Aller dans « Saisie Données »",
                        "Vérifier que l'onglet « Osmoseur » est sélectionné",
                        "Rester en mode « Saisie » (bouton en haut à droite)",
                        "Remplir les champs : Débit Perméat, Débit Concentrat, Taux Récupération, Conductivité, pH Entrée, pH Sortie, Turbidité, Chlore, Dureté, TDS",
                        "Cliquer sur « Enregistrer »",
                    ],
                },
            },
            {
                id: "add-remplisseuse",
                label: "Comment saisir un relevé Remplisseuse ?",
                answer: {
                    title: "Saisie d'un Relevé Remplisseuse",
                    explanation:
                        "Le formulaire Remplisseuse collecte les données de la ligne de remplissage (température, volume, carbonation, rendement, etc.).",
                    steps: [
                        "Aller dans « Saisie Données »",
                        "Sélectionner l'onglet « Remplisseuse »",
                        "Remplir les champs : Température, Volume, CO₂, Unités Conformes, Heures Arrêt, MTBF, Rendement, Consommation Air/CO₂, Vibrations",
                        "Cliquer sur « Enregistrer »",
                    ],
                },
            },
            {
                id: "edit-record",
                label: "Comment modifier un relevé existant ?",
                answer: {
                    title: "Modifier un Relevé",
                    explanation:
                        "Les relevés déjà saisis peuvent être modifiés si une erreur a été commise.",
                    steps: [
                        "Aller dans « Saisie Données »",
                        "Passer en vue « Tableau » avec le bouton en haut à droite",
                        "Localiser la ligne à modifier",
                        "Cliquer sur le bouton « Modifier » (icône crayon)",
                        "Le formulaire s'ouvre pré-rempli avec les données existantes",
                        "Corriger les valeurs puis cliquer sur « Enregistrer »",
                    ],
                },
            },
            {
                id: "delete-record",
                label: "Comment supprimer un relevé ?",
                answer: {
                    title: "Supprimer un Relevé",
                    explanation:
                        "Un relevé erroné peut être supprimé définitivement du système.",
                    steps: [
                        "Aller dans « Saisie Données »",
                        "Passer en vue « Tableau »",
                        "Localiser la ligne à supprimer",
                        "Cliquer sur le bouton « Supprimer » (icône poubelle)",
                        "Confirmer la suppression dans la boîte de dialogue",
                    ],
                },
            },
        ],
    },
    {
        id: "iot",
        name: "Monitoring IoT",
        icon: "Radio",
        description: "Surveillance temps-réel des capteurs",
        questions: [
            {
                id: "iot-status",
                label: "Que signifie le statut Connecté / Déconnecté ?",
                answer: {
                    title: "Statut de Connexion IoT",
                    explanation:
                        "Le badge de statut en haut de la page IoT Monitoring indique si le capteur ESP32 communique avec le serveur. « Connecté » signifie que des données sont reçues en temps réel. « Déconnecté » signifie que le capteur ne transmet plus.",
                    interpretation:
                        "Si le statut est « Déconnecté », vérifiez la connexion Wi-Fi du capteur, son alimentation et le serveur backend.",
                },
            },
            {
                id: "iot-metrics",
                label: "Comment lire les valeurs actuelles des capteurs ?",
                answer: {
                    title: "Valeurs Actuelles IoT",
                    explanation:
                        "La section « Valeurs Actuelles » affiche 6 métriques en temps réel : Débit Entrée (L/h), Turbidité Entrée (NTU), pH, TDS (ppm), Débit Sortie (L/h), Turbidité Sortie (NTU).",
                    interpretation:
                        "Les valeurs sont mises à jour toutes les 3 secondes. Si une valeur affiche « — », aucune donnée n'a encore été reçue.",
                    steps: [
                        "Aller dans « IoT Monitoring »",
                        "Consulter les 6 cartes de métriques dans « Valeurs Actuelles »",
                        "Comparer avec les seuils attendus",
                    ],
                },
            },
            {
                id: "iot-charts",
                label: "Comment utiliser les courbes temps-réel ?",
                answer: {
                    title: "Courbes Temps-Réel IoT",
                    explanation:
                        "Le graphique affiche les 5 dernières minutes de données pour pH, TDS, Turbidité Entrée et Turbidité Sortie. Il permet de détecter visuellement les pics ou les dérives soudaines.",
                    steps: [
                        "Aller dans « IoT Monitoring »",
                        "Descendre jusqu'à « Courbes Temps-Réel »",
                        "Survoler une courbe pour voir la valeur exacte à un instant donné",
                        "Observer les tendances : un pic soudain peut indiquer un problème ponctuel",
                    ],
                },
            },
        ],
    },
];

// ─────────────────────────────────────────────────────────────
// MANAGER-ONLY categories
// ─────────────────────────────────────────────────────────────

const managerCategories: ColaCategory[] = [
    {
        id: "admin",
        name: "Administration",
        icon: "Shield",
        description: "Gestion des techniciens et supervision",
        questions: [
            {
                id: "create-technician",
                label: "Comment créer un compte technicien ?",
                answer: {
                    title: "Créer un Compte Technicien",
                    explanation:
                        "Les managers peuvent créer des comptes pour les nouveaux techniciens directement depuis la plateforme.",
                    steps: [
                        "Aller dans « Gestion Techniciens »",
                        "Cliquer sur « Ajouter un technicien »",
                        "Saisir le nom d'utilisateur et l'adresse email",
                        "Valider la création",
                        "Un mot de passe par défaut est généré et doit être communiqué au technicien",
                    ],
                },
            },
            {
                id: "toggle-technician",
                label: "Comment activer / désactiver un technicien ?",
                answer: {
                    title: "Activer ou Désactiver un Compte",
                    explanation:
                        "Un compte désactivé empêche le technicien de se connecter sans supprimer ses données historiques.",
                    steps: [
                        "Aller dans « Gestion Techniciens »",
                        "Localiser le technicien dans le tableau",
                        "Cliquer sur le bouton « Activer » ou « Désactiver »",
                        "Le statut se met à jour immédiatement",
                    ],
                },
            },
            {
                id: "delete-technician",
                label: "Comment supprimer un technicien ?",
                answer: {
                    title: "Supprimer un Compte Technicien",
                    explanation:
                        "La suppression est définitive. Utilisez-la uniquement si le compte ne doit plus exister. Préférez la désactivation pour une suspension temporaire.",
                    steps: [
                        "Aller dans « Gestion Techniciens »",
                        "Cliquer sur le bouton « Supprimer » (icône poubelle) sur la ligne du technicien",
                        "Confirmer la suppression dans la boîte de dialogue",
                    ],
                },
            },
            {
                id: "view-technician-detail",
                label: "Comment voir le détail d'un technicien ?",
                answer: {
                    title: "Détail d'un Technicien",
                    explanation:
                        "Le modal Détail affiche les informations du technicien ainsi que ses statistiques d'activité (saisies effectuées, incidents traités, etc.).",
                    steps: [
                        "Aller dans « Gestion Techniciens »",
                        "Cliquer sur le bouton « Voir détail » sur la ligne du technicien",
                        "Un modal s'ouvre avec les statistiques et l'historique d'activité",
                    ],
                },
            },
            {
                id: "technician-kpis",
                label: "Comment lire les indicateurs de synthèse des techniciens ?",
                answer: {
                    title: "KPIs de Gestion Techniciens",
                    explanation:
                        "Les cartes en haut de la page « Gestion Techniciens » affichent le nombre total de techniciens, les comptes actifs/inactifs et d'autres métriques de synthèse sur la période sélectionnée (30 jours par défaut).",
                },
            },
        ],
    },
    {
        id: "dashboard-kpis",
        name: "Dashboard Pilotage",
        icon: "LayoutDashboard",
        description: "Comprendre le tableau de bord principal",
        questions: [
            {
                id: "rendement-global",
                label: "Comment interpréter le Rendement Global ?",
                answer: {
                    title: "Rendement Global",
                    explanation:
                        "Le Rendement Global mesure l'efficacité de la production en pourcentage. Il compare la production effective à la capacité théorique de la ligne.",
                    interpretation:
                        "Affiché dans la section « Indicateurs Clés » du Dashboard. Un rendement en baisse signale des arrêts fréquents, des pannes ou une perte d'efficacité.",
                    steps: [
                        "Aller dans « Dashboard » (Pilotage)",
                        "Consulter la première carte « Rendement Global » dans « Indicateurs Clés »",
                        "Comparer à la cible affichée sous la valeur",
                    ],
                },
            },
            {
                id: "temps-arret",
                label: "Que signifie le Temps d'Arrêt ?",
                answer: {
                    title: "Temps d'Arrêt",
                    explanation:
                        "Le Temps d'Arrêt totalise les heures d'indisponibilité des équipements sur la période filtrée. Un temps d'arrêt élevé est corrélé à un faible rendement.",
                    interpretation:
                        "Carte visible dans « Indicateurs Clés » du Dashboard. Croisez cette valeur avec le MTTR des incidents pour identifier les causes principales d'arrêt.",
                },
            },
            {
                id: "rendement-chart",
                label: "Comment lire la courbe d'évolution du rendement ?",
                answer: {
                    title: "Évolution du Rendement",
                    explanation:
                        "Le graphique linéaire montre le rendement quotidien sur la période sélectionnée. Il permet de repérer les tendances à la baisse et les jours critiques.",
                    steps: [
                        "Aller dans « Dashboard »",
                        "Section « Analyses et Tendances »",
                        "Survoler la courbe pour voir les valeurs exactes jour par jour",
                    ],
                },
            },
        ],
    },
];

// ─────────────────────────────────────────────────────────────
// Exported lookup
// ─────────────────────────────────────────────────────────────

export function getCategoriesForRole(role: ColaRole): ColaCategory[] {
    if (role === "manager") {
        return [...sharedCategories, ...managerCategories];
    }
    return [...sharedCategories, ...technicianCategories];
}
