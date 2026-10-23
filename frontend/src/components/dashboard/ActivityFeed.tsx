import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { AlertTriangle, CheckCircle, Info, Wrench } from "lucide-react"
import { cn } from "@/lib/utils"

const activities = [
    {
        id: 1,
        type: "alert",
        message: "Pression critique détectée sur Osmoseur 2",
        time: "Il y a 10 min",
        icon: AlertTriangle,
        color: "text-red-500",
        bg: "bg-red-50"
    },
    {
        id: 2,
        type: "maintenance",
        message: "Maintenance préventive terminée sur Remplisseuse 1",
        time: "Il y a 1h",
        icon: Wrench,
        color: "text-orange-500",
        bg: "bg-orange-50"
    },
    {
        id: 3,
        type: "success",
        message: "Cycle de nettoyage terminé avec succès",
        time: "Il y a 2h",
        icon: CheckCircle,
        color: "text-green-500",
        bg: "bg-green-50"
    },
    {
        id: 4,
        type: "info",
        message: "Mise à jour du firmware système",
        time: "Il y a 4h",
        icon: Info,
        color: "text-blue-500",
        bg: "bg-blue-50"
    },
]

export function ActivityFeed() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Activité Récente</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {activities.map((activity) => (
                        <div key={activity.id} className="flex items-start space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                            <div className={cn("p-2 rounded-full", activity.bg)}>
                                <activity.icon className={cn("h-4 w-4", activity.color)} />
                            </div>
                            <div className="flex-1 space-y-1">
                                <p className="text-sm font-medium leading-none">{activity.message}</p>
                                <p className="text-xs text-gray-500">{activity.time}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}
