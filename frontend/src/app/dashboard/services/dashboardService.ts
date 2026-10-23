/**
 * Dashboard Service
 * 
 * Handles all API calls for the dashboard.
 * Provides typed interfaces for API responses.
 */

import type { KPIStatus, TrendDirection } from '../config/kpiThresholds'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface KPIData {
    value: number
    previous: number
    target: number
    status: KPIStatus
    trend: TrendDirection
    change: number
    unit: string
}

export interface TimeSeriesPoint {
    date: string
    value: number
}

export interface Alert {
    id: string
    severity: "critical" | "warning" | "info"
    equipment: string
    message: string
    timestamp: string
}

export interface Technician {
    original_name: string
    intervention_count: number
    avg_efficiency: number
}

export interface Correlations {
    temperature_vs_efficiency: number
    vibration_vs_efficiency: number
    interpretation: string
}

export interface DashboardOverviewResponse {
    kpis: {
        rendement_global: KPIData
        taux_recuperation_osmoseur: KPIData
        production_totale: KPIData
        temps_arret: KPIData
        qualite_eau: KPIData
    }
    timeseries: {
        rendement: TimeSeriesPoint[]
        taux_recuperation: TimeSeriesPoint[]
    }
    alerts: Alert[]
    technicians: Technician[]
    correlations: Correlations
    period: {
        start: string
        end: string
        equipment: string
    }
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

export class DashboardService {
    /**
     * Fetch all dashboard data in one call
     */
    static async getDashboardOverview(
        startDate: string,
        endDate: string,
        equipment: string = "all"
    ): Promise<DashboardOverviewResponse> {
        const params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate,
            equipment
        })

        const response = await fetch(
            `${API_BASE}/analytics/dashboard/overview?${params}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`)
        }

        return response.json()
    }

    /**
     * Legacy: Get global KPIs (kept for backward compatibility)
     */
    static async getGlobalKPIs(startDate: string, endDate: string) {
        const params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate
        })

        const response = await fetch(
            `${API_BASE}/analytics/kpi/global?${params}`
        )

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`)
        }

        return response.json()
    }
}
