'use client';

import React from 'react';
import { Recommendation } from '@/services/mlService';
import { Shield, Clock, AlertTriangle, ChevronRight, Zap } from 'lucide-react';

interface RecommendationCardsProps {
    recommendation: Recommendation | null;
    isLoading: boolean;
}

export default function RecommendationCards({ recommendation, isLoading }: RecommendationCardsProps) {
    if (isLoading) {
        return <div className="p-6 rounded-xl shadow-sm flex items-center justify-center min-h-[300px]"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--secondary-500, #2563EB)' }}></div>
        </div>;
    }

    if (!recommendation) {
        return (
            <div className="p-6 rounded-xl"
                style={{ background: 'var(--status-success-50, #ECFDF5)', border: '1px solid var(--status-success-100, #D1FAE5)' }}>
                <div className="flex items-center gap-3">
                    <Shield className="w-8 h-8" style={{ color: 'var(--status-success-600, #059669)' }} />
                    <div>
                        <h3 className="text-lg font-semibold" style={{ color: 'var(--status-success-600, #059669)' }}>Aucune action requise</h3>
                        <p className="text-sm" style={{ color: 'var(--status-success-600, #059669)', opacity: 0.8 }}>La machine fonctionne dans les paramètres optimaux.</p>
                    </div>
                </div>
            </div>
        );
    }

    const priorityConfig: Record<string, { color: string; bgColor: string; borderColor: string; icon: React.ReactNode }> = {
        LOW: {
            color: 'var(--status-success-600, #059669)',
            bgColor: 'var(--status-success-50, #ECFDF5)',
            borderColor: 'var(--status-success-100, #D1FAE5)',
            icon: <Shield className="w-6 h-6" style={{ color: 'var(--status-success-600, #059669)' }} />
        },
        MEDIUM: {
            color: 'var(--status-warning-500, #F59E0B)',
            bgColor: 'var(--status-warning-50, #FFFBEB)',
            borderColor: 'var(--status-warning-100, #FEF3C7)',
            icon: <Clock className="w-6 h-6" style={{ color: 'var(--status-warning-500, #F59E0B)' }} />
        },
        HIGH: {
            color: '#EA580C',
            bgColor: '#FFF7ED',
            borderColor: '#FFEDD5',
            icon: <AlertTriangle className="w-6 h-6" style={{ color: '#EA580C' }} />
        },
        CRITICAL: {
            color: 'var(--status-danger-600, #E11D48)',
            bgColor: 'var(--status-danger-50, #FFF1F2)',
            borderColor: 'var(--status-danger-100, #FFE4E6)',
            icon: <Zap className="w-6 h-6" style={{ color: 'var(--status-danger-600, #E11D48)' }} />
        }
    };

    const config = priorityConfig[recommendation.priority] || priorityConfig['MEDIUM'];

    return (
        <div className="rounded-xl overflow-hidden" style={{ background: config.bgColor, border: `2px solid ${config.borderColor}` }}>
            {/* Header */}
            <div className="p-5 flex items-start gap-4">
                <div className="flex-shrink-0 mt-1">{config.icon}</div>
                <div className="flex-grow">
                    <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs font-bold uppercase tracking-widest px-2 py-0.5 rounded-md"
                            style={{ color: config.color, border: `1px solid ${config.borderColor}` }}>
                            {recommendation.priority}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded" style={{ color: 'var(--text-tertiary, #64748B)', background: 'rgba(255,255,255,0.6)' }}>
                            Type: {recommendation.action_type}
                        </span>
                    </div>
                    <p className="text-base font-semibold leading-relaxed" style={{ color: config.color }}>
                        {recommendation.action}
                    </p>
                </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-px bg-black/5">
                {/* Deadline */}
                <div className="bg-white/60 p-4">
                    <p className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--text-tertiary, #64748B)' }}>Délai</p>
                    <p className="text-lg font-bold" style={{ color: config.color }}>
                        {recommendation.deadline_label}
                    </p>
                </div>

                {/* RUL */}
                <div className="bg-white/60 p-4">
                    <p className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--text-tertiary, #64748B)' }}>RUL Estimé</p>
                    <p className="text-lg font-bold" style={{ color: 'var(--text-primary, #0F172A)' }}>
                        {recommendation.estimated_rul_hours
                            ? `${recommendation.estimated_rul_hours}h`
                            : 'Stable'
                        }
                    </p>
                </div>

                {/* Confidence */}
                <div className="bg-white/60 p-4">
                    <p className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--text-tertiary, #64748B)' }}>Confiance Diag.</p>
                    <p className="text-lg font-bold" style={{ color: 'var(--text-primary, #0F172A)' }}>
                        {recommendation.confidence !== null
                            ? `${recommendation.confidence}%`
                            : 'N/A'
                        }
                    </p>
                </div>
            </div>

            {/* Justification */}
            <div className="p-4 bg-white/40 border-t border-black/5">
                <p className="text-xs font-semibold uppercase mb-2" style={{ color: 'var(--text-tertiary, #64748B)' }}>Justification</p>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary, #334155)' }}>{recommendation.justification}</p>
            </div>

            {/* Impact */}
            <div className="p-4 bg-white/30 border-t border-black/5">
                <p className="text-xs font-semibold uppercase mb-2 flex items-center gap-1" style={{ color: 'var(--status-danger-600, #E11D48)' }}>
                    <AlertTriangle className="w-3 h-3" />
                    Impact si aucune action
                </p>
                <p className="text-sm font-medium" style={{ color: 'var(--status-danger-600, #E11D48)' }}>{recommendation.impact_if_ignored}</p>
            </div>
        </div>
    );
}
