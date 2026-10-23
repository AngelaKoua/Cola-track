'use client';

import React from 'react';
import { RULEstimate } from '@/services/mlService';
import { Timer, TrendingDown, Gauge } from 'lucide-react';

interface RULEstimationPanelProps {
    rul: RULEstimate | null;
    isLoading: boolean;
}

export default function RULEstimationPanel({ rul, isLoading }: RULEstimationPanelProps) {
    if (isLoading || !rul) return null;

    const riskConfig: Record<string, { color: string; bg: string; label: string }> = {
        stable: { color: 'var(--status-success-600, #059669)', bg: 'var(--status-success-50, #ECFDF5)', label: 'Stable' },
        low: { color: 'var(--secondary-500, #2563EB)', bg: 'var(--secondary-50, #EFF6FF)', label: 'Risque Faible' },
        moderate: { color: 'var(--status-warning-500, #F59E0B)', bg: 'var(--status-warning-50, #FFFBEB)', label: 'Risque Modéré' },
        high: { color: '#EA580C', bg: '#FFF7ED', label: 'Risque Élevé' },
        imminent: { color: 'var(--status-danger-600, #E11D48)', bg: 'var(--status-danger-50, #FFF1F2)', label: 'Imminent' }
    };

    const config = riskConfig[rul.risk_level] || riskConfig['stable'];

    const velocityIcons: Record<string, string> = {
        improving: '📈',
        stable: '➡️',
        slow_degradation: '📉',
        degrading: '⚠️',
        rapid_degradation: '🔴'
    };

    return (
        <div className="p-6 rounded-xl shadow-sm"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <h3 className="text-lg font-semibold mb-4 flex items-center" style={{ color: 'var(--text-primary, #0F172A)' }}>
                <Timer className="w-5 h-5 mr-2" style={{ color: 'var(--secondary-500, #2563EB)' }} />
                Remaining Useful Life (RUL)
            </h3>

            {/* Risk Level Badge */}
            <div className="flex items-center gap-3 mb-6">
                <span className="px-3 py-1.5 rounded-lg text-sm font-bold"
                    style={{ color: config.color, background: config.bg }}>
                    {config.label}
                </span>
                <span className="text-sm" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                    {velocityIcons[rul.velocity_label] || '➡️'} Vitesse: {rul.velocity_label.replace('_', ' ')}
                </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-4">
                {/* Health */}
                <div className="p-4 rounded-lg" style={{ background: 'var(--bg-elevated, #F1F5F9)' }}>
                    <div className="flex items-center gap-2 mb-1">
                        <Gauge className="w-4 h-4" style={{ color: 'var(--text-muted, #94A3B8)' }} />
                        <p className="text-xs font-semibold uppercase" style={{ color: 'var(--text-tertiary, #64748B)' }}>Health Actuel</p>
                    </div>
                    <p className="text-2xl font-bold" style={{ color: 'var(--text-primary, #0F172A)' }}>{rul.current_health}</p>
                </div>

                {/* Velocity */}
                <div className="p-4 rounded-lg" style={{ background: 'var(--bg-elevated, #F1F5F9)' }}>
                    <div className="flex items-center gap-2 mb-1">
                        <TrendingDown className="w-4 h-4" style={{ color: 'var(--text-muted, #94A3B8)' }} />
                        <p className="text-xs font-semibold uppercase" style={{ color: 'var(--text-tertiary, #64748B)' }}>Dégradation/h</p>
                    </div>
                    <p className="text-2xl font-bold"
                        style={{ color: rul.degradation_velocity_per_hour < 0 ? 'var(--status-danger-600, #E11D48)' : 'var(--status-success-600, #059669)' }}>
                        {rul.degradation_velocity_per_hour > 0 ? '+' : ''}{rul.degradation_velocity_per_hour} pts
                    </p>
                </div>

                {/* Time to Warning */}
                <div className="p-4 rounded-lg"
                    style={{ background: 'var(--status-warning-50, #FFFBEB)', border: '1px solid var(--status-warning-100, #FEF3C7)' }}>
                    <p className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--status-warning-500, #F59E0B)' }}>Seuil Warning (70)</p>
                    <p className="text-xl font-bold" style={{ color: '#B45309' }}>
                        {rul.hours_to_warning !== null ? `${rul.hours_to_warning}h` : '∞'}
                    </p>
                </div>

                {/* Time to Critical */}
                <div className="p-4 rounded-lg"
                    style={{ background: 'var(--status-danger-50, #FFF1F2)', border: '1px solid var(--status-danger-100, #FFE4E6)' }}>
                    <p className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--status-danger-600, #E11D48)' }}>Seuil Critique (50)</p>
                    <p className="text-xl font-bold" style={{ color: '#BE123C' }}>
                        {rul.hours_to_critical !== null ? `${rul.hours_to_critical}h` : '∞'}
                    </p>
                </div>
            </div>
        </div>
    );
}
