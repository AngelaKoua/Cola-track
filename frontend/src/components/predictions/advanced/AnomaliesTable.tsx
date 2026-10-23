'use client';

import React from 'react';
import { HistoricalRUL } from '@/services/mlService';
import { AlertCircle, CheckCircle } from 'lucide-react';

interface AnomaliesTableProps {
    history: HistoricalRUL[];
    isLoading: boolean;
}

export default function AnomaliesTable({ history, isLoading }: AnomaliesTableProps) {
    if (isLoading) return null;

    const anomalies = history.filter(h => h.alert_level > 0 || h.failure_probability > 0.5);

    if (anomalies.length === 0) {
        return (
            <div className="p-6 rounded-xl shadow-sm h-full flex flex-col items-center justify-center text-center"
                style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
                <CheckCircle className="w-10 h-10 mb-3" style={{ color: 'var(--status-success-600, #059669)' }} />
                <h3 className="text-lg font-medium" style={{ color: 'var(--text-primary, #0F172A)' }}>Aucune Anomalie Récente</h3>
                <p className="text-sm mt-1" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                    L'intelligence artificielle n'a détecté aucun comportement hors norme sur les deux dernières heures.
                </p>
            </div>
        );
    }

    return (
        <div className="p-6 rounded-xl shadow-sm flex flex-col"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <h3 className="text-lg font-semibold mb-4 flex items-center flex-shrink-0" style={{ color: 'var(--text-primary, #0F172A)' }}>
                <AlertCircle className="w-5 h-5 mr-2" style={{ color: 'var(--status-danger-600, #E11D48)' }} />
                Anomalies Récentes (IA)
            </h3>

            <div className="overflow-auto max-h-[400px]">
                <table className="min-w-full">
                    <thead className="sticky top-0" style={{ background: 'var(--bg-elevated, #F1F5F9)' }}>
                        <tr style={{ borderBottom: '1px solid var(--border-default, #E2E8F0)' }}>
                            <th scope="col" className="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                Heure
                            </th>
                            <th scope="col" className="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                Sévérité
                            </th>
                            <th scope="col" className="px-3 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                Prob. Panne
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {anomalies.map((anomaly, idx) => (
                            <tr key={idx} className="transition-colors"
                                style={{ borderBottom: '1px solid var(--border-light, #F1F5F9)' }}
                                onMouseEnter={e => (e.currentTarget.style.background = 'var(--hover-row, #F8FAFC)')}
                                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                            >
                                <td className="px-3 py-3 whitespace-nowrap text-sm" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                    {new Date(anomaly.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </td>
                                <td className="px-3 py-3 whitespace-nowrap">
                                    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-semibold ring-1 ring-inset ${anomaly.alert_level === 3 ? 'bg-rose-50 text-rose-700 ring-rose-200' :
                                        anomaly.alert_level === 2 ? 'bg-orange-50 text-orange-700 ring-orange-200' :
                                            'bg-amber-50 text-amber-700 ring-amber-200'
                                        }`}>
                                        {anomaly.alert_level === 3 ? 'Critique' : anomaly.alert_level === 2 ? 'Élevé' : 'Mineur'}
                                    </span>
                                </td>
                                <td className="px-3 py-3 whitespace-nowrap text-sm text-right font-semibold" style={{ color: 'var(--text-primary, #0F172A)', borderLeft: '1px solid var(--border-light, #F1F5F9)' }}>
                                    {(anomaly.failure_probability * 100).toFixed(1)}%
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
