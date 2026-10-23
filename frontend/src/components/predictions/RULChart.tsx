import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ActivitySquare } from "lucide-react";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

interface HistoricalRUL {
    timestamp: string;
    health_index: number;
    failure_probability: number;
    alert_level: number;
    timeShort?: string;
}

interface RULChartProps {
    history: HistoricalRUL[];
}

export function RULChart({ history }: RULChartProps) {
    if (!history || history.length === 0) {
        return (
            <Card className="shadow-sm rounded-xl" style={{ border: '1px solid var(--border-default, #E2E8F0)' }}>
                <CardHeader className="pb-2">
                    <CardTitle className="text-base font-semibold" style={{ color: 'var(--text-primary, #0F172A)' }}>Health Degradation Chart</CardTitle>
                </CardHeader>
                <CardContent className="h-64 flex items-center justify-center" style={{ color: 'var(--text-muted, #94A3B8)' }}>
                    No historical data available.
                </CardContent>
            </Card>
        );
    }

    const chartData = history.map(h => ({
        ...h,
        timeShort: h.timeShort || new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }));

    return (
        <Card className="shadow-sm rounded-xl overflow-hidden" style={{ border: '1px solid var(--border-default, #E2E8F0)' }}>
            <CardHeader className="pb-3" style={{ background: 'var(--bg-elevated, #F1F5F9)', borderBottom: '1px solid var(--border-default, #E2E8F0)' }}>
                <div className="flex items-center gap-2">
                    <ActivitySquare className="h-5 w-5" style={{ color: 'var(--secondary-500, #2563EB)' }} />
                    <CardTitle className="text-base font-semibold" style={{ color: 'var(--text-primary, #0F172A)' }}>Health Degradation Chart</CardTitle>
                </div>
            </CardHeader>
            <CardContent className="pt-4">
                <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                            <XAxis dataKey="timeShort" tick={{ fontSize: 12, fill: '#64748B' }} tickMargin={10} />
                            <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#64748B' }} />
                            <Tooltip
                                contentStyle={{ borderRadius: '10px', border: '1px solid #E2E8F0', boxShadow: '0 4px 12px rgba(0,0,0,0.08)', background: '#FFFFFF' }}
                                labelStyle={{ fontWeight: 'bold', color: '#0F172A', marginBottom: '4px' }}
                            />
                            <ReferenceLine y={75} stroke="#F59E0B" strokeDasharray="3 3" label={{ position: "insideTopLeft", value: "Warning", fill: "#F59E0B", fontSize: 10 }} />
                            <ReferenceLine y={50} stroke="#E11D48" strokeDasharray="3 3" label={{ position: "insideTopLeft", value: "Critical", fill: "#E11D48", fontSize: 10 }} />
                            <Line
                                type="monotone"
                                dataKey="health_index"
                                stroke="#2563EB"
                                strokeWidth={3}
                                dot={{ r: 3, fill: '#2563EB' }}
                                activeDot={{ r: 6 }}
                                name="Health Index"
                                animationDuration={1000}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
