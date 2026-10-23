"use client"

import { AlertCircle, AlertTriangle, Info, X } from "lucide-react"
import { useState } from "react"
import type { Alert } from "../services/dashboardService"

interface AlertBannerProps {
    alerts: Alert[]
}

export function AlertBanner({ alerts }: AlertBannerProps) {
    const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set())

    if (!alerts || alerts.length === 0) {
        return null
    }

    const visibleAlerts = alerts.filter(alert => !dismissedAlerts.has(alert.id))

    if (visibleAlerts.length === 0) {
        return null
    }

    const handleDismiss = (alertId: string) => {
        setDismissedAlerts(prev => new Set([...prev, alertId]))
    }

    const getSeverityStyles = (severity: Alert["severity"]) => {
        switch (severity) {
            case "critical":
                return {
                    bg: "bg-rose-50 border-rose-200",
                    text: "text-rose-900",
                    icon: "text-rose-600",
                    Icon: AlertCircle
                }
            case "warning":
                return {
                    bg: "bg-amber-50 border-amber-200",
                    text: "text-amber-900",
                    icon: "text-amber-600",
                    Icon: AlertTriangle
                }
            default:
                return {
                    bg: "bg-blue-50 border-blue-200",
                    text: "text-blue-900",
                    icon: "text-blue-600",
                    Icon: Info
                }
        }
    }

    return (
        <div className="space-y-2 mb-6">
            {visibleAlerts.map((alert) => {
                const styles = getSeverityStyles(alert.severity)
                const IconComponent = styles.Icon

                return (
                    <div
                        key={alert.id}
                        className={`${styles.bg} border rounded-lg p-4 flex items-start justify-between`}
                    >
                        <div className="flex items-start gap-3 flex-1">
                            <IconComponent className={`h-5 w-5 ${styles.icon} mt-0.5`} />
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-sm font-semibold ${styles.text}`}>
                                        {alert.equipment}
                                    </span>
                                    <span className={`text-xs ${styles.text} opacity-60`}>
                                        ID: {alert.id}
                                    </span>
                                </div>
                                <p className={`text-sm ${styles.text}`}>
                                    {alert.message}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={() => handleDismiss(alert.id)}
                            className={`${styles.icon} hover:opacity-70 transition-opacity`}
                            aria-label="Dismiss alert"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                )
            })}
        </div>
    )
}
