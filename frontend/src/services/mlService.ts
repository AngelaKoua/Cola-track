import { API_BASE } from '@/lib/config'
const API_URL = API_BASE;

// ==============================================================================
// EXISTING INTERFACES
// ==============================================================================

export interface MLPrediction {
    id: string;
    timestamp: string;
    machine_id: string;
    health_index: number;
    failure_probability_24h: number;
    quality_risk: number | null;
    is_anomaly: boolean;
    alert_level: number;
    reason: string;
}

export interface HistoricalRUL {
    timestamp: string;
    health_index: number;
    failure_probability: number;
    alert_level: number;
}

export interface TimelineEvent {
    type: string;
    timestamp: string;
    title: string;
    severity: string;
    description: string;
    status: string;
}

export interface ComparisonMetric {
    parameter: string;
    normal: number;
    current: number;
    delta_pct: number;
}

export interface SensorTrend {
    timestamp: string;
    debit?: number;
    conductivite?: number;
    tds?: number;
    taux_recuperation?: number;
    volume?: number;
    vibrations?: number;
    temperature?: number;
    carbonation?: number;
}

// ==============================================================================
// NEW INTERFACES — LAYERED AI ARCHITECTURE
// ==============================================================================

// Layer 3 — Diagnosis
export interface DiagnosisEvidence {
    parameter: string;
    expected: string;
    actual: string;
    match: boolean;
    current_value: number | null;
}

export interface Diagnosis {
    diagnosis: string;
    description: string;
    confidence: number;
    matched_conditions: number;
    total_conditions: number;
    severity: string;
    recommended_action: string;
    rul_impact: string;
    evidence: DiagnosisEvidence[];
}

export interface AnomalyParameter {
    name: string;
    value: number;
    z_score: number;
    is_anomalous: boolean;
    direction: string;
    baseline_mean: number;
    baseline_std: number;
    unit: string;
    deviation_pct: number;
}

export interface DiagnosisResponse {
    diagnoses: Diagnosis[];
    anomalies: {
        total_anomalies: number;
        parameters: AnomalyParameter[];
    };
}

// Layer 4 — Prognostics / Forecast
export interface ForecastData {
    timestamp: string;
    forecasted_health: number;
}

export interface ParameterForecast {
    parameter: string;
    current_value: number;
    trend_slope: number;
    trend_direction: string;
    forecasts: Record<string, number>;
}

export interface RULEstimate {
    current_health: number;
    degradation_velocity_per_hour: number;
    hours_to_warning: number | null;
    hours_to_critical: number | null;
    risk_level: string;
    velocity_label: string;
}

export interface ForecastResponse {
    parameter_forecasts: ParameterForecast[];
    rul: RULEstimate;
}

// Layer 5 — Decision Support
export interface Recommendation {
    priority: string;
    action_type: string;
    action: string;
    deadline_hours: number;
    deadline_label: string;
    justification: string;
    impact_if_ignored: string;
    confidence: number | null;
    estimated_rul_hours: number | null;
}

export interface SituationReport {
    health_index: number;
    failure_probability_24h: number;
    quality_risk: number | null;
    is_anomaly: boolean;
    alert_level: number;
    reason: string;
    degradation_velocity: number;
    velocity_label: string;
    estimated_rul_hours: number | null;
    status: string;
}

export interface RecommendationResponse {
    recommendation: Recommendation | null;
    situation: SituationReport;
}

// Transversal — Explainability
export interface FeatureContribution {
    feature: string;
    label: string;
    importance: number;
    importance_pct: number;
}

export interface ExplainabilityResponse {
    feature_importance: FeatureContribution[];
    explanation: {
        key_features_anomalous: string[];
        explanation: string;
        top_features: FeatureContribution[];
    };
}

// ==============================================================================
// API SERVICE
// ==============================================================================

export const MLService = {
    async getLatestPrediction(machineId: string): Promise<MLPrediction | null> {
        try {
            const response = await fetch(`${API_URL}/api/ml/predictions/latest/${machineId}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });
            if (!response.ok) {
                if (response.status === 404) return null;
                throw new Error(`Failed to fetch ML Prediction: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching ML prediction for ${machineId}:`, error);
            return null;
        }
    },

    async getHistoricalRUL(machineId: string, limit: number = 24): Promise<HistoricalRUL[]> {
        try {
            const response = await fetch(`${API_URL}/api/ml/analytics/rul/${machineId}?limit=${limit}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });
            if (!response.ok) throw new Error(`Failed to fetch Historical RUL: ${response.statusText}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching historical RUL for ${machineId}:`, error);
            return [];
        }
    },

    // --- ADVANCED ENDPOINTS ---

    async getMachineTimeline(machineId: string, limit: number = 15): Promise<TimelineEvent[]> {
        try {
            const response = await fetch(`${API_URL}/api/ml/advanced/${machineId}/timeline?limit=${limit}`);
            if (!response.ok) throw new Error('Failed to fetch timeline');
            return await response.json();
        } catch (error) {
            console.error('Error fetching timeline', error);
            return [];
        }
    },

    async getNormalComparison(machineId: string): Promise<ComparisonMetric[]> {
        try {
            const response = await fetch(`${API_URL}/api/ml/advanced/${machineId}/comparison`);
            if (!response.ok) throw new Error('Failed to fetch comparison');
            return await response.json();
        } catch (error) {
            console.error('Error fetching normal comparison', error);
            return [];
        }
    },

    async getSensorTrends(machineId: string, limit: number = 36): Promise<SensorTrend[]> {
        try {
            const response = await fetch(`${API_URL}/api/ml/advanced/${machineId}/sensor-trends?limit=${limit}`);
            if (!response.ok) throw new Error('Failed to fetch sensor trends');
            return await response.json();
        } catch (error) {
            console.error('Error fetching sensor trends', error);
            return [];
        }
    },

    // --- LAYER 3: DIAGNOSIS ---

    async getDiagnosis(machineId: string): Promise<DiagnosisResponse | null> {
        try {
            const response = await fetch(`${API_URL}/api/ml/advanced/${machineId}/diagnosis`);
            if (!response.ok) throw new Error('Failed to fetch diagnosis');
            return await response.json();
        } catch (error) {
            console.error('Error fetching diagnosis', error);
            return null;
        }
    },

    // --- LAYER 4: FORECAST + RUL ---

    async getForecast(machineId: string): Promise<ForecastResponse | null> {
        try {
            const response = await fetch(`${API_URL}/api/ml/advanced/${machineId}/forecast`);
            if (!response.ok) throw new Error('Failed to fetch forecast');
            return await response.json();
        } catch (error) {
            console.error('Error fetching forecast', error);
            return null;
        }
    },

    // --- LAYER 5: RECOMMENDATIONS ---

    async getRecommendations(machineId: string): Promise<RecommendationResponse | null> {
        try {
            const response = await fetch(`${API_URL}/api/ml/advanced/${machineId}/recommendations`);
            if (!response.ok) throw new Error('Failed to fetch recommendations');
            return await response.json();
        } catch (error) {
            console.error('Error fetching recommendations', error);
            return null;
        }
    },

    // --- TRANSVERSAL: EXPLAINABILITY ---

    async getExplainability(machineId: string): Promise<ExplainabilityResponse | null> {
        try {
            const response = await fetch(`${API_URL}/api/ml/advanced/${machineId}/explainability`);
            if (!response.ok) throw new Error('Failed to fetch explainability');
            return await response.json();
        } catch (error) {
            console.error('Error fetching explainability', error);
            return null;
        }
    }
};
