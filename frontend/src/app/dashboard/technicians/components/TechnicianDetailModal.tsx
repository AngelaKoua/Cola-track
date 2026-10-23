/**
 * Technician Detail Modal Component
 * 
 * Modal displaying detailed analytics for a specific technician:
 * - General information
 * - Activity charts (by day, by equipment, by hour)
 */

"use client"

import { useState, useEffect } from "react"
import { X, User, Calendar, Activity } from "lucide-react"
import { LineChart, Line, PieChart, Pie, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "@/lib/dynamicCharts"
import { TechniciansService, type TechnicianDetail } from "../services/techniciansService"

interface TechnicianDetailModalProps {
    isOpen: boolean
    technicianId: number | null
    periodDays: number
    onClose: () => void
}

export function TechnicianDetailModal({
    isOpen,
    technicianId,
    periodDays,
    onClose
}: TechnicianDetailModalProps) {
    const [detail, setDetail] = useState<TechnicianDetail | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (isOpen && technicianId) {
            fetchDetail()
        }
    }, [isOpen, technicianId, periodDays])

    const fetchDetail = async () => {
        if (!technicianId) return

        setLoading(true)
        setError(null)

        try {
            const data = await TechniciansService.getTechnicianDetail(technicianId, periodDays)
            setDetail(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : "Erreur de chargement")
        } finally {
            setLoading(false)
        }
    }

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return "N/A"
        const date = new Date(dateStr)
        return new Intl.DateTimeFormat("fr-FR", {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }).format(date)
    }

    // Prepare chart data
    const equipmentData = detail ? [
        { name: "Osmoseur", value: detail.entries_by_equipment.Osmoseur, color: "#3b82f6" },
        { name: "Remplisseuse", value: detail.entries_by_equipment.Remplisseuse, color: "#a855f7" }
    ].filter(item => item.value > 0) : []

    const hourData = detail ? detail.entries_by_hour.map((count, hour) => ({
        hour: `${hour}h`,
        saisies: count
    })) : []

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-all overflow-y-auto">
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full my-8 animate-in fade-in zoom-in-95 duration-300 ease-out">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-emerald-100/50 border border-emerald-100 rounded-xl">
                            <User className="h-5 w-5 text-emerald-600" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-slate-900">Détails du technicien</h2>
                            {detail && (
                                <p className="text-sm font-medium text-slate-500">{detail.username}</p>
                            )}
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-slate-600"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto custom-scrollbar">
                    {loading && (
                        <div className="flex items-center justify-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-200 border-t-emerald-600"></div>
                        </div>
                    )}

                    {error && (
                        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-sm font-medium">
                            {error}
                        </div>
                    )}

                    {detail && !loading && (
                        <>
                            {/* General Information */}
                            <div className="bg-slate-50/50 rounded-xl p-5 space-y-4 border border-slate-100">
                                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                                    <Calendar className="h-4 w-4 text-slate-500" />
                                    Informations générales
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-sm">
                                    <div>
                                        <span className="text-slate-500">Statut :</span>
                                        <span className={`ml-2 font-medium ${detail.is_active ? "text-emerald-600" : "text-slate-500"}`}>
                                            {detail.is_active ? "Actif" : "Inactif"}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-slate-500">Date de création :</span>
                                        <span className="ml-2 font-semibold text-slate-900">
                                            {formatDate(detail.created_at)}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-slate-500">Dernière activité :</span>
                                        <span className="ml-2 font-semibold text-slate-900">
                                            {formatDate(detail.last_activity)}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-slate-500">Total saisies :</span>
                                        <span className="ml-2 font-semibold text-slate-900">
                                            {(detail.entries_by_equipment.Osmoseur + detail.entries_by_equipment.Remplisseuse).toLocaleString()}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Charts Section */}
                            <div className="space-y-6 pt-2">
                                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                                    <Activity className="h-4 w-4 text-emerald-600" />
                                    Activité de saisie
                                </h3>

                                {/* Entries by Day */}
                                {detail.entries_by_day.length > 0 ? (
                                    <div className="bg-white border border-slate-200 rounded-xl p-5">
                                        <h4 className="text-sm font-semibold text-slate-700 mb-6">Nombre de relevés par jour</h4>
                                        <ResponsiveContainer width="100%" height={250}>
                                            <LineChart data={detail.entries_by_day}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                                                <YAxis tick={{ fontSize: 12 }} />
                                                <Tooltip />
                                                <Line type="monotone" dataKey="count" stroke="#059669" strokeWidth={2} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                ) : (
                                    <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-8 text-center text-slate-500 text-sm font-medium">
                                        Aucune donnée disponible pour la période sélectionnée
                                    </div>
                                )}

                                {/* Equipment Distribution & Hour Distribution */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    {/* Equipment Distribution */}
                                    {equipmentData.length > 0 && (
                                        <div className="bg-white border border-slate-200 rounded-xl p-5">
                                            <h4 className="text-sm font-semibold text-slate-700 mb-6">Répartition par type d'équipement</h4>
                                            <ResponsiveContainer width="100%" height={200}>
                                                <PieChart>
                                                    <Pie
                                                        data={equipmentData}
                                                        cx="50%"
                                                        cy="50%"
                                                        labelLine={false}
                                                        label={(entry) => `${entry.name}: ${entry.value}`}
                                                        outerRadius={80}
                                                        fill="#8884d8"
                                                        dataKey="value"
                                                    >
                                                        {equipmentData.map((entry, index) => (
                                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                                        ))}
                                                    </Pie>
                                                    <Tooltip />
                                                </PieChart>
                                            </ResponsiveContainer>
                                        </div>
                                    )}

                                    {/* Hour Distribution */}
                                    {hourData.some(h => h.saisies > 0) && (
                                        <div className="bg-white border border-slate-200 rounded-xl p-5">
                                            <h4 className="text-sm font-semibold text-slate-700 mb-6">Heures typiques de saisie</h4>
                                            <ResponsiveContainer width="100%" height={200}>
                                                <BarChart data={hourData}>
                                                    <CartesianGrid strokeDasharray="3 3" />
                                                    <XAxis dataKey="hour" tick={{ fontSize: 10 }} interval={2} />
                                                    <YAxis tick={{ fontSize: 12 }} />
                                                    <Tooltip />
                                                    <Bar dataKey="saisies" fill="#059669" />
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end p-6 border-t border-slate-100 bg-slate-50/50 rounded-b-2xl">
                    <button
                        onClick={onClose}
                        className="px-5 py-2.5 text-sm font-semibold bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 transition-colors shadow-sm hover:shadow-md hover:-translate-y-0.5"
                    >
                        Fermer
                    </button>
                </div>
            </div>
        </div>
    )
}
