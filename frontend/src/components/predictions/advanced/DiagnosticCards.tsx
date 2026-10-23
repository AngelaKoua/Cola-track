'use client';

import React from 'react';
import { Diagnosis } from '@/services/mlService';
import { Target, CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react';

interface DiagnosticCardsProps {
    diagnoses: Diagnosis[];
    isLoading: boolean;
}

export default function DiagnosticCards({ diagnoses, isLoading }: DiagnosticCardsProps) {
    const [expanded, setExpanded] = React.useState<number | null>(0);

    if (isLoading) {
        return <div className="p-6 rounded-xl shadow-sm flex items-center justify-center min-h-[300px]"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--secondary-500, #2563EB)' }}></div>
        </div>;
    }

    if (!diagnoses || diagnoses.length === 0) {
        return (
            <div className="p-6 rounded-xl shadow-sm"
                style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
                <h3 className="text-lg font-semibold mb-4 flex items-center" style={{ color: 'var(--text-primary, #0F172A)' }}>
                    <Target className="w-5 h-5 mr-2" style={{ color: 'var(--secondary-500, #2563EB)' }} />
                    Root Cause Analysis
                </h3>
                <div className="flex flex-col items-center justify-center py-8" style={{ color: 'var(--text-muted, #94A3B8)' }}>
                    <CheckCircle2 className="w-10 h-10 mb-3" style={{ color: 'var(--status-success-600, #059669)' }} />
                    <p className="font-medium" style={{ color: 'var(--text-secondary, #334155)' }}>Aucune cause de défaillance identifiée</p>
                    <p className="text-sm mt-1" style={{ color: 'var(--text-muted, #94A3B8)' }}>Les patterns de panne connus ne sont pas détectés actuellement.</p>
                </div>
            </div>
        );
    }

    const severityStyle = (severity: string) => {
        switch (severity) {
            case 'critical': return { borderLeft: '4px solid var(--status-danger-600, #E11D48)', background: 'var(--status-danger-50, #FFF1F2)' };
            case 'high': return { borderLeft: '4px solid #EA580C', background: '#FFF7ED' };
            default: return { borderLeft: '4px solid var(--status-warning-500, #F59E0B)', background: 'var(--status-warning-50, #FFFBEB)' };
        }
    };

    const confidenceStyle = (confidence: number) => {
        if (confidence >= 70) return { color: 'var(--status-danger-600, #E11D48)', background: 'var(--status-danger-50, #FFF1F2)' };
        if (confidence >= 40) return { color: '#EA580C', background: '#FFF7ED' };
        return { color: 'var(--status-warning-500, #F59E0B)', background: 'var(--status-warning-50, #FFFBEB)' };
    };

    return (
        <div className="p-6 rounded-xl shadow-sm"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <h3 className="text-lg font-semibold mb-6 flex items-center" style={{ color: 'var(--text-primary, #0F172A)' }}>
                <Target className="w-5 h-5 mr-2" style={{ color: 'var(--secondary-500, #2563EB)' }} />
                Root Cause Analysis
                <span className="ml-auto text-xs font-medium px-2 py-1 rounded"
                    style={{ color: 'var(--text-tertiary, #64748B)', background: 'var(--bg-elevated, #F1F5F9)' }}>
                    {diagnoses.length} cause{diagnoses.length > 1 ? 's' : ''} possible{diagnoses.length > 1 ? 's' : ''}
                </span>
            </h3>

            <div className="space-y-4">
                {diagnoses.map((diag, idx) => (
                    <div key={idx} className="rounded-lg overflow-hidden transition-all" style={severityStyle(diag.severity)}>
                        <button
                            onClick={() => setExpanded(expanded === idx ? null : idx)}
                            className="w-full flex items-center justify-between p-4 text-left hover:bg-black/5 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <span className="text-2xl font-bold px-3 py-1 rounded-lg" style={confidenceStyle(diag.confidence)}>
                                    {diag.confidence}%
                                </span>
                                <div>
                                    <h4 className="font-semibold" style={{ color: 'var(--text-primary, #0F172A)' }}>{diag.diagnosis}</h4>
                                    <p className="text-sm" style={{ color: 'var(--text-tertiary, #64748B)' }}>{diag.description}</p>
                                </div>
                            </div>
                            {expanded === idx
                                ? <ChevronUp className="w-5 h-5" style={{ color: 'var(--text-muted, #94A3B8)' }} />
                                : <ChevronDown className="w-5 h-5" style={{ color: 'var(--text-muted, #94A3B8)' }} />
                            }
                        </button>

                        {expanded === idx && (
                            <div className="px-4 pb-4 pt-0 border-t border-black/5">
                                <div className="mt-3">
                                    <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-tertiary, #64748B)' }}>
                                        Conditions vérifiées ({diag.matched_conditions}/{diag.total_conditions})
                                    </p>
                                    <div className="space-y-2">
                                        {diag.evidence.map((ev, eidx) => (
                                            <div key={eidx} className="flex items-center gap-2 text-sm bg-white/50 p-2 rounded">
                                                {ev.match ? (
                                                    <CheckCircle2 className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--status-success-600, #059669)' }} />
                                                ) : (
                                                    <XCircle className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--border-default, #E2E8F0)' }} />
                                                )}
                                                <span style={{ color: ev.match ? 'var(--text-primary, #0F172A)' : 'var(--text-muted, #94A3B8)', fontWeight: ev.match ? 500 : 400 }}>
                                                    {ev.parameter}: attendu <code className="px-1 rounded text-xs" style={{ background: 'var(--bg-sunken, #E2E8F0)' }}>{ev.expected}</code>, observé <code className="px-1 rounded text-xs" style={{ background: 'var(--bg-sunken, #E2E8F0)' }}>{ev.actual}</code>
                                                </span>
                                                {ev.current_value !== null && (
                                                    <span className="ml-auto text-xs" style={{ color: 'var(--text-muted, #94A3B8)' }}>({ev.current_value})</span>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
                                    <div className="bg-white/60 p-3 rounded border border-black/5">
                                        <p className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--text-tertiary, #64748B)' }}>Action recommandée</p>
                                        <p className="text-sm font-medium" style={{ color: 'var(--text-primary, #0F172A)' }}>{diag.recommended_action}</p>
                                    </div>
                                    <div className="bg-white/60 p-3 rounded border border-black/5">
                                        <p className="text-xs font-semibold uppercase mb-1" style={{ color: 'var(--text-tertiary, #64748B)' }}>Impact si inaction</p>
                                        <p className="text-sm font-medium" style={{ color: 'var(--text-primary, #0F172A)' }}>{diag.rul_impact}</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
