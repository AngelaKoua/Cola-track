'use client';

import React from 'react';
import { FeatureContribution } from '@/services/mlService';
import { BarChart3 } from 'lucide-react';

interface FeatureImportanceChartProps {
    features: FeatureContribution[];
    explanationText: string;
    isLoading: boolean;
}

export default function FeatureImportanceChart({ features, explanationText, isLoading }: FeatureImportanceChartProps) {
    if (isLoading) {
        return <div className="p-6 rounded-xl shadow-sm flex items-center justify-center min-h-[300px]"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--secondary-500, #2563EB)' }}></div>
        </div>;
    }

    if (!features || features.length === 0) return null;

    const maxImportance = Math.max(...features.map(f => f.importance_pct));

    // Design system chart-inspired gradient for feature bars
    const barColors = ['#2563EB', '#3B82F6', '#60A5FA', '#94A3B8'];

    return (
        <div className="p-6 rounded-xl shadow-sm"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <h3 className="text-lg font-semibold mb-2 flex items-center" style={{ color: 'var(--text-primary, #0F172A)' }}>
                <BarChart3 className="w-5 h-5 mr-2" style={{ color: 'var(--secondary-500, #2563EB)' }} />
                Feature Importance (XGBoost)
            </h3>
            <p className="text-sm mb-6" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                Contribution relative de chaque variable à la prédiction de panne.
            </p>

            <div className="space-y-3">
                {features.map((f, idx) => {
                    const barWidth = maxImportance > 0 ? (f.importance_pct / maxImportance) * 100 : 0;
                    const isTopThree = idx < 3;
                    const barColor = idx < barColors.length ? barColors[idx] : barColors[barColors.length - 1];

                    return (
                        <div key={idx} className="group">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-sm" style={{ fontWeight: isTopThree ? 600 : 400, color: isTopThree ? 'var(--text-primary, #0F172A)' : 'var(--text-tertiary, #64748B)' }}>
                                    {f.label}
                                </span>
                                <span className="text-sm font-mono" style={{ fontWeight: isTopThree ? 700 : 400, color: isTopThree ? 'var(--secondary-500, #2563EB)' : 'var(--text-muted, #94A3B8)' }}>
                                    {f.importance_pct}%
                                </span>
                            </div>
                            <div className="w-full rounded-full h-2.5 overflow-hidden" style={{ background: 'var(--bg-elevated, #F1F5F9)' }}>
                                <div
                                    className="h-2.5 rounded-full transition-all duration-700"
                                    style={{ width: `${barWidth}%`, background: barColor }}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>

            {explanationText && (
                <div className="mt-6 p-4 rounded-lg" style={{ background: 'var(--secondary-50, #EFF6FF)', border: '1px solid var(--secondary-100, #DBEAFE)' }}>
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--secondary-600, #1E40AF)' }}>
                        <span className="font-semibold">Interprétation IA :</span> {explanationText}
                    </p>
                </div>
            )}
        </div>
    );
}
