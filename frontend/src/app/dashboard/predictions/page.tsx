"use client";

import { useState, useEffect } from "react";
import {
    MLService, MLPrediction, HistoricalRUL,
    TimelineEvent, ComparisonMetric, SensorTrend,
    DiagnosisResponse, ForecastResponse,
    RecommendationResponse, ExplainabilityResponse
} from "@/services/mlService";
import { Droplets, Thermometer, Settings2, Cpu } from "lucide-react";

// Section 1 — Situation Awareness
import { HealthCard } from "@/components/predictions/HealthCard";
import { FailureProbabilityCard } from "@/components/predictions/FailureProbabilityCard";
import { QualityRiskCard } from "@/components/predictions/QualityRiskCard";
import { AlertCard } from "@/components/predictions/AlertCard";
import DegradationVelocityBadge from "@/components/predictions/advanced/DegradationVelocityBadge";

// Section 2 — Events & Anomalies
import AnomaliesTable from "@/components/predictions/advanced/AnomaliesTable";
import OutOfBoundsPanel from "@/components/predictions/advanced/OutOfBoundsPanel";
import TimelinePanel from "@/components/predictions/advanced/TimelinePanel";

// Section 3 — Root Cause Analysis
import DiagnosticCards from "@/components/predictions/advanced/DiagnosticCards";
import FeatureImportanceChart from "@/components/predictions/advanced/FeatureImportanceChart";
import NormalComparisonTable from "@/components/predictions/advanced/NormalComparisonTable";

// Section 4 — Machine Behaviour
import SensorTrendsChart from "@/components/predictions/advanced/SensorTrendsChart";
import { RULChart } from "@/components/predictions/RULChart";

// Section 5 — Prognostics
import RULEstimationPanel from "@/components/predictions/advanced/RULEstimationPanel";

// Section 6 — Decision Support
import RecommendationCards from "@/components/predictions/advanced/RecommendationCards";

export default function PredictionsPage() {
    const [selectedMachine, setSelectedMachine] = useState<"OSM-001" | "RMP-001">("OSM-001");
    const [prediction, setPrediction] = useState<MLPrediction | null>(null);
    const [history, setHistory] = useState<HistoricalRUL[]>([]);

    // Advanced Data States
    const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
    const [comparisonMetrics, setComparisonMetrics] = useState<ComparisonMetric[]>([]);
    const [sensorTrends, setSensorTrends] = useState<SensorTrend[]>([]);
    const [diagnosisData, setDiagnosisData] = useState<DiagnosisResponse | null>(null);
    const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
    const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
    const [explainability, setExplainability] = useState<ExplainabilityResponse | null>(null);

    const [isLoading, setIsLoading] = useState(true);

    const fetchMachineData = async (machineId: string) => {
        try {
            const [
                latest, hist,
                timeline, comparison, trends,
                diagnosis, forecast, recs, explain
            ] = await Promise.all([
                MLService.getLatestPrediction(machineId),
                MLService.getHistoricalRUL(machineId, 24),
                MLService.getMachineTimeline(machineId, 15),
                MLService.getNormalComparison(machineId),
                MLService.getSensorTrends(machineId, 36),
                MLService.getDiagnosis(machineId),
                MLService.getForecast(machineId),
                MLService.getRecommendations(machineId),
                MLService.getExplainability(machineId)
            ]);

            setPrediction(latest);
            setHistory(hist);
            setTimelineEvents(timeline);
            setComparisonMetrics(comparison);
            setSensorTrends(trends);
            setDiagnosisData(diagnosis);
            setForecastData(forecast);
            setRecommendations(recs);
            setExplainability(explain);
        } catch (error) {
            console.error(`Failed to load AI diagnostics for ${machineId}`, error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        setIsLoading(true);
        fetchMachineData(selectedMachine);

        const interval = setInterval(() => {
            fetchMachineData(selectedMachine);
        }, 30000);

        return () => clearInterval(interval);
    }, [selectedMachine]);

    const isOsmoseur = selectedMachine === "OSM-001";

    // Loading state
    if (isLoading && !prediction) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center gap-4" style={{ background: 'var(--bg-base, #F8FAFC)' }}>
                <div className="relative">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: 'var(--accent-red, #D92B2B)' }}></div>
                    <Cpu className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-5 w-5" style={{ color: 'var(--accent-red, #D92B2B)' }} />
                </div>
                <p className="font-medium" style={{ color: 'var(--text-tertiary, #64748B)' }}>Analyse IA en cours...</p>
            </div>
        );
    }

    // No data
    if (!prediction) {
        return (
            <div className="min-h-screen p-6 flex items-center justify-center" style={{ background: 'var(--bg-base, #F8FAFC)' }}>
                <div className="p-8 rounded-xl shadow-sm text-center" style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
                    <Settings2 className="h-16 w-16 mx-auto mb-4" style={{ color: 'var(--text-muted, #94A3B8)' }} />
                    <h2 className="text-xl font-bold" style={{ color: 'var(--text-secondary, #334155)' }}>Aucune donnée prédictive</h2>
                    <p className="mt-2" style={{ color: 'var(--text-tertiary, #64748B)' }}>Le moteur IA n'a pas encore analysé cette machine.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen" style={{ background: 'var(--bg-base, #F8FAFC)' }}>
            <div className="max-w-[1400px] mx-auto p-4 sm:p-6 lg:p-8 space-y-10">

                {/* ================================================================ */}
                {/* HEADER                                                          */}
                {/* ================================================================ */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6" style={{ borderBottom: '1px solid var(--border-default, #E2E8F0)' }}>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3" style={{ color: 'var(--text-primary, #0F172A)' }}>
                            Prédictions et aide à la décision
                        </h1>
                    </div>

                    <div className="mt-4 sm:mt-0 flex flex-col items-end gap-2">
                        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted, #94A3B8)' }}>SÉLECTION ÉQUIPEMENT</span>
                        <div className="w-64 relative">
                            <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                                {isOsmoseur
                                    ? <Droplets className="h-4 w-4" style={{ color: 'var(--secondary-500, #2563EB)' }} />
                                    : <Thermometer className="h-4 w-4" style={{ color: 'var(--status-warning-500, #F59E0B)' }} />
                                }
                            </div>
                            <select
                                value={selectedMachine}
                                onChange={(e) => setSelectedMachine(e.target.value as any)}
                                className="w-full rounded-lg py-2 pl-10 pr-4 shadow-sm appearance-none font-medium text-sm transition-all duration-200"
                                style={{
                                    background: 'var(--bg-surface, #FFFFFF)',
                                    border: '1px solid var(--border-default, #E2E8F0)',
                                    color: 'var(--text-secondary, #334155)',
                                    outline: 'none',
                                }}
                            >
                                <option value="OSM-001">Osmoseur</option>
                                <option value="RMP-001">Remplisseuse</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* ================================================================ */}
                {/* SECTION 1 — SITUATION AWARENESS                                 */}
                {/* ================================================================ */}
                <section>
                    <h2 className="section-title section-title--kpi mb-5">
                        État Global de la Machine
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-4">
                        <HealthCard healthIndex={prediction.health_index} />
                        <FailureProbabilityCard probability={prediction.failure_probability_24h} />
                        <QualityRiskCard risk={prediction.quality_risk} />
                        <AlertCard level={prediction.alert_level} />
                    </div>
                    <DegradationVelocityBadge situation={recommendations?.situation || null} />
                </section>

                {/* ================================================================ */}
                {/* SECTION 2 — ANOMALIES & EVENTS                                 */}
                {/* ================================================================ */}
                <section>
                    <h2 className="section-title section-title--operations mb-5">
                        Événements & Paramètres Anormaux
                    </h2>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
                        <div className="lg:col-span-2 space-y-5">
                            <OutOfBoundsPanel metrics={comparisonMetrics} isLoading={isLoading} />
                            <AnomaliesTable history={history} isLoading={isLoading} />
                        </div>
                        <div className="lg:col-span-1">
                            <TimelinePanel events={timelineEvents} isLoading={isLoading} />
                        </div>
                    </div>
                </section>

                {/* ================================================================ */}
                {/* SECTION 3 — ROOT CAUSE ANALYSIS                                 */}
                {/* ================================================================ */}
                <section>
                    <h2 className="section-title section-title--analysis mb-5">
                        Analyse causes racines
                    </h2>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                        <DiagnosticCards
                            diagnoses={diagnosisData?.diagnoses || []}
                            isLoading={isLoading}
                        />
                        <div className="space-y-6">
                            <FeatureImportanceChart
                                features={explainability?.feature_importance || []}
                                explanationText={explainability?.explanation?.explanation || ''}
                                isLoading={isLoading}
                            />
                            <NormalComparisonTable metrics={comparisonMetrics} isLoading={isLoading} />
                        </div>
                    </div>
                </section>

                {/* ================================================================ */}
                {/* SECTION 4 — MACHINE BEHAVIOUR                                   */}
                {/* ================================================================ */}
                <section>
                    <h2 className="section-title section-title--analysis mb-5">
                        Tendances Capteurs & Dégradation
                    </h2>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                        <SensorTrendsChart data={sensorTrends} machineId={selectedMachine} isLoading={isLoading} />
                        <RULChart history={history} />
                    </div>
                </section>

                {/* ================================================================ */}
                {/* SECTION 5 — PROGNOSTICS                                         */}
                {/* ================================================================ */}
                <section>
                    <h2 className="section-title section-title--operations mb-5">
                        Prévisions & Remaining Useful Life
                    </h2>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                        <RULEstimationPanel rul={forecastData?.rul || null} isLoading={isLoading} />
                        {/* Parameter Forecast Summary */}
                        {forecastData?.parameter_forecasts && forecastData.parameter_forecasts.length > 0 && (
                            <div className="p-6 rounded-xl shadow-sm" style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
                                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary, #0F172A)' }}>Prévision des Paramètres Critiques</h3>
                                <div className="overflow-x-auto">
                                    <table className="min-w-full" style={{ borderCollapse: 'separate', borderSpacing: 0 }}>
                                        <thead>
                                            <tr style={{ borderBottom: '1px solid var(--border-default, #E2E8F0)' }}>
                                                <th className="px-3 py-2.5 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>Paramètre</th>
                                                <th className="px-3 py-2.5 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>Actuel</th>
                                                <th className="px-3 py-2.5 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>Tendance</th>
                                                {Object.keys(forecastData.parameter_forecasts[0]?.forecasts || {}).map(h => (
                                                    <th key={h} className="px-3 py-2.5 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>{h}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {forecastData.parameter_forecasts.map((pf, idx) => (
                                                <tr key={idx} className="transition-colors" style={{ borderBottom: '1px solid var(--border-light, #F1F5F9)' }}
                                                    onMouseEnter={e => (e.currentTarget.style.background = 'var(--hover-row, #F8FAFC)')}
                                                    onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                                                >
                                                    <td className="px-3 py-2.5 text-sm font-medium" style={{ color: 'var(--text-primary, #0F172A)' }}>{pf.parameter}</td>
                                                    <td className="px-3 py-2.5 text-sm text-right" style={{ color: 'var(--text-secondary, #334155)' }}>{pf.current_value}</td>
                                                    <td className="px-3 py-2.5 text-sm text-right">
                                                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${pf.trend_direction === 'rising' ? 'bg-rose-100 text-rose-700' :
                                                            pf.trend_direction === 'falling' ? 'bg-blue-100 text-blue-700' :
                                                                'bg-slate-100 text-slate-600'
                                                            }`}>
                                                            {pf.trend_direction === 'rising' ? '↑' : pf.trend_direction === 'falling' ? '↓' : '→'} {pf.trend_direction}
                                                        </span>
                                                    </td>
                                                    {Object.values(pf.forecasts).map((val, vidx) => (
                                                        <td key={vidx} className="px-3 py-2.5 text-sm text-right font-mono" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                                            {val}
                                                        </td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>
                </section>

                {/* ================================================================ */}
                {/* SECTION 6 — DECISION SUPPORT                                    */}
                {/* ================================================================ */}
                <section className="pb-12">
                    <h2 className="section-title section-title--kpi mb-5">
                        Recommandations de Maintenance
                    </h2>
                    <RecommendationCards
                        recommendation={recommendations?.recommendation || null}
                        isLoading={isLoading}
                    />
                    </section>

                    {/* ColaAssist Context Data */}
                    <div id="cola-context-machine" data-machine={selectedMachine} style={{display: 'none'}} />
                    <div id="cola-context-indicators" data-indicators={`Santé: ${prediction?.health_index || 'N/A'}% | Alerte: ${prediction?.alert_level || 'N/A'}`} style={{display: 'none'}} />

                </div>
            </div>
        );
    }
