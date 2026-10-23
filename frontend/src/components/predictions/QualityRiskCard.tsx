import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { AlertTriangle } from "lucide-react";

interface QualityRiskCardProps {
    risk: number | null;
}

export function QualityRiskCard({ risk }: QualityRiskCardProps) {
    if (risk === null) {
        return (
            <Card className="shadow-sm border-2 rounded-xl" style={{ background: 'var(--bg-elevated, #F1F5F9)', borderColor: 'var(--border-default, #E2E8F0)' }}>
                <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                    <CardTitle className="text-sm font-semibold" style={{ color: 'var(--text-secondary, #334155)' }}>Quality Risk</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-lg font-medium" style={{ color: 'var(--text-muted, #94A3B8)' }}>N/A</div>
                </CardContent>
            </Card>
        );
    }

    const percent = risk * 100;

    let colorStyle = { color: 'var(--status-success-600, #059669)' };
    let bgStyle = {
        background: 'var(--status-success-50, #ECFDF5)',
        borderColor: 'var(--status-success-100, #D1FAE5)',
    };

    if (percent > 50) {
        colorStyle = { color: 'var(--status-danger-600, #E11D48)' };
        bgStyle = {
            background: 'var(--status-danger-50, #FFF1F2)',
            borderColor: 'var(--status-danger-100, #FFE4E6)',
        };
    } else if (percent > 20) {
        colorStyle = { color: 'var(--status-warning-500, #F59E0B)' };
        bgStyle = {
            background: 'var(--status-warning-50, #FFFBEB)',
            borderColor: 'var(--status-warning-100, #FEF3C7)',
        };
    }

    return (
        <Card className="shadow-sm border-2 rounded-xl transition-all duration-200 hover:shadow-md" style={bgStyle}>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-semibold" style={{ color: 'var(--text-secondary, #334155)' }}>Quality Risk</CardTitle>
                <AlertTriangle className="h-4 w-4" style={colorStyle} />
            </CardHeader>
            <CardContent>
                <div className="text-3xl font-black" style={colorStyle}>
                    {percent.toFixed(1)}%
                </div>
            </CardContent>
        </Card>
    );
}
