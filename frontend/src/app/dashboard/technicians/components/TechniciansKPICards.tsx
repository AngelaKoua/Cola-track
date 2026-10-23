/**
 * Technicians KPI Cards Component
 * 
 * Displays summary statistics in card format:
 * - Total technicians
 * - Active technicians
 * - Inactive technicians
 * - Total entries in period
 */

import { Users, UserCheck, UserX, Database } from "lucide-react"
import { KPICard } from "@/components/dashboard/KPICard"
import type { TechnicianSummaryStats } from "../services/techniciansService"

interface TechniciansKPICardsProps {
    stats: TechnicianSummaryStats | null
    loading: boolean
}

export function TechniciansKPICards({ stats, loading }: TechniciansKPICardsProps) {
    if (loading || !stats) {
        return (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
                {[...Array(4)].map((_, i) => (
                    <div key={i} className={`h-32 bg-slate-200/70 animate-pulse rounded-2xl animate-fade-in-up stagger-${i + 1}`}></div>
                ))}
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            <KPICard
                title="Total Techniciens"
                value={stats.total}
                unit=""
                description="Comptes utilisateurs enregistrés"
                icon={<Users className="h-4 w-4" />}
                status="neutral"
                trend="neutral"
                index={0}
            />

            <KPICard
                title="Techniciens Actifs"
                value={stats.active}
                unit=""
                description="Comptes actifs sur la plateforme"
                icon={<UserCheck className="h-4 w-4" />}
                status="success"
                trend="neutral"
                index={1}
            />

            <KPICard
                title="Techniciens Inactifs"
                value={stats.inactive}
                unit=""
                description="Comptes désactivés administrativement"
                icon={<UserX className="h-4 w-4" />}
                status={stats.inactive > 0 ? "warning" : "neutral"}
                trend="neutral"
                index={2}
            />

            <KPICard
                title={`Saisies (${stats.period_days}j)`}
                value={stats.total_entries.toLocaleString()}
                unit=""
                description="Saisies enregistrées sur la période"
                icon={<Database className="h-4 w-4" />}
                status="neutral"
                trend="neutral"
                index={3}
            />
        </div>
    )
}
