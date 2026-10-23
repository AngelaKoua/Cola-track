"use client"

import React, { createContext, useContext, useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { authApi } from "@/lib/api"

interface User {
    username: string
    role: "technician" | "manager"
    userId: number
}

interface AuthContextType {
    user: User | null
    login: (username: string, role: string, token: string, userId: number) => void
    logout: () => void
    isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        // Initialize from local storage
        const token = localStorage.getItem("token")
        const role = localStorage.getItem("role") as "technician" | "manager"
        const username = localStorage.getItem("username")
        const storedUserId = localStorage.getItem("user_id")

        if (token && role && username && storedUserId) {
            setUser({ username, role, userId: parseInt(storedUserId) })
        }
        setIsLoading(false)
    }, [])

    const login = (username: string, role: string, token: string, userId: number) => {
        localStorage.setItem("token", token)
        localStorage.setItem("role", role)
        localStorage.setItem("username", username)
        localStorage.setItem("user_id", String(userId))
        setUser({ username, role: role as "technician" | "manager", userId })
        router.push("/dashboard")
    }

    const logout = () => {
        localStorage.removeItem("token")
        localStorage.removeItem("role")
        localStorage.removeItem("username")
        localStorage.removeItem("user_id")
        setUser(null)
        router.push("/")
    }

    return (
        <AuthContext.Provider value={{ user, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider")
    }
    return context
}
