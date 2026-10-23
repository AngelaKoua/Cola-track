"use client"

import { useState, useMemo } from "react"
import { CardContent, CardDescription } from "@/components/ui/Card"
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
    BarChart,
    Bar,
} from "@/lib/dynamicCharts"

type ChartPeriod = "7" | "30" | "90" | "all"

interface TimeSeriesChartProps {
    data: any[]
    title: string
    description?: string
    metricKey: string
    color?: string
    unit?: string
}

export function TimeSeriesChart({
    data,
    title,
    description,
    metricKey,
    color = "#059669",
    unit = ""
}: TimeSeriesChartProps) {
    const [chartPeriod, setChartPeriod] = useState<ChartPeriod>("all")

    // Filter data based on the selected period
    const filteredData = useMemo(() => {
        if (chartPeriod === "all" || !data || data.length === 0) return data

        const now = new Date()
        const daysBack = parseInt(chartPeriod)
        const cutoffDate = new Date(now)
        cutoffDate.setDate(cutoffDate.getDate() - daysBack)

        return data.filter((point) => {
            const pointDate = new Date(point.date)
            return pointDate >= cutoffDate
        })
    }, [data, chartPeriod])

    return (
        <div className="chart-watermark relative">
            {/* Enterprise Chart Header */}
            <div className="flex items-center justify-between px-8 pt-6 pb-4">
                <div>
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">{title}</h3>
                    {description && (
                        <p className="text-xs text-slate-400 mt-0.5 font-medium">{description}</p>
                    )}
                </div>
                <select
                    value={chartPeriod}
                    onChange={(e) => setChartPeriod(e.target.value as ChartPeriod)}
                    className="text-xs font-medium text-slate-500 bg-slate-50 border border-slate-200/70 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-slate-300 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                    <option value="7">7 derniers jours</option>
                    <option value="30">30 derniers jours</option>
                    <option value="90">90 derniers jours</option>
                    <option value="all">Personnalisé</option>
                </select>
            </div>

            {/* Separator */}
            <div className="mx-8 border-t border-slate-100" />

            {/* Chart Area */}
            <div className="h-[320px] w-full px-8 pt-4 pb-6 relative z-[1]">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={filteredData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id={`color-${metricKey}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={color} stopOpacity={0.25} />
                                <stop offset="95%" stopColor={color} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" strokeOpacity={0.6} />
                        <XAxis
                            dataKey="date"
                            stroke="#94a3b8"
                            fontSize={11}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => {
                                if (value.length > 10) return new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                return new Date(value).toLocaleDateString([], { day: '2-digit', month: '2-digit' })
                            }}
                        />
                        <YAxis
                            stroke="#94a3b8"
                            fontSize={11}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `${value}${unit}`}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(255,255,255,0.95)',
                                backdropFilter: 'blur(8px)',
                                borderRadius: '10px',
                                border: '1px solid rgba(226,232,240,0.7)',
                                boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
                                padding: '10px 14px',
                                fontSize: '12px'
                            }}
                            labelStyle={{ color: '#334155', marginBottom: '4px', fontWeight: 600 }}
                            formatter={(value: any) => [`${Number(value).toFixed(2)}${unit}`, title]}
                        />
                        <Area
                            type="monotone"
                            dataKey="value"
                            stroke={color}
                            strokeWidth={2}
                            fillOpacity={1}
                            fill={`url(#color-${metricKey})`}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

interface CorrelationChartProps {
    data: { temperature_vs_efficiency: number; vibration_vs_efficiency: number; interpretation: string } | null
}

export function CorrelationChart({ data }: CorrelationChartProps) {
    if (!data) return null;

    const chartData = [
        { name: "Température", correlation: data.temperature_vs_efficiency, fill: Math.abs(data.temperature_vs_efficiency) > 0.5 ? "#e11d48" : "#f59e0b" },
        { name: "Vibrations", correlation: data.vibration_vs_efficiency, fill: Math.abs(data.vibration_vs_efficiency) > 0.5 ? "#e11d48" : "#059669" },
    ]

    return (
        <div className="chart-watermark relative h-full flex flex-col">
            {/* Enterprise Chart Header */}
            <div className="flex items-center justify-between px-8 pt-6 pb-4">
                <div>
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">Analyse de Corrélation</h3>
                    <p className="text-xs text-slate-400 mt-0.5 font-medium">Facteurs impactant le rendement (1.0 = Fort impact)</p>
                </div>
            </div>

            {/* Separator */}
            <div className="mx-8 border-t border-slate-100" />

            {/* Chart Area */}
            <div className="h-[250px] w-full px-8 pt-4 pb-2 relative z-[1] flex-1">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 10, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" strokeOpacity={0.6} />
                        <XAxis type="number" domain={[-1, 1]} fontSize={11} stroke="#94a3b8" />
                        <YAxis dataKey="name" type="category" width={100} fontSize={11} stroke="#94a3b8" />
                        <Tooltip
                            cursor={{ fill: 'transparent' }}
                            contentStyle={{
                                backgroundColor: 'rgba(255,255,255,0.95)',
                                backdropFilter: 'blur(8px)',
                                borderRadius: '10px',
                                border: '1px solid rgba(226,232,240,0.7)',
                                boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
                                padding: '10px 14px',
                                fontSize: '12px'
                            }}
                        />
                        <Bar dataKey="correlation" radius={[0, 4, 4, 0]} barSize={28} />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            <div className="px-8 pb-6 pt-2 text-[11px] text-slate-400 italic text-center border-t border-slate-100 mx-8 relative z-[1]">
                {data.interpretation}
            </div>
        </div>
    )
}
