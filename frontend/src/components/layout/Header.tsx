"use client"
import { Search, User, ChevronDown, LogOut } from "lucide-react"
import { Input } from "@/components/ui/Input"
import { useAuth } from "@/context/AuthContext"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { NotificationBell } from "@/components/notifications/NotificationBell"

export function Header() {
    const { user, logout } = useAuth()
    const router = useRouter()
    const [isProfileOpen, setIsProfileOpen] = useState(false)

    // Helper to get initials
    const getInitials = (name: string) => {
        return name
            .split(' ')
            .map(part => part[0])
            .join('')
            .toUpperCase()
            .slice(0, 2)
    }

    // Helper to format role
    const formatRole = (role: string) => {
        const roles: Record<string, string> = {
            'technician': 'Technicien Sur Site',
            'manager': 'Manager Production'
        }
        return roles[role] || role
    }

    return (
        <header className="h-16 bg-white/80 backdrop-blur-md border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-30 transition-all duration-300">
            {/* Search Bar */}
            <div className="hidden md:flex items-center max-w-md w-full">
                <div className="relative w-full group">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400 group-focus-within:text-primary transition-colors" />
                    <Input
                        type="search"
                        placeholder="Rechercher une machine, une alerte..."
                        className="pl-9 bg-gray-50/50 border-gray-200 focus-visible:ring-1 focus-visible:ring-primary/20 focus-visible:border-primary/50 transition-all"
                    />
                </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-2 sm:space-x-4">
                <NotificationBell />

                <div className="relative">
                    <button
                        onClick={() => setIsProfileOpen(!isProfileOpen)}
                        className="flex items-center space-x-3 pl-2 sm:pl-4 border-l border-gray-200 hover:bg-gray-50/50 rounded-lg p-1 transition-colors outline-none"
                    >
                        <div className="text-right hidden sm:block">
                            <p className="text-sm font-semibold text-foreground capitalize">
                                {user?.username || 'Invité'}
                            </p>
                            <p className="text-xs text-gray-500 font-medium">
                                {user?.role ? formatRole(user.role) : 'Mode Démo'}
                            </p>
                        </div>
                        <div className="h-9 w-9 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-white font-bold shadow-md shadow-primary/20 ring-2 ring-white">
                            {user?.username ? getInitials(user.username) : <User className="h-4 w-4" />}
                        </div>
                        <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${isProfileOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Dropdown Menu */}
                    <AnimatePresence>
                        {isProfileOpen && (
                            <motion.div
                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                transition={{ duration: 0.2 }}
                                className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50 origin-top-right"
                            >
                                <div className="px-4 py-2 border-b border-gray-50 sm:hidden">
                                    <p className="text-sm font-semibold text-foreground capitalize">
                                        {user?.username || 'Invité'}
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        {user?.role ? formatRole(user.role) : 'Mode Démo'}
                                    </p>
                                </div>
                                <div className="p-1">
                                    <button
                                        onClick={() => { router.push('/dashboard/profile'); setIsProfileOpen(false) }}
                                        className="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
                                    >
                                        <User className="h-4 w-4 mr-2" />
                                        Mon Profil
                                    </button>
                                    <div className="h-px bg-gray-100 my-1" />
                                    <button
                                        onClick={logout}
                                        className="w-full flex items-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    >
                                        <LogOut className="h-4 w-4 mr-2" />
                                        Déconnexion
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </header>
    )
}
