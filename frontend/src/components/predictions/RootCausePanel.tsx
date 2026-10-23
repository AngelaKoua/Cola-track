import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { FileSearch } from "lucide-react";

interface RootCausePanelProps {
    reason: string;
}

export function RootCausePanel({ reason }: RootCausePanelProps) {
    return (
        <Card className="shadow-sm border-slate-200">
            <CardHeader className="bg-slate-50 border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                    <FileSearch className="h-5 w-5 text-indigo-600" />
                    <CardTitle className="text-base font-semibold text-slate-800">Root Cause Analysis</CardTitle>
                </div>
            </CardHeader>
            <CardContent className="pt-4">
                <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-md text-indigo-900 font-medium">
                    {reason || "System operations are normal. No critical root causes identified."}
                </div>
            </CardContent>
        </Card>
    );
}
