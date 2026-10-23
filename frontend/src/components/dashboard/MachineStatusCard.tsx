import { Card, CardContent } from "@/components/ui/Card"
import { LucideIcon, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface MachineStatusCardProps {
    name: string
    status: "ok" | "warning" | "critical"
    lastUpdate: string
    alertCount: number
    icon: LucideIcon
}

export function MachineStatusCard({
    name,
    status,
    lastUpdate,
    alertCount,
    icon: Icon
}: MachineStatusCardProps) {
    const statusColors = {
        ok: "border-l-4 border-l-[#2ECC71]",
        warning: "border-l-4 border-l-[#F39C12]",
        critical: "border-l-4 border-l-[#E74C3C]"
    }

    const iconColors = {
        ok: "text-[#2ECC71] bg-[#2ECC71]/10",
        warning: "text-[#F39C12] bg-[#F39C12]/10",
        critical: "text-[#E74C3C] bg-[#E74C3C]/10"
    }

    return (
        <Card className={cn("overflow-hidden hover:shadow-md transition-shadow", statusColors[status])}>
            <CardContent className="p-6">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                        <div className={cn("p-3 rounded-xl", iconColors[status])}>
                            <Icon className="h-6 w-6" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900">{name}</h3>
                            <p className="text-sm text-gray-500">Mis à jour : {lastUpdate}</p>
                        </div>
                    </div>
                </div>

                <div className="mt-4 flex items-center justify-between">
                    <span className={cn(
                        "text-sm font-medium px-2 py-1 rounded-md",
                        status === "ok" ? "text-[#2ECC71] bg-[#2ECC71]/10" :
                            status === "warning" ? "text-[#F39C12] bg-[#F39C12]/10" :
                                "text-[#E74C3C] bg-[#E74C3C]/10"
                    )}>
                        {status === "ok" ? "Opérationnel" : status === "warning" ? "Surveillance" : "Arrêt Critique"}
                    </span>

                    {alertCount > 0 && (
                        <div className="flex items-center text-[#E74C3C] text-sm font-medium">
                            <AlertCircle className="h-4 w-4 mr-1" />
                            {alertCount} alerte{alertCount > 1 ? 's' : ''}
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
