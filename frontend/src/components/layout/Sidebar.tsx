"use client"

import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
    LayoutDashboard,
    Activity,
    BarChart2,
    AlertTriangle,
    Zap,
    LogOut,
    Menu,
    ChevronRight,
    Users,
    ClipboardList,
    Cpu,
} from "lucide-react"
import { Button } from "@/components/ui/Button"
import { useState } from "react"
import { useAuth } from "@/context/AuthContext"

const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Gestion Techniciens", href: "/dashboard/technicians", icon: Users },
    { name: "Saisie Données", href: "/dashboard/input", icon: Activity },
    { name: "Incidents", href: "/dashboard/incidents", icon: ClipboardList },
    // { name: "Visualisation", href: "/dashboard/analytics", icon: BarChart2 },
    { name: "Prédictions", href: "/dashboard/predictions", icon: AlertTriangle },
    // { name: "Performance", href: "/dashboard/energy", icon: Zap },
    { name: "IoT Monitoring", href: "/dashboard/iot-monitoring", icon: Cpu },
]

export function Sidebar() {
    const pathname = usePathname()
    const [isOpen, setIsOpen] = useState(true)
    const [isCollapsed, setIsCollapsed] = useState(false)
    const { user, logout } = useAuth()

    const filteredNavItems = navItems.filter(item => {
        if (!user) return false

        if (user.role === 'technician') {
            return ['Saisie Données', 'Incidents', 'IoT Monitoring'].includes(item.name)
        }

        // Manager Access
        if (user.role === 'manager') {
            // Managers have access to everything except data entry
            return item.name !== 'Saisie Données'
        }

        return false
    })

    return (
        <>
            {/* Mobile Menu Button */}
            <div className="lg:hidden fixed top-4 left-4 z-50">
                <Button variant="outline" size="icon" onClick={() => setIsOpen(!isOpen)} className="bg-white shadow-md">
                    <Menu className="h-6 w-6 text-gray-700" />
                </Button>
            </div>

            {/* Sidebar Container */}
            <aside
                className={cn(
                    "fixed inset-y-0 left-0 z-40 bg-gradient-to-b from-slate-900 to-slate-800 text-white shadow-2xl transform transition-all duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-auto lg:flex lg:flex-col",
                    isOpen ? "translate-x-0" : "-translate-x-full",
                    isCollapsed ? "w-20" : "w-72"
                )}
            >
                {/* Logo Area */}
                <div className={cn(
                    "flex items-center h-20 px-6 border-b border-slate-700/50 transition-all duration-300",
                    isCollapsed ? "justify-center px-0" : "justify-start"
                )}>
                    <Link href="/dashboard" className="flex items-center hover:opacity-90 transition-opacity">
                        <Image
                            src="/logo_ctrack.png"
                            alt="Ctrack Logo"
                            width={180}
                            height={52}
                            className={cn(
                                "object-contain transition-all duration-300",
                                isCollapsed ? "w-18 h-18" : "w-auto h-38"
                            )}
                            priority
                        />
                    </Link>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto py-6 px-4">
                    {!isCollapsed && (
                        <div className="mb-2 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">
                            Menu Principal
                        </div>
                    )}
                    <ul className="space-y-2">
                        {filteredNavItems.map((item) => {
                            const isActive = pathname === item.href
                            return (
                                <li key={item.href}>
                                    <Link
                                        href={item.href}
                                        title={isCollapsed ? item.name : undefined}
                                        className={cn(
                                            "relative flex items-center py-3 text-sm font-medium rounded-xl transition-all duration-200 group overflow-hidden",
                                            isActive
                                                ? "bg-primary text-white shadow-lg shadow-primary/25"
                                                : "text-slate-300 hover:bg-slate-800 hover:text-white",
                                            isCollapsed ? "justify-center px-2" : "px-4"
                                        )}
                                    >
                                        <item.icon
                                            className={cn(
                                                "h-5 w-5 transition-transform duration-200 group-hover:scale-110",
                                                isActive ? "text-white" : "text-slate-400 group-hover:text-white",
                                                !isCollapsed && "mr-3"
                                            )}
                                        />
                                        {!isCollapsed && (
                                            <>
                                                <span className="relative z-10 whitespace-nowrap">{item.name}</span>
                                                {isActive && (
                                                    <ChevronRight className="ml-auto h-4 w-4 text-white/50" />
                                                )}
                                            </>
                                        )}
                                    </Link>
                                </li>
                            )
                        })}
                    </ul>

                    {/* Toggle Button (Desktop Only) */}
                    <div className="hidden lg:flex justify-center mt-8">
                        <button
                            onClick={() => setIsCollapsed(!isCollapsed)}
                            className="h-10 w-10 rounded-full bg-slate-700/50 hover:bg-primary hover:text-white text-slate-400 flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50"
                            id="sidebarToggle"
                        >
                            <ChevronRight className={cn("h-5 w-5 transition-transform duration-300", isCollapsed ? "rotate-0" : "rotate-180")} />
                        </button>
                    </div>
                </nav>

                {/* Footer / Logout */}
                <div className="p-4 border-t border-slate-700/50 bg-slate-900/50">
                    <Button
                        variant="ghost"
                        className={cn(
                            "w-full text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors",
                            isCollapsed ? "justify-center px-0" : "justify-start"
                        )}
                        onClick={logout}
                        title={isCollapsed ? "Déconnexion" : undefined}
                    >
                        <LogOut className={cn("h-4 w-4", !isCollapsed && "mr-2")} />
                        {!isCollapsed && "Déconnexion"}
                    </Button>
                    {!isCollapsed && (
                        <div className="mt-4 text-center text-[10px] text-slate-500 whitespace-nowrap">
                            Version 2.4.0 • © 2025 Ctrack
                        </div>
                    )}
                </div>
            </aside>

            {/* Overlay for mobile */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 lg:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </>
    )
}
