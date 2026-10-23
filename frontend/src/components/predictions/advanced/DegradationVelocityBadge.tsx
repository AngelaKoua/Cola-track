'use client';

import React from 'react';
import { SituationReport } from '@/services/mlService';
import { Activity } from 'lucide-react';

interface DegradationVelocityBadgeProps {
    situation: SituationReport | null;
}

export default function DegradationVelocityBadge({ situation }: DegradationVelocityBadgeProps) {
    if (!situation) return null;

    const velocityConfig: Record<string, { color: string; bg: string; border: string; label: string; icon: string }> = {
        improving: { color: 'var(--status-success-600)', bg: 'var(--status-success-50)', border: 'var(--status-success-100)', label: 'En amélioration', icon: '📈' },
        stable: { color: 'var(--secondary-500)', bg: 'var(--secondary-50)', border: 'var(--secondary-100)', label: 'Stable', icon: '➡️' },
        slow_degradation: { color: 'var(--status-warning-500)', bg: 'var(--status-warning-50)', border: 'var(--status-warning-100)', label: 'Dégradation lente', icon: '📉' },
        degrading: { color: '#EA580C', bg: '#FFF7ED', border: '#FFEDD5', label: 'Dégradation active', icon: '⚠️' },
        rapid_degradation: { color: 'var(--status-danger-600)', bg: 'var(--status-danger-50)', border: 'var(--status-danger-100)', label: 'Dégradation rapide', icon: '🔴' }
    };

    const statusConfig: Record<string, { color: string; bg: string }> = {
        NOMINAL: { color: 'var(--status-success-600)', bg: 'var(--status-success-50)' },
        CAUTION: { color: 'var(--status-warning-500)', bg: 'var(--status-warning-50)' },
        WARNING: { color: '#EA580C', bg: '#FFF7ED' },
        CRITICAL: { color: 'var(--status-danger-600)', bg: 'var(--status-danger-50)' }
    };

    const vConfig = velocityConfig[situation.velocity_label] || velocityConfig['stable'];
    const sConfig = statusConfig[situation.status] || statusConfig['NOMINAL'];

    return (
        <div className="p-4 rounded-xl flex items-center justify-between transition-all duration-200"
            style={{ background: vConfig.bg, border: `1px solid ${vConfig.border}` }}>
            <div className="flex items-center gap-3">
                <span className="text-2xl">{vConfig.icon}</span>
                <div>
                    <p className="text-sm font-semibold" style={{ color: vConfig.color }}>{vConfig.label}</p>
                    <p className="text-xs" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                        Vélocité: {situation.degradation_velocity > 0 ? '+' : ''}{situation.degradation_velocity} pts/intervalle
                    </p>
                </div>
            </div>
            <div className="flex items-center gap-3">
                <span className="px-3 py-1 rounded-lg text-xs font-bold"
                    style={{ color: sConfig.color, background: sConfig.bg }}>
                    {situation.status}
                </span>
                {situation.estimated_rul_hours !== null && (
                    <div className="text-right">
                        <p className="text-xs" style={{ color: 'var(--text-muted, #94A3B8)' }}>RUL estimé</p>
                        <p className="text-sm font-bold" style={{ color: 'var(--text-primary, #0F172A)' }}>{situation.estimated_rul_hours}h</p>
                    </div>
                )}
            </div>
        </div>
    );
}
