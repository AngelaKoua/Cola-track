import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
    "inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
    {
        variants: {
            status: {
                ok: "bg-[#2ECC71]/10 text-[#2ECC71] border border-[#2ECC71]/20",
                warning: "bg-[#F39C12]/10 text-[#F39C12] border border-[#F39C12]/20",
                critical: "bg-[#E74C3C]/10 text-[#E74C3C] border border-[#E74C3C]/20",
            },
        },
        defaultVariants: {
            status: "ok",
        },
    }
)

export interface SystemHealthBadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
    status: "ok" | "warning" | "critical"
}

export function SystemHealthBadge({ className, status, ...props }: SystemHealthBadgeProps) {
    const labels = {
        ok: "Système Global : OK",
        warning: "Système Global : Attention",
        critical: "Système Global : Critique",
    }

    return (
        <div className={cn(badgeVariants({ status }), className)} {...props}>
            <span className={cn("mr-2 h-2 w-2 rounded-full",
                status === "ok" && "bg-[#2ECC71]",
                status === "warning" && "bg-[#F39C12]",
                status === "critical" && "bg-[#E74C3C]"
            )} />
            {labels[status]}
        </div>
    )
}
