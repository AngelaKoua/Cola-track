import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { AlertCircle, Clock, CheckCircle2 } from "lucide-react"

interface Alert {
    id: string
    message: string
    severity: "critical" | "warning" | "info"
    time: string
    machine: string
}

export function AlertList({ alerts }: { alerts: Alert[] }) {
    if (alerts.length === 0) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <CardTitle className="text-[#1F2937]">Alertes Actives</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center h-[200px] text-gray-500">
                    <CheckCircle2 className="h-12 w-12 text-[#2ECC71] mb-2" />
                    <p>Aucune alerte active</p>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle className="flex items-center justify-between text-[#1F2937]">
                    <span>Alertes & Anomalies</span>
                    <span className="text-xs font-normal px-2 py-1 bg-red-100 text-[#E74C3C] rounded-full">
                        {alerts.length} active{alerts.length > 1 ? 's' : ''}
                    </span>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    {alerts.map((alert) => (
                        <div key={alert.id} className="flex gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
                            <AlertCircle className={`h-5 w-5 shrink-0 ${alert.severity === "critical" ? "text-[#E74C3C]" :
                                    alert.severity === "warning" ? "text-[#F39C12]" : "text-[#1976D2]"
                                }`} />
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                    {alert.message}
                                </p>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                                        {alert.machine}
                                    </span>
                                    <span className="flex items-center text-xs text-gray-400">
                                        <Clock className="h-3 w-3 mr-1" />
                                        {alert.time}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}
