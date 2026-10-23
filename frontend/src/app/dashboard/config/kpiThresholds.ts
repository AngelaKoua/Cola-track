/**
 * KPI Thresholds Configuration
 * 
 * Centralized business rules for KPI status determination.
 * Must be kept in sync with backend/analytics/business_rules.py
 */

export interface KPIThreshold {
    target: number
    warning: number
    critical: number
    unit: string
    higherIsBetter: boolean
}

export const KPI_THRESHOLDS: Record<string, KPIThreshold> = {
    rendement: {
        target: 85,
        warning: 80,
        critical: 75,
        unit: "%",
        higherIsBetter: true
    },
    taux_recuperation: {
        target: 75,
        warning: 70,
        critical: 65,
        unit: "%",
        higherIsBetter: true
    },
    temps_arret: {
        target: 1.2,
        warning: 1.5,
        critical: 2,
        unit: "h",
        higherIsBetter: false
    },
    production: {
        target: 30000,
        warning: 25000,
        critical: 20000,
        unit: "unités",
        higherIsBetter: true
    },
    conductivite: {
        target: 25,
        warning: 30,
        critical: 35,
        unit: "µS/cm",
        higherIsBetter: false
    }
}

export type KPIStatus = "success" | "warning" | "danger" | "neutral"
export type TrendDirection = "up" | "down" | "neutral"

export const STATUS_COLORS: Record<KPIStatus, string> = {
    success: "emerald",
    warning: "amber",
    danger: "rose",
    neutral: "gray"
}
