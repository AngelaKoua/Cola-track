import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"

interface KPICardProps {
    title: string
    value: string | number
    unit?: string
    description?: string
    trend?: string | "up" | "down" | "stable" | "neutral"
    // Analytics dashboard props
    previous?: number
    target?: number
    change?: number
    status?: "success" | "warning" | "danger" | "neutral"
    /** Index for stagger animation (0-based) */
    index?: number
    /** Optional icon for the card */
    icon?: React.ReactNode
}

export function KPICard({
    title,
    value,
    unit,
    description,
    trend,
    previous,
    target,
    change,
    status,
    index = 0,
    icon
}: KPICardProps) {
    // Badge colors for trends
    const trendBadgeColors = {
        positive: "bg-emerald-100 text-emerald-700 border-emerald-200",
        negative: "bg-rose-100 text-rose-700 border-rose-200",
        neutral: "bg-slate-100 text-slate-600 border-slate-200"
    }

    const getTrendColor = () => {
        if (change !== undefined) {
            return change > 0 ? "positive" : change < 0 ? "negative" : "neutral"
        }
        if (trend === "up") return "positive"
        if (trend === "down") return "negative"
        return "neutral"
    }

    // Status-based subtle color accents
    const statusColors = {
        success: {
            gradient: "from-emerald-50/40 via-white to-white",
            glow: "hover:shadow-emerald-100/40",
            shimmer: "from-transparent via-emerald-100/20 to-transparent",
            dot: "bg-emerald-600",
            progressBar: "bg-emerald-500"
        },
        warning: {
            gradient: "from-amber-50/40 via-white to-white",
            glow: "hover:shadow-amber-100/40",
            shimmer: "from-transparent via-amber-100/20 to-transparent",
            dot: "bg-amber-500",
            progressBar: "bg-amber-500"
        },
        danger: {
            gradient: "from-rose-50/40 via-white to-white",
            glow: "hover:shadow-rose-100/40",
            shimmer: "from-transparent via-rose-100/20 to-transparent",
            dot: "bg-rose-600",
            progressBar: "bg-rose-500"
        },
        neutral: {
            gradient: "from-slate-50/40 via-white to-white",
            glow: "hover:shadow-slate-100/40",
            shimmer: "from-transparent via-slate-100/20 to-transparent",
            dot: "bg-slate-400",
            progressBar: "bg-slate-400"
        }
    }

    const currentStatus = status || "neutral"
    const colorScheme = statusColors[currentStatus]

    // Compute progress ratio for target bar
    const numericValue = typeof value === 'string' ? parseFloat(value.replace(/[^\d.,-]/g, '').replace(',', '.')) : value
    const progressPercent = (target !== undefined && !isNaN(numericValue))
        ? Math.min(Math.max((numericValue / target) * 100, 0), 100)
        : null

    return (
        <Card className={cn(
            "group relative overflow-hidden min-h-[200px]",
            "bg-white/80 backdrop-blur-md",
            "border border-slate-200/70",
            "transition-all duration-500 ease-out",
            "hover:shadow-lg hover:-translate-y-0.5",
            colorScheme.glow,
            "animate-fade-in-up",
            `stagger-${Math.min(index + 1, 5)}`
        )}>
            {/* Gradient background overlay */}
            <div className={cn(
                "absolute inset-0 bg-gradient-to-br opacity-60",
                colorScheme.gradient
            )} />

            {/* Animated shimmer effect on hover */}
            <div className={cn(
                "absolute inset-0 -translate-x-full group-hover:translate-x-full",
                "transition-transform duration-1000 ease-in-out",
                "bg-gradient-to-r",
                colorScheme.shimmer
            )} />

            <CardHeader className="relative pb-2">
                <CardTitle className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className={cn(
                            "w-1.5 h-1.5 rounded-full flex-shrink-0",
                            colorScheme.dot,
                            (status === "success" || status === "warning" || status === "danger") && "animate-pulse"
                        )} />
                        {title}
                    </div>
                    {icon && <div className="text-slate-400">{icon}</div>}
                </CardTitle>
            </CardHeader>

            <CardContent className="relative">
                {/* Main value */}
                <div className="flex items-baseline gap-2 mb-2">
                    <span className={cn(
                        "text-3xl font-black tracking-tight",
                        "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-600 bg-clip-text text-transparent",
                        "transition-all duration-300"
                    )}>
                        {value}
                    </span>
                    {unit && (
                        <span className="text-sm font-semibold text-slate-400">
                            {unit}
                        </span>
                    )}
                </div>

                {/* Target progress micro-bar */}
                {progressPercent !== null && target !== undefined && (
                    <div className="mb-3">
                        <div className="progress-micro-bar">
                            <div
                                className={cn("progress-fill", colorScheme.progressBar)}
                                style={{ width: `${progressPercent}%` }}
                            />
                        </div>
                        <div className="flex justify-between mt-0.5">
                            <span className="text-[10px] text-slate-400">{Math.round(progressPercent)}%</span>
                            <span className="text-[10px] text-slate-400">cible: {target}{unit}</span>
                        </div>
                    </div>
                )}

                {/* Trend indicators */}
                {(trend || change !== undefined) && (
                    <div className="flex items-center gap-2 mb-3">
                        <div className={cn(
                            "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold",
                            "border shadow-sm",
                            "transition-all duration-300",
                            trendBadgeColors[getTrendColor()]
                        )}>
                            {trend === "up" && <TrendingUp className="h-3.5 w-3.5" />}
                            {trend === "down" && <TrendingDown className="h-3.5 w-3.5" />}
                            {(trend === "stable" || trend === "neutral") && <Minus className="h-3.5 w-3.5" />}

                            {change !== undefined && (
                                <span>
                                    {change > 0 ? "+" : ""}{change}%
                                </span>
                            )}

                            {typeof trend === 'string' && !["up", "down", "stable", "neutral"].includes(trend) && (
                                <span>{trend}</span>
                            )}
                        </div>
                    </div>
                )}

                {/* Objective & Previous values */}
                {(target !== undefined || previous !== undefined) && (
                    <div className="space-y-1.5 pt-3 border-t border-slate-200/50">
                        <div className="flex items-center gap-4">
                            {target !== undefined && (
                                <div className="flex items-center gap-1.5 text-[11px]">
                                    <div className="w-1 h-1 rounded-full bg-blue-500" />
                                    <span className="text-slate-500 font-medium">Objectif</span>
                                    <span className="text-slate-800 font-bold">{target}{unit}</span>
                                </div>
                            )}
                            {previous !== undefined && (
                                <div className="flex items-center gap-1.5 text-[11px]">
                                    <div className="w-1 h-1 rounded-full bg-violet-500" />
                                    <span className="text-slate-500 font-medium">Préc.</span>
                                    <span className="text-slate-800 font-bold">{previous}{unit}</span>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {description && (
                    <p className="text-xs text-slate-500 mt-3 leading-relaxed font-medium">{description}</p>
                )}
            </CardContent>
        </Card>
    )
}
