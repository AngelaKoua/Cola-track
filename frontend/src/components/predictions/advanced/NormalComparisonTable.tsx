'use client';

import React from 'react';
import { ComparisonMetric } from '@/services/mlService';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface NormalComparisonTableProps {
    metrics: ComparisonMetric[];
    isLoading: boolean;
}

export default function NormalComparisonTable({ metrics, isLoading }: NormalComparisonTableProps) {
    if (isLoading) {
        return <div className="p-6 rounded-xl shadow-sm min-h-[300px] flex items-center justify-center"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--secondary-500, #2563EB)' }}></div>
        </div>;
    }

    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <div className="p-6 rounded-xl shadow-sm"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary, #0F172A)' }}>Baseline Comparison</h3>
                <span className="text-xs font-semibold px-2 py-1 rounded"
                    style={{ background: 'var(--secondary-50, #EFF6FF)', color: 'var(--secondary-500, #2563EB)', border: '1px solid var(--secondary-100, #DBEAFE)' }}>
                    Live Delta
                </span>
            </div>

            <p className="text-sm mb-6" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                Comparing current real-time telemetry against theoretical normal operating parameters mapping to 100% Health.
            </p>

            <div className="overflow-x-auto">
                <table className="min-w-full">
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-default, #E2E8F0)' }}>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                Parameter
                            </th>
                            <th scope="col" className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                Normal
                            </th>
                            <th scope="col" className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                Current
                            </th>
                            <th scope="col" className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                Delta
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {metrics.map((m, idx) => {
                            const isHigh = m.delta_pct > 10;
                            const isLow = m.delta_pct < -10;
                            const isCritical = m.delta_pct > 25 || m.delta_pct < -25;

                            const currentColor = isCritical ? 'var(--status-danger-600, #E11D48)' : (isHigh || isLow) ? '#EA580C' : 'var(--status-success-600, #059669)';
                            const deltaColor = isCritical ? 'var(--status-danger-600, #E11D48)' : (isHigh || isLow) ? '#EA580C' : 'var(--text-tertiary, #64748B)';
                            const iconColor = isCritical ? 'var(--status-danger-600, #E11D48)' : (isHigh || isLow) ? '#EA580C' : 'var(--text-muted, #94A3B8)';

                            return (
                                <tr key={idx} className="transition-colors"
                                    style={{ borderBottom: '1px solid var(--border-light, #F1F5F9)' }}
                                    onMouseEnter={e => (e.currentTarget.style.background = 'var(--hover-row, #F8FAFC)')}
                                    onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                                >
                                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium" style={{ color: 'var(--text-primary, #0F172A)' }}>
                                        {m.parameter}
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right" style={{ color: 'var(--text-muted, #94A3B8)', borderLeft: '1px solid var(--border-light, #F1F5F9)' }}>
                                        {m.normal}
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold" style={{ color: currentColor, borderLeft: '1px solid var(--border-light, #F1F5F9)' }}>
                                        {m.current}
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right" style={{ borderLeft: '1px solid var(--border-light, #F1F5F9)' }}>
                                        <div className="flex items-center justify-end gap-1">
                                            {m.delta_pct > 0 ? (
                                                <TrendingUp className="w-4 h-4" style={{ color: iconColor }} />
                                            ) : m.delta_pct < 0 ? (
                                                <TrendingDown className="w-4 h-4" style={{ color: iconColor }} />
                                            ) : (
                                                <Minus className="w-4 h-4" style={{ color: 'var(--text-muted, #94A3B8)' }} />
                                            )}
                                            <span className="font-medium" style={{ color: deltaColor }}>
                                                {m.delta_pct > 0 ? '+' : ''}{m.delta_pct}%
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
