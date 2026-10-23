"use client"

import { useEffect, useState, useCallback } from "react"
import {
    iotOsmoseurApi,
    IoTOsmoseurReading,
    IoTOsmoseurStatus,
} from "@/services/iotOsmoseurService"
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts"
import { Activity, Wifi, WifiOff, Droplets, Gauge, FlaskConical, Waves } from "lucide-react"

// ============================================================================
// TYPES
// ============================================================================

interface ChartDataPoint {
    time: string
    ph: number | null
    tds: number | null
    turb_in: number | null
    turb_out: number | null
}

// ============================================================================
// CONSTANTS
// ============================================================================

const POLL_INTERVAL_MS = 3000
const TIMESERIES_MINUTES = 5

const CHART_COLORS = {
    ph: "#6366f1",       // indigo
    tds: "#f59e0b",      // amber
    turb_in: "#10b981",  // emerald
    turb_out: "#ef4444", // red
}

// ============================================================================
// COMPONENT
// ============================================================================

export default function IoTMonitoringPage() {
    const [status, setStatus] = useState<IoTOsmoseurStatus | null>(null)
    const [latest, setLatest] = useState<IoTOsmoseurReading | null>(null)
    const [chartData, setChartData] = useState<ChartDataPoint[]>([])
    const [error, setError] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    // ---- Data Fetching ----
    const fetchAll = useCallback(async () => {
        try {
            const [statusRes, timeseriesRes] = await Promise.all([
                iotOsmoseurApi.getStatus(),
                iotOsmoseurApi.getTimeseries(TIMESERIES_MINUTES),
            ])

            setStatus(statusRes)

            // Try to get latest – may 404 if no data
            try {
                const latestRes = await iotOsmoseurApi.getLatest()
                setLatest(latestRes)
            } catch {
                setLatest(null)
            }

            // Transform timeseries for Recharts
            const points: ChartDataPoint[] = timeseriesRes.map((r) => ({
                time: new Date(r.created_at).toLocaleTimeString("fr-FR", {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                }),
                ph: r.ph,
                tds: r.tds,
                turb_in: r.turb_in,
                turb_out: r.turb_out,
            }))
            setChartData(points)
            setError(null)
        } catch {
            setError("Impossible de contacter le serveur")
        } finally {
            setIsLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchAll()
        const interval = setInterval(fetchAll, POLL_INTERVAL_MS)
        return () => clearInterval(interval)
    }, [fetchAll])

    // ---- Loading State ----
    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full min-h-[400px]">
                <div className="flex flex-col items-center gap-3">
                    <div className="w-8 h-8 border-3 border-slate-300 border-t-indigo-500 rounded-full animate-spin" />
                    <span className="text-sm text-slate-500">Chargement des données…</span>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* ── Page Header ── */}
            <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-indigo-50">
                    <Activity className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">
                        IoT Monitoring
                        <span className="ml-2 text-xs font-normal px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 align-middle">
                            Prototype
                        </span>
                    </h1>
                    <p className="text-sm text-slate-500">Données temps réel du prototype</p>
                </div>
            </div>

            {/* ── Error Banner ── */}
            {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {/* ── Row 1: Status + Latest Values ── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                {/* A. Status Card */}
                <StatusCard status={status} />

                {/* B. Latest Values Card */}
                <LatestValuesCard latest={latest} />
            </div>

            {/* ── Row 2: Real-Time Chart ── */}
            <RealtimeChart data={chartData} />
        </div>
    )
}

// ============================================================================
// STATUS CARD
// ============================================================================

function StatusCard({ status }: { status: IoTOsmoseurStatus | null }) {
    const isConnected = status?.status === "CONNECTED"

    const lastSeen = status?.last_seen
        ? new Date(status.last_seen).toLocaleString("fr-FR", {
              day: "2-digit",
              month: "2-digit",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
          })
        : "—"

    return (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                    État Connexion
                </h2>
                {isConnected ? (
                    <Wifi className="h-5 w-5 text-emerald-500" />
                ) : (
                    <WifiOff className="h-5 w-5 text-red-400" />
                )}
            </div>

            <div className="flex items-center gap-3">
                <span
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${
                        isConnected
                            ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200"
                            : "bg-red-50 text-red-700 ring-1 ring-red-200"
                    }`}
                >
                    <span
                        className={`w-2 h-2 rounded-full ${
                            isConnected ? "bg-emerald-500 animate-pulse" : "bg-red-400"
                        }`}
                    />
                    {isConnected ? "Connecté" : "Déconnecté"}
                </span>
            </div>

            <p className="mt-4 text-xs text-slate-400">
                Dernière donnée : <span className="text-slate-600 font-medium">{lastSeen}</span>
            </p>
        </div>
    )
}

// ============================================================================
// LATEST VALUES CARD
// ============================================================================

interface MetricCardProps {
    label: string
    value: number | null | undefined
    unit: string
    icon: React.ReactNode
    color: string
}

function MetricTile({ label, value, unit, icon, color }: MetricCardProps) {
    return (
        <div className="flex items-start gap-3 p-4 rounded-lg bg-slate-50/80 border border-slate-100">
            <div className={`p-2 rounded-lg ${color}`}>{icon}</div>
            <div className="min-w-0">
                <p className="text-xs text-slate-500 truncate">{label}</p>
                <p className="text-lg font-bold text-slate-800 mt-0.5">
                    {value != null ? value.toFixed(2) : "—"}
                    <span className="text-xs font-normal text-slate-400 ml-1">{unit}</span>
                </p>
            </div>
        </div>
    )
}

function LatestValuesCard({ latest }: { latest: IoTOsmoseurReading | null }) {
    if (!latest) {
        return (
            <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm flex items-center justify-center">
                <p className="text-slate-400 text-sm">Aucune donnée disponible</p>
            </div>
        )
    }

    const metrics: MetricCardProps[] = [
        {
            label: "Débit Entrée",
            value: latest.debit_in,
            unit: "L/h",
            icon: <Droplets className="h-4 w-4 text-blue-600" />,
            color: "bg-blue-50",
        },
        {
            label: "Turbidité Entrée",
            value: latest.turb_in,
            unit: "NTU",
            icon: <Waves className="h-4 w-4 text-emerald-600" />,
            color: "bg-emerald-50",
        },
        {
            label: "pH",
            value: latest.ph,
            unit: "",
            icon: <FlaskConical className="h-4 w-4 text-indigo-600" />,
            color: "bg-indigo-50",
        },
        {
            label: "TDS",
            value: latest.tds,
            unit: "PPM",
            icon: <Gauge className="h-4 w-4 text-amber-600" />,
            color: "bg-amber-50",
        },
        {
            label: "Débit Sortie",
            value: latest.debit_out,
            unit: "L/h",
            icon: <Droplets className="h-4 w-4 text-cyan-600" />,
            color: "bg-cyan-50",
        },
        {
            label: "Turbidité Sortie",
            value: latest.turb_out,
            unit: "NTU",
            icon: <Waves className="h-4 w-4 text-red-500" />,
            color: "bg-red-50",
        },
    ]

    return (
        <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-4">
                Dernières Valeurs
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {metrics.map((m) => (
                    <MetricTile key={m.label} {...m} />
                ))}
            </div>
        </div>
    )
}

// ============================================================================
// REAL-TIME CHART
// ============================================================================

function RealtimeChart({ data }: { data: ChartDataPoint[] }) {
    if (data.length === 0) {
        return (
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm flex items-center justify-center h-80">
                <p className="text-slate-400 text-sm">
                    En attente de données pour le graphique…
                </p>
            </div>
        )
    }

    return (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-4">
                Graphique Temps Réel
                <span className="ml-2 text-xs font-normal text-slate-400">
                    (dernières {TIMESERIES_MINUTES} min)
                </span>
            </h2>

            <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                        data={data}
                        margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis
                            dataKey="time"
                            tick={{ fontSize: 11, fill: "#94a3b8" }}
                            interval="preserveStartEnd"
                        />
                        <YAxis 
                            yAxisId="left"
                            tick={{ fontSize: 11, fill: "#94a3b8" }} 
                            label={{ value: 'TDS (ppm)', angle: -90, position: 'insideLeft', fontSize: 11, fill: "#94a3b8" }}
                        />
                        <YAxis 
                            yAxisId="right" 
                            orientation="right" 
                            tick={{ fontSize: 11, fill: "#94a3b8" }} 
                            label={{ value: 'pH / Turbidité', angle: 90, position: 'insideRight', fontSize: 11, fill: "#94a3b8" }}
                            domain={[0, 'dataMax + 2']}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#ffffff",
                                border: "1px solid #e2e8f0",
                                borderRadius: "8px",
                                fontSize: "12px",
                            }}
                        />
                        <Legend
                            wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }}
                        />
                        <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="ph"
                            name="pH"
                            stroke={CHART_COLORS.ph}
                            strokeWidth={2}
                            dot={false}
                            animationDuration={300}
                        />
                        <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="tds"
                            name="TDS (ppm)"
                            stroke={CHART_COLORS.tds}
                            strokeWidth={2}
                            dot={false}
                            animationDuration={300}
                        />
                        <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="turb_in"
                            name="Turb. Entrée (V)"
                            stroke={CHART_COLORS.turb_in}
                            strokeWidth={2}
                            dot={false}
                            animationDuration={300}
                        />
                        <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="turb_out"
                            name="Turb. Sortie (V)"
                            stroke={CHART_COLORS.turb_out}
                            strokeWidth={2}
                            dot={false}
                            animationDuration={300}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}
