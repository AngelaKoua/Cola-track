"use client"

import { useState } from "react"
import { Filter, RefreshCcw } from "lucide-react"

import { KPICard } from "@/components/dashboard/KPICard"
import { TimeSeriesChart, CorrelationChart } from "./components/DashboardCharts"
import { TechnicianTable } from "./components/TechnicianTable"
import { AlertBanner } from "./components/AlertBanner"
import { EquipmentSelector, type EquipmentType } from "./components/EquipmentSelector"
import { useDashboardData } from "./hooks/useDashboardData"
import { Card } from "@/components/ui/Card"

export default function DashboardPage() {
    // --- STATE ---
    const [dateRange, setDateRange] = useState({
        start: "2025-12-01",
        end: new Date().toISOString().split('T')[0]
    })
    const [equipment, setEquipment] = useState<EquipmentType>("all")

    // --- FETCH DATA (UNIFIED) ---
    const { data, loading, error, refetch } = useDashboardData({
        startDate: dateRange.start,
        endDate: dateRange.end,
        equipment
    })

    // --- RENDER ---
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-50 control-room-grid relative">
            {/* Main container */}
            <div className="relative max-w-[1600px] mx-auto p-4 sm:p-6 lg:p-8 space-y-10 z-[1]">

                {/* HEADER */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 lg:gap-6 animate-fade-in-up">
                    <div className="space-y-1">
                        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-slate-900">
                            Pilotage
                        </h1>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                        {/* Equipment Selector */}
                        <EquipmentSelector selected={equipment} onChange={setEquipment} />

                        {/* Date Range */}
                        <div className="flex items-center gap-2 bg-white/80 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md hover:border-slate-300/80 transition-all duration-300">
                            <Filter className="h-4 w-4 text-slate-400 flex-shrink-0" />
                            <input
                                type="date"
                                value={dateRange.start}
                                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                                className="text-xs sm:text-sm border-none focus:ring-0 p-0 text-slate-700 w-[110px] sm:w-auto bg-transparent"
                            />
                            <span className="text-slate-300">→</span>
                            <input
                                type="date"
                                value={dateRange.end}
                                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                                className="text-xs sm:text-sm border-none focus:ring-0 p-0 text-slate-700 w-[110px] sm:w-auto bg-transparent"
                            />
                        </div>

                    </div>
                </div>

                {/* ERROR STATE */}
                {error && (
                    <div className="enterprise-section !bg-rose-50/80 !border-rose-200/70 text-rose-900 animate-fade-in-up">
                        <p className="font-semibold text-sm sm:text-base">Erreur de chargement</p>
                        <p className="text-xs sm:text-sm mt-1 text-rose-700">{error.message}</p>
                    </div>
                )}

                {/* LOADING STATE — Enterprise shimmer */}
                {loading && !data && (
                    <div className="enterprise-section flex flex-col items-center justify-center py-16 sm:py-20 animate-fade-in-up">
                        <div className="w-full max-w-md space-y-4">
                            {/* Shimmer bars */}
                            <div className="shimmer-bar h-1.5 w-full" />
                            <div className="shimmer-bar h-1.5 w-3/4 mx-auto" />
                            <div className="shimmer-bar h-1.5 w-1/2 mx-auto" />
                        </div>
                        <p className="mt-6 text-xs text-slate-400 font-semibold uppercase tracking-widest">
                            Chargement des données...
                        </p>
                    </div>
                )}

                {/* DASHBOARD CONTENT */}
                {data && (
                    <>
                        {/* ═══════════════════════════════════════════
                            SECTION: KPI CARDS
                        ═══════════════════════════════════════════ */}
                        <section className="enterprise-section animate-fade-in-up">
                            <div className="section-title section-title--kpi mb-6">
                                Indicateurs Clés
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 sm:gap-5 lg:gap-6">
                                {data.kpis.rendement_global && (
                                    <KPICard
                                        title="Rendement Global"
                                        value={data.kpis.rendement_global.value}
                                        unit={data.kpis.rendement_global.unit}
                                        target={data.kpis.rendement_global.target}
                                        status={data.kpis.rendement_global.status}
                                        index={0}
                                    />
                                )}
                                {data.kpis.taux_recuperation_osmoseur && (
                                    <KPICard
                                        title="Taux Récupération"
                                        value={data.kpis.taux_recuperation_osmoseur.value}
                                        unit={data.kpis.taux_recuperation_osmoseur.unit}
                                        target={data.kpis.taux_recuperation_osmoseur.target}
                                        status={data.kpis.taux_recuperation_osmoseur.status}
                                        index={1}
                                    />
                                )}
                                {data.kpis.production_totale && (
                                    <KPICard
                                        title="Production Totale"
                                        value={data.kpis.production_totale.value.toLocaleString()}
                                        target={data.kpis.production_totale.target}
                                        status={data.kpis.production_totale.status}
                                        index={2}
                                    />
                                )}
                                {data.kpis.temps_arret && (
                                    <KPICard
                                        title="Temps d'Arrêt"
                                        value={data.kpis.temps_arret.value}
                                        unit={data.kpis.temps_arret.unit}
                                        target={data.kpis.temps_arret.target}
                                        status={data.kpis.temps_arret.status}
                                        index={3}
                                    />
                                )}
                                {data.kpis.qualite_eau && (
                                    <KPICard
                                        title="Qualité de l'eau"
                                        value={data.kpis.qualite_eau.value}
                                        unit={data.kpis.qualite_eau.unit}
                                        target={data.kpis.qualite_eau.target}
                                        status={data.kpis.qualite_eau.status}
                                        index={4}
                                    />
                                )}
                            </div>
                        </section>

                        {/* ═══════════════════════════════════════════
                            SECTION: CHARTS — Analyses & Tendances
                        ═══════════════════════════════════════════ */}
                        <section className="enterprise-section animate-fade-in-up stagger-2">
                            <div className="section-title section-title--analysis mb-6">
                                Analyses et Tendances
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
                                {/* Main Efficiency Chart */}
                                {data.timeseries.rendement && (
                                    <div className="lg:col-span-2">
                                        <Card className="border border-slate-200/70 shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
                                            <TimeSeriesChart
                                                title="Évolution du Rendement"
                                                description="Analyse quotidienne de l'efficacité de production"
                                                data={data.timeseries.rendement}
                                                metricKey="rendement"
                                                color="#059669"
                                                unit="%"
                                            />
                                        </Card>
                                    </div>
                                )}

                                {/* Correlation */}
                                <div className="lg:col-span-1">
                                    <Card className="border border-slate-200/70 shadow-md hover:shadow-lg transition-shadow duration-300 h-full overflow-hidden">
                                        <CorrelationChart data={data.correlations} />
                                    </Card>
                                </div>
                            </div>
                        </section>

                        {/* ═══════════════════════════════════════════
                            SECTION: Détails Opérationnels
                        ═══════════════════════════════════════════ */}
                        <section className="enterprise-section animate-fade-in-up stagger-3">
                            <div className="section-title section-title--operations mb-6">
                                Détails Opérationnels
                            </div>

                            {/* Performance Osmoseur */}
                            {data.timeseries.taux_recuperation && (
                                <Card className="border border-slate-200/70 shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
                                    <TimeSeriesChart
                                        title="Performance Osmoseur"
                                        description="Suivi du taux de récupération"
                                        data={data.timeseries.taux_recuperation}
                                        metricKey="taux_recuperation"
                                        color="#3b82f6"
                                        unit="%"
                                    />
                                </Card>
                            )}
                        </section>
                    </>
                )}
            </div>
        </div>
    )
}
