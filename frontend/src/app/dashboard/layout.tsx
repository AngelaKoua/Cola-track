"use client"

import DashboardLayout from "@/components/layout/DashboardLayout"
import { DataProvider } from "@/context/DataContext"
import { useAuth } from "@/context/AuthContext"
import { useRouter, usePathname } from "next/navigation"
import { useEffect } from "react"

export default function Layout({
    children,
}: {
    children: React.ReactNode
}) {
    const { user, isLoading } = useAuth()
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        if (!isLoading) {
            if (!user) {
                router.push("/")
                return
            }

            // Route Protection Rules
            if (user.role === 'technician') {
                // Technician can access Input and Incidents
                const allowedPaths = ['/dashboard/input', '/dashboard/incidents', '/dashboard/profile', '/dashboard/iot-monitoring']
                // Allow exact dashboard root to redirect
                if (pathname === '/dashboard') {
                    router.push('/dashboard/input')
                } else if (!allowedPaths.some(path => pathname.startsWith(path))) {
                    // If trying to access analytics etc.
                    router.push('/dashboard/input')
                }
            } else if (user.role === 'manager') {
                // Manager CANNOT access Input
                if (pathname.startsWith('/dashboard/input')) {
                    router.push('/dashboard')
                }
            }
        }
    }, [user, isLoading, pathname, router])

    if (isLoading) {
        return <div className="flex h-screen items-center justify-center">Chargement...</div>
    }

    if (!user) {
        return null // Will redirect
    }

    return (
        <DataProvider>
            <DashboardLayout>{children}</DashboardLayout>
        </DataProvider>
    )
}
