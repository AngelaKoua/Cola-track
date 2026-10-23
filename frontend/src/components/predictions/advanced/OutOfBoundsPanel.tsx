'use client';

import React from 'react';
import { ComparisonMetric } from '@/services/mlService';
import { AlertCircle } from 'lucide-react';

interface OutOfBoundsPanelProps {
    metrics: ComparisonMetric[];
    isLoading: boolean;
}

export default function OutOfBoundsPanel({ metrics, isLoading }: OutOfBoundsPanelProps) {
    if (isLoading) return null;

    const outOfBounds = metrics?.filter(m => Math.abs(m.delta_pct) > 15) || [];

    if (outOfBounds.length === 0) {
        return (
            <div className="p-4 rounded-xl flex items-center"
                style={{ background: 'var(--status-success-50, #ECFDF5)', border: '1px solid var(--status-success-100, #D1FAE5)' }}>
                <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: 'var(--status-success-100, #D1FAE5)' }}>
                        <svg className="w-5 h-5" style={{ color: 'var(--status-success-600, #059669)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                </div>
                <div className="ml-3">
                    <h3 className="text-sm font-medium" style={{ color: 'var(--status-success-600, #059669)' }}>All Parameters in Range</h3>
                    <p className="text-xs mt-1" style={{ color: 'var(--status-success-600, #059669)', opacity: 0.8 }}>Machine constraints are respected.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-5 rounded-xl" style={{ background: 'var(--status-danger-50, #FFF1F2)', border: '1px solid var(--status-danger-100, #FFE4E6)', borderLeft: '4px solid var(--status-danger-600, #E11D48)' }}>
            <h3 className="text-sm font-semibold flex items-center mb-3" style={{ color: 'var(--status-danger-600, #E11D48)' }}>
                <AlertCircle className="w-4 h-4 mr-2" />
                Parameters Out of Range
            </h3>

            <ul className="space-y-2">
                {outOfBounds.map((m, idx) => (
                    <li key={idx} className="flex justify-between items-center p-2 rounded text-sm"
                        style={{ background: 'rgba(255,255,255,0.6)', border: '1px solid var(--status-danger-100, #FFE4E6)' }}>
                        <span className="font-medium" style={{ color: 'var(--text-primary, #0F172A)' }}>{m.parameter}</span>
                        <div className="text-right">
                            <span className="font-bold" style={{ color: 'var(--status-danger-600, #E11D48)' }}>{m.current}</span>
                            <span className="text-xs ml-1" style={{ color: 'var(--text-muted, #94A3B8)' }}>(Normal: {m.normal})</span>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}
