'use client';

import React from 'react';
import { SensorTrend } from '@/services/mlService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity } from 'lucide-react';


interface SensorTrendsChartProps {
    data: SensorTrend[];
    machineId: string;
    isLoading: boolean;
}

export default function SensorTrendsChart({ data, machineId, isLoading }: SensorTrendsChartProps) {
    if (isLoading) {
        return <div className="p-6 rounded-xl shadow-sm flex items-center justify-center min-h-[350px]"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--secondary-500, #2563EB)' }}></div>
        </div>;
    }

    if (!data || data.length === 0) {
        return null;
    }

    const isOsmoseur = machineId.includes('OSM');

    const formattedData = data.map(item => ({
        ...item,
        time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }));

    return (
        <div className="p-6 rounded-xl shadow-sm"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <h3 className="text-lg font-semibold mb-6 flex items-center" style={{ color: 'var(--text-primary, #0F172A)' }}>
                <Activity className="w-5 h-5 mr-2" style={{ color: 'var(--accent-red, #D92B2B)' }} />
                Live Sensor Trends
            </h3>

            <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={formattedData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                        <XAxis
                            dataKey="time"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#64748B', fontSize: 12 }}
                            dy={10}
                        />
                        <YAxis
                            yAxisId="left"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#64748B', fontSize: 12 }}
                        />
                        <YAxis
                            yAxisId="right"
                            orientation="right"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#64748B', fontSize: 12 }}
                        />
                        <Tooltip
                            contentStyle={{
                                borderRadius: '10px',
                                border: '1px solid #E2E8F0',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                                background: '#FFFFFF'
                            }}
                        />
                        <Legend wrapperStyle={{ paddingTop: '20px' }} />

                        {isOsmoseur ? (
                            <>
                                <Line yAxisId="left" type="monotone" dataKey="debit" name="Débit (L/h)" stroke="#059669" strokeWidth={2} dot={false} activeDot={{ r: 6 }} />
                                <Line yAxisId="right" type="monotone" dataKey="conductivite" name="Conductivité (µS/cm)" stroke="#F59E0B" strokeWidth={2} dot={false} />
                                <Line yAxisId="left" type="monotone" dataKey="tds" name="TDS (ppm)" stroke="#2563EB" strokeWidth={2} dot={false} />
                            </>
                        ) : (
                            <>
                                <Line yAxisId="left" type="monotone" dataKey="vibrations" name="Vibrations (mm/s)" stroke="#D92B2B" strokeWidth={2} dot={false} activeDot={{ r: 6 }} />
                                <Line yAxisId="right" type="monotone" dataKey="volume" name="Volume (L)" stroke="#2563EB" strokeWidth={2} dot={false} />
                                <Line yAxisId="left" type="monotone" dataKey="carbonation" name="Carbonatation (g/L)" stroke="#8B5CF6" strokeWidth={2} dot={false} />
                            </>
                        )}
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
