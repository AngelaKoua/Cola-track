'use client';

import React from 'react';
import { TimelineEvent } from '@/services/mlService';
import { AlertTriangle, Clock, Info, CheckCircle, Wrench } from 'lucide-react';

interface TimelinePanelProps {
    events: TimelineEvent[];
    isLoading: boolean;
}

export default function TimelinePanel({ events, isLoading }: TimelinePanelProps) {
    if (isLoading) {
        return <div className="p-6 rounded-xl shadow-sm flex items-center justify-center min-h-[400px]"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--secondary-500, #2563EB)' }}></div>
        </div>;
    }

    if (!events || events.length === 0) {
        return (
            <div className="p-6 rounded-xl shadow-sm"
                style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary, #0F172A)' }}>Historical Event Timeline</h3>
                <div className="flex flex-col items-center justify-center py-12" style={{ color: 'var(--text-muted, #94A3B8)' }}>
                    <Clock className="w-12 h-12 mb-4" style={{ color: 'var(--border-default, #E2E8F0)' }} />
                    <p>No recent events or alerts found.</p>
                </div>
            </div>
        );
    }

    const getIconInfo = (type: string, severity: string) => {
        if (type === 'Predictive Alert') {
            if (severity === 'Halt') return { icon: AlertTriangle, color: 'var(--status-danger-600, #E11D48)', bg: 'var(--status-danger-50, #FFF1F2)' };
            if (severity === 'Critical') return { icon: AlertTriangle, color: '#EA580C', bg: '#FFF7ED' };
            return { icon: Info, color: 'var(--status-warning-500, #F59E0B)', bg: 'var(--status-warning-50, #FFFBEB)' };
        }

        if (severity === 'Critique' || severity === 'Élevé') return { icon: Wrench, color: 'var(--status-danger-600, #E11D48)', bg: 'var(--status-danger-50, #FFF1F2)' };
        if (severity === 'Moyen' || severity === 'Faible') return { icon: Wrench, color: 'var(--status-warning-500, #F59E0B)', bg: 'var(--status-warning-50, #FFFBEB)' };

        return { icon: CheckCircle, color: 'var(--secondary-500, #2563EB)', bg: 'var(--secondary-50, #EFF6FF)' };
    };

    return (
        <div className="p-6 rounded-xl shadow-sm flex flex-col"
            style={{ background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E2E8F0)' }}>
            <h3 className="text-lg font-semibold mb-6 flex items-center flex-shrink-0" style={{ color: 'var(--text-primary, #0F172A)' }}>
                <Clock className="w-5 h-5 mr-2" style={{ color: 'var(--secondary-500, #2563EB)' }} />
                Event Timeline
            </h3>

            <div className="relative ml-3 overflow-y-auto max-h-[500px] pr-2" style={{ borderLeft: '1px solid var(--border-default, #E2E8F0)' }}>
                {events.map((event, idx) => {
                    const { icon: Icon, color, bg } = getIconInfo(event.type, event.severity);

                    return (
                        <div key={idx} className="mb-8 ml-6 group">
                            <span className="absolute flex items-center justify-center w-8 h-8 rounded-full -left-4 ring-4 ring-white"
                                style={{ background: bg, color: color }}>
                                <Icon className="w-4 h-4" />
                            </span>

                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-1">
                                <h4 className="text-sm font-semibold" style={{ color: 'var(--text-primary, #0F172A)' }}>{event.title}</h4>
                                <time className="text-xs font-medium px-2 py-1 rounded" style={{ color: 'var(--text-tertiary, #64748B)', background: 'var(--bg-elevated, #F1F5F9)' }}>
                                    {new Date(event.timestamp).toLocaleString()}
                                </time>
                            </div>

                            <p className="text-sm mt-1" style={{ color: 'var(--text-tertiary, #64748B)' }}>{event.description}</p>

                            <div className="mt-2 flex items-center gap-2">
                                <span className="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium"
                                    style={{ background: 'var(--bg-elevated, #F1F5F9)', color: 'var(--text-tertiary, #64748B)' }}>
                                    {event.type}
                                </span>
                                <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-semibold ${event.severity === 'Halt' || event.severity === 'Critique' ? 'bg-rose-50 text-rose-700' :
                                    event.severity === 'Critical' || event.severity === 'Élevé' ? 'bg-orange-50 text-orange-700' :
                                        'bg-amber-50 text-amber-700'
                                    }`}>
                                    Severity: {event.severity}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
