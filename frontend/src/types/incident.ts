export interface Incident {
    id: string;
    date_declaration: string;
    ligne: string;
    equipement: string;
    type_incident: string;
    criticite: 'Critique' | 'Élevé' | 'Moyen' | 'Faible';
    description_probleme: string;
    cause_racine?: string;
    action_corrective?: string;
    responsable: string;
    deadline: string;
    statut: 'Ouvert' | 'En cours' | 'En attente' | 'Résolu';
    date_cloture?: string;
    temps_resolution?: any; // Interval/Duration from backend, might be string or object
}

export interface IncidentCreate {
    ligne: string;
    equipement: string;
    type_incident: string;
    criticite: string;
    description_probleme: string;
    cause_racine?: string;
    action_corrective?: string;
    responsable: string;
    deadline: string; // ISO Date YYYY-MM-DD
}

export interface IncidentUpdate {
    ligne?: string;
    equipement?: string;
    type_incident?: string;
    criticite?: string;
    description_probleme?: string;
    cause_racine?: string;
    action_corrective?: string;
    responsable?: string;
    deadline?: string;
    statut?: string;
}

export interface IncidentKPI {
    total_incidents: number;
    incidents_ouverts: number;
    incidents_critiques: number;
    mttr_moyen_heures: number;
    respect_deadline_percent: number;
}

export interface IncidentFilters {
    ligne?: string;
    statut?: string;
    criticite?: string;
    responsable?: string;
}
