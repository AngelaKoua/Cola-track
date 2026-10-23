'use client';

import React from 'react';
import { ForecastData } from '@/services/mlService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingDown } from 'lucide-react';

interface ForecastPanelProps {
    data: ForecastData[];
    isLoading: boolean;
}

export default function ForecastPanel({ data, isLoading }: ForecastPanelProps) {
    if (isLoading) {
        return <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100 flex items-center justify-center min-h-[300px]">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>;
    }

    if (!data || data.length === 0) {
        return null;
    }

    const formattedData = data.map(item => ({
        ...item,
        time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }));

    return (
        <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <TrendingDown className="w-5 h-5 mr-2 text-primary-600" />
                Health Index Forecast (Next 30 mins)
            </h3>
            <p className="text-sm text-gray-500 mb-6">
                Linear projection of the machine's health index based on the current degradation velocity.
            </p>

            <div className="h-[200px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={formattedData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis
                            dataKey="time"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                            dy={10}
                        />
                        <YAxis
                            domain={[0, 100]}
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                        />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />

                        {/* Threshold Lines */}
                        <ReferenceLine y={75} stroke="#f59e0b" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Warning Zone', fill: '#f59e0b', fontSize: 11 }} />
                        <ReferenceLine y={50} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Critical Zone', fill: '#ef4444', fontSize: 11 }} />

                        <Line
                            type="monotone"
                            dataKey="forecasted_health"
                            name="Forecasted Health"
                            stroke="#8b5cf6"
                            strokeWidth={3}
                            strokeDasharray="5 5"
                            dot={{ fill: '#8b5cf6', strokeWidth: 2 }}
                            activeDot={{ r: 6 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
