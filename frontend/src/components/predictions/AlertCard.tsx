import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ShieldAlert, ShieldCheck, Shield } from "lucide-react";

interface AlertCardProps {
    level: number;
}

export function AlertCard({ level }: AlertCardProps) {
    let config = {
        bg: 'var(--status-success-600, #059669)',
        text: '#FFFFFF',
        label: "LOW (Normal)",
        icon: <ShieldCheck className="h-10 w-10 text-white" />
    };

    if (level === 1) {
        config = {
            bg: 'var(--status-warning-500, #F59E0B)',
            text: 'var(--primary-900, #0F172A)',
            label: "MEDIUM (Warning)",
            icon: <Shield className="h-10 w-10" style={{ color: 'var(--primary-900, #0F172A)' }} />
        };
    } else if (level === 2) {
        config = {
            bg: 'var(--accent-red, #D92B2B)',
            text: '#FFFFFF',
            label: "HIGH (Action Required)",
            icon: <ShieldAlert className="h-10 w-10 text-white" />
        };
    } else if (level === 3) {
        config = {
            bg: 'var(--status-danger-600, #E11D48)',
            text: '#FFFFFF',
            label: "CRITICAL (Imminent Failure)",
            icon: <ShieldAlert className="h-10 w-10 text-white animate-pulse" />
        };
    }

    return (
        <Card className="shadow-lg border-0 overflow-hidden rounded-xl" style={{ background: config.bg }}>
            <CardContent className="p-6 flex items-center justify-between">
                <div>
                    <p className="text-sm font-semibold uppercase tracking-wider opacity-80" style={{ color: config.text }}>
                        Machine Alert Level
                    </p>
                    <p className="text-3xl font-black mt-1" style={{ color: config.text }}>
                        {config.label}
                    </p>
                </div>
                <div>{config.icon}</div>
            </CardContent>
        </Card>
    );
}
