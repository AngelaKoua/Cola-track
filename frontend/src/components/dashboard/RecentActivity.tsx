import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { ClipboardCheck, Wrench, UserCheck } from "lucide-react"

const recentActivities = [
    {
        id: 1,
        message: "Relevé manuel Osmoseur effectué",
        time: "10:30",
        user: "J. Doe",
        icon: ClipboardCheck
    },
    {
        id: 2,
        message: "Validation fin de lot Remplisseuse",
        time: "09:45",
        user: "A. Smith",
        icon: UserCheck
    },
    {
        id: 3,
        message: "Intervention maintenancier terminée",
        time: "08:15",
        user: "Tech Lead",
        icon: Wrench
    },
]

export function RecentActivity() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle className="text-[#1F2937]">Activité Récente</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {recentActivities.map((activity) => (
                        <div key={activity.id} className="flex items-start gap-3 text-sm">
                            <activity.icon className="h-4 w-4 text-gray-400 mt-0.5" />
                            <div className="flex-1">
                                <p className="text-gray-700">{activity.message}</p>
                                <p className="text-xs text-gray-400 mt-0.5">{activity.time} - {activity.user}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}
