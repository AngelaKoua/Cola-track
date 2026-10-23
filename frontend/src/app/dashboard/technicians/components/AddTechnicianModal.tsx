/**
 * Add Technician Modal Component
 * 
 * Modal for creating a new technician with form validation.
 */

"use client"

import { useState } from "react"
import { X, UserPlus, Mail } from "lucide-react"

interface AddTechnicianModalProps {
    isOpen: boolean
    onClose: () => void
    onSubmit: (username: string, email: string) => Promise<void>
}

export function AddTechnicianModal({ isOpen, onClose, onSubmit }: AddTechnicianModalProps) {
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")

        // Validation
        if (username.length < 3) {
            setError("Le nom d'utilisateur doit contenir au moins 3 caractères")
            return
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(email)) {
            setError("Veuillez entrer une adresse email valide")
            return
        }

        setLoading(true)
        try {
            await onSubmit(username, email)
            setUsername("")
            setEmail("")
            onClose()
        } catch (err) {
            setError(err instanceof Error ? err.message : "Une erreur est survenue")
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-all">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-in fade-in zoom-in-95 duration-300 ease-out">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-emerald-100 rounded-lg">
                            <UserPlus className="h-5 w-5 text-emerald-600" />
                        </div>
                        <h2 className="text-xl font-bold text-slate-900">Ajouter un technicien</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-slate-600"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {error && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                            {error}
                        </div>
                    )}

                    <div>
                        <label htmlFor="username" className="block text-sm font-semibold text-slate-700 mb-2">
                            Nom d'utilisateur *
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-slate-900"
                            placeholder="ex: jdupont"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label htmlFor="email" className="block text-sm font-semibold text-slate-700 mb-2">
                            Email du technicien *
                        </label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-slate-900"
                                placeholder="technicien@example.com"
                                required
                                disabled={loading}
                            />
                        </div>
                        <p className="mt-1.5 text-xs text-slate-400">Les identifiants seront envoyés à cette adresse</p>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-end gap-3 pt-6 border-t border-slate-100 mt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                            disabled={loading}
                        >
                            Annuler
                        </button>
                        <button
                            type="submit"
                            className="px-5 py-2.5 text-sm font-semibold bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 active:bg-emerald-800 transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
                            disabled={loading}
                        >
                            {loading ? "Création..." : "Créer"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
