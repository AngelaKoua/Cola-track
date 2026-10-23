import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ClipboardList, CheckCircle2, AlertCircle, Wrench } from "lucide-react";

interface RecommendedActionPanelProps {
    healthIndex: number;
    alertLevel: number;
    failureProb: number;
}

export function RecommendedActionPanel({ healthIndex, alertLevel, failureProb }: RecommendedActionPanelProps) {
    let recommendations: string[] = [];
    let icon = <CheckCircle2 className="h-5 w-5 text-emerald-600" />;
    let headerColor = "text-emerald-800";
    let bgBox = "bg-emerald-50 border-emerald-100";

    // Logic based on status
    if (alertLevel === 3 || failureProb > 0.8 || healthIndex < 40) {
        icon = <AlertCircle className="h-5 w-5 text-red-600" />;
        headerColor = "text-red-800";
        bgBox = "bg-red-50 border-red-100";
        recommendations = [
            "Shutdown machine immediately to prevent catastrophic failure.",
            "Schedule emergency corrective maintenance within 1 hour.",
            "Inspect main mechanical components based on identified root cause."
        ];
    } else if (alertLevel === 2 || failureProb > 0.5 || healthIndex < 60) {
        icon = <Wrench className="h-5 w-5 text-orange-600" />;
        headerColor = "text-orange-800";
        bgBox = "bg-orange-50 border-orange-100";
        recommendations = [
            "Schedule preventive maintenance within next 24 hours.",
            "Reduce operation load if possible.",
            "Check fluid levels and perform sensory inspection of abnormal vibrations."
        ];
    } else if (alertLevel === 1 || healthIndex < 80) {
        icon = <ClipboardList className="h-5 w-5 text-amber-600" />;
        headerColor = "text-amber-800";
        bgBox = "bg-amber-50 border-amber-100";
        recommendations = [
            "Monitor closely during the next shift.",
            "Review telemetry patterns for any early signs of degradation.",
            "Ensure standard lubrication and cleaning protocols are followed."
        ];
    } else {
        recommendations = [
            "Continue normal operations.",
            "No immediate action required.",
            "System operating at optimal efficiency."
        ];
    }

    return (
        <Card className="shadow-sm border-slate-200">
            <CardHeader className="bg-slate-50 border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                    {icon}
                    <CardTitle className="text-base font-semibold text-slate-800">Recommended Maintenance Action</CardTitle>
                </div>
            </CardHeader>
            <CardContent className="pt-4">
                <div className={`p-4 rounded-md border ${bgBox}`}>
                    <ul className={`space-y-2 font-medium ${headerColor}`}>
                        {recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                                <span className="mt-1 flex-shrink-0">•</span>
                                <span>{rec}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </CardContent>
        </Card>
    );
}
