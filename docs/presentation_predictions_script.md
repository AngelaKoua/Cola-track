# Présentation : Page "Prédictions et Aide à la Décision"

Ce document contient à la fois un rapport détaillé expliquant la structure de la page et un script oral prêt à être utilisé lors d'une soutenance devant un jury.

---

## PARTIE 1 : Rapport Explicatif de la Page Haut Niveau

La page **"Prédictions et aide à la décision"** est le cœur de l'intelligence artificielle (IA) au sein de l'application Colatrack. Elle permet aux opérateurs et aux décideurs de passer d'une maintenance réactive à une maintenance **prédictive et proactive**. 

La page est divisée en 6 sections logiques, conçues comme un entonnoir : on part de la vision globale de la machine pour aller vers le diagnostic précis, pour terminer par la recommandation d'action.

### 1. En-tête : Sélection de l'équipement
L'utilisateur peut cibler précisément l'équipement à analyser (ex: l'Osmoseur `OSM-001` ou la Remplisseuse `RMP-001`). Les données de la page se mettent à jour dynamiquement toutes les 30 secondes pour garantir une surveillance en temps réel.

### 2. Section 1 - État Global de la Machine (Situation Awareness)
Cette section donne immédiatement le "pouls" de la machine grâce à 4 KPI critiques :
- **Indice de Santé (Health Index)** : Un score global de la vitalité de l'équipement.
- **Probabilité de panne (Failure Probability 24h)** : Le risque qu'une panne sévère survienne dans les prochaines 24 heures.
- **Risque Qualité (Quality Risk)** : L'impact potentiel de l'état de la machine sur la qualité de l'eau ou du produit final.
- **Niveau d'Alerte (Alert Level)** : L'urgence de la situation (Normal, Attention, Critique).
- **Vitesse de dégradation** : Un badge indiquant si la machine se dégrade lentement ou rapidement.

### 3. Section 2 - Événements & Paramètres Anormaux (Anomalies)
Si l'état global indique un problème, cette section montre *où* regarder :
- **Panneau Hors Normes (Out Of Bounds)** : Met en évidence les capteurs qui dépassent les seuils normaux établis.
- **Tableau des Anomalies** : Un historique récent des comportements anormaux détectés par l'IA.
- **Timeline chronologique** : Retrace les événements historiques marquants pour contextualiser la situation.

### 4. Section 3 - Analyse Causes Racines (Root Cause Analysis)
Ici, l'IA explique *pourquoi* il y a une anomalie (Explicabilité de l'IA / XAI) :
- **Cartes de Diagnostic** : Hypothèses formulées par l'algorithme sur la nature exacte du problème.
- **Importance des Variables (Feature Importance)** : Un graphique montrant quel capteur contribue le plus à l'alerte actuelle (ex: "La pression de la pompe est responsable à 60% de l'alerte").
- **Comparaison avec la Normale** : Un tableau croisé permettant de voir l'écart direct entre les valeurs actuelles et le comportement attendu (baseline).

### 5. Section 4 & 5 - Tendances et Prévisions (Prognostics & RUL)
L'IA se projette dans le futur :
- **Courbes de Tendance (Sensor Trends)** : L'évolution des capteurs dans le temps.
- **RUL (Remaining Useful Life)** : L'Estimation de la Durée de Vie Utile Restante. C'est la métrique reine de la maintenance prédictive. Elle indique combien de temps (en heures ou cycles) la machine peut encore fonctionner avant la panne.
- **Prévision des Paramètres** : Un tableau prospectif montrant comment les métriques vont évoluer dans les prochaines heures (tendance à la hausse, à la baisse).

### 6. Section 6 - Aide à la Décision (Recommandations)
La conclusion de l'entonnoir. L'IA ne laisse pas l'opérateur seul avec des graphiques : elle prescrit des actions claires.
- **Cartes de recommandations** : Actions de maintenance suggérées (ex: "Nettoyer les membranes", "Vérifier la valve"), adaptées à la cause racine détectée.

---

## PARTIE 2 : Script Oral pour la Soutenance (Devant le Jury)

*(Instructions pour l'orateur : Parlez de manière posée. Laissez des blancs de 1 ou 2 secondes entre les sections pour que le jury assimile. Pointez les éléments à l'écran si vous faites une démo en direct).*

**[Introduction]**
"Mesdames et Messieurs les membres du jury, nous voici à présent sur l'une des pages les plus critiques de notre solution Colatrack : le module **Prédictions et Aide à la décision**. 
C'est ici que l'Intelligence Artificielle de notre système prend tout son sens. L'objectif de cet écran n'est pas seulement d'afficher de la donnée brute, mais de **transformer cette donnée en actions concrètes** pour nos équipes de maintenance. 

Découvrons ensemble comment cet écran accompagne l'opérateur dans sa prise de décision, étape par étape."

**[Sélection & État Global]**
"En haut de la page, nous sélectionnons l'équipement ciblé, par exemple l'Osmoseur. L'IA charge alors son analyse en temps réel.
Immédiatement, la première ligne que vous voyez donne ce que nous appelons la 'Situation Awareness', c'est-à-dire le **pouls de la machine**. Plutôt que d'obliger le technicien à analyser 50 capteurs, l'IA lui résume la situation en 4 scores vitaux : l'indice de santé global, la probabilité de panne dans les prochaines 24h, le risque d'impact sur la qualité de notre production, et enfin le niveau d'alerte général. En un coup d'œil, on sait s'il y a urgence."

**[Anomalies & Contexte]**
"Si l'un de ces indicateurs passe au rouge, la question suivante de l'opérateur sera : *'Qu'est-ce qui cloche ?'* 
C'est précisément le rôle de la deuxième section. Elle isole instantanément les **Paramètres Anormaux**. Le système fait remonter les capteurs qui présentent des valeurs hors normes par rapport à leur comportement habituel, avec une frise chronologique qui retrace les événements récents. Cela donne tout le contexte nécessaire à l'opérateur."

**[Explicabilité de l'IA (Cause Racine)]**
"Mais nous avons voulu aller plus loin, pour éviter l'effet 'boîte noire' de l'Intelligence Artificielle. C'est l'objectif de notre 3ème section : **l'Analyse des causes racines**.
Ici, l'IA explique *pourquoi* elle a déclenché une alerte. Le graphique d'importance des variables montre très concrètement quel capteur pèse le plus dans la dégradation. Complété par les diagnostics générés, cela permet à l'équipe de savoir exactement où chercher la panne."

**[Prévisions & RUL]**
"Ensuite, nous passons de l'analyse du présent à la **prévision du futur**.
Dans cette section, vous retrouvez la métrique clé de la maintenance prédictive : le **R.U.L** (Remaining Useful Life), ou Durée de Vie Utile Restante. L'algorithme calcule le temps exact qu'il nous reste avant une défaillance critique. Nous affichons également les tendances projetées de nos capteurs critiques pour les prochaines heures, ce qui permet d'anticiper la dégradation physique de l'équipement."

**[Aide à la décision / Recommandation]**
"Enfin, nous arrivons au but ultime de la page : **L'Aide à la Décision**. 
Toutes les données, anomalies et prévisions précédentes convergent vers cette dernière section sous forme de Recommandations de Maintenance claires et prescriptives. L'opérateur n'a plus à deviner l'action appropriée : le système lui suggère l'intervention optimale, au moment idéal, pour éviter l'arrêt de production."

**[Conclusion]**
"En résumé, cet écran incarne notre vision pour Colatrack : rendre la donnée complexe accessible, explicable, et surtout, directement exploitable pour garantir l'efficacité de l'outil industriel."
