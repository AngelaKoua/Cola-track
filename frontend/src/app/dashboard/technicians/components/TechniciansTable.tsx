/**
 * Technicians Table Component
 * 
 * Professional table displaying technicians with:
 * - Sorting by column
 * - Search by name
 * - Filter by status
 * - Actions (view, activate/deactivate, delete)
 */

"use client"

import { useState, useMemo } from "react"
import { Search, ChevronUp, ChevronDown, Eye, Power, Trash2, RefreshCw, Users } from "lucide-react"
import type { TechnicianListItem } from "../services/techniciansService"

interface TechniciansTableProps {
    technicians: TechnicianListItem[]
    loading: boolean
    onViewDetail: (id: number) => void
    onToggleStatus: (id: number, currentStatus: boolean) => void
    onDelete: (id: number) => void
    onRefresh?: () => void
}

type SortField = "username" | "total_entries" | "last_entry"
type SortOrder = "asc" | "desc"

export function TechniciansTable({
    technicians,
    loading,
    onViewDetail,
    onToggleStatus,
    onDelete,
    onRefresh
}: TechniciansTableProps) {
    const [search, setSearch] = useState("")
    const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all")
    const [sortField, setSortField] = useState<SortField>("username")
    const [sortOrder, setSortOrder] = useState<SortOrder>("asc")

    // Filtering and sorting
    const filteredAndSorted = useMemo(() => {
        let result = [...technicians]

        // Search filter
        if (search) {
            result = result.filter(t =>
                t.username.toLowerCase().includes(search.toLowerCase())
            )
        }

        // Status filter
        if (statusFilter === "active") {
            result = result.filter(t => t.is_active)
        } else if (statusFilter === "inactive") {
            result = result.filter(t => !t.is_active)
        }

        // Sorting
        result.sort((a, b) => {
            let aValue: any = a[sortField]
            let bValue: any = b[sortField]

            // Handle null values for last_entry
            if (sortField === "last_entry") {
                if (!aValue && !bValue) return 0
                if (!aValue) return sortOrder === "asc" ? 1 : -1
                if (!bValue) return sortOrder === "asc" ? -1 : 1
            }

            if (sortField === "username") {
                aValue = aValue.toLowerCase()
                bValue = bValue.toLowerCase()
            }

            if (aValue < bValue) return sortOrder === "asc" ? -1 : 1
            if (aValue > bValue) return sortOrder === "asc" ? 1 : -1
            return 0
        })

        return result
    }, [technicians, search, statusFilter, sortField, sortOrder])

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortOrder(sortOrder === "asc" ? "desc" : "asc")
        } else {
            setSortField(field)
            setSortOrder("asc")
        }
    }

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return "Aucune"
        const date = new Date(dateStr)
        return new Intl.DateTimeFormat("fr-FR", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        }).format(date)
    }

    const getEquipmentBadgeColor = (type: string) => {
        switch (type) {
            case "Osmoseur":
                return "bg-blue-100 text-blue-700 border-blue-200"
            case "Remplisseuse":
                return "bg-purple-100 text-purple-700 border-purple-200"
            case "Mixte":
                return "bg-emerald-100 text-emerald-700 border-emerald-200"
            default:
                return "bg-slate-100 text-slate-700 border-slate-200"
        }
    }

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-pulse">
                    <div className="h-8 bg-slate-200/60 rounded-full w-32"></div>
                    <div className="flex gap-3">
                        <div className="h-10 bg-slate-200/60 rounded-xl w-full sm:w-64"></div>
                        <div className="h-10 bg-slate-200/60 rounded-xl w-full sm:w-40"></div>
                    </div>
                </div>
                <div className="overflow-x-auto rounded-xl border border-slate-200/60 bg-white/50">
                    <div className="w-full">
                        <div className="border-b border-slate-200/60 bg-slate-50/50 p-4">
                            <div className="h-5 bg-slate-200/60 rounded max-w-2xl animate-pulse"></div>
                        </div>
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="flex items-center justify-between p-4 border-b border-slate-100">
                                <div className="flex items-center gap-4">
                                    <div className="h-10 w-10 rounded-full bg-slate-200/60 animate-pulse"></div>
                                    <div className="space-y-2.5">
                                        <div className="h-4 w-32 bg-slate-200/60 rounded animate-pulse"></div>
                                        <div className="h-3 w-20 bg-slate-200/60 rounded animate-pulse"></div>
                                    </div>
                                </div>
                                <div className="hidden sm:block h-6 w-24 bg-slate-200/60 rounded-full animate-pulse"></div>
                                <div className="flex gap-2">
                                    <div className="h-8 w-8 bg-slate-200/60 rounded-lg animate-pulse"></div>
                                    <div className="h-8 w-8 bg-slate-200/60 rounded-lg animate-pulse"></div>
                                    <div className="h-8 w-8 bg-slate-200/60 rounded-lg animate-pulse"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <span className="text-sm font-semibold text-slate-700 bg-slate-100 px-3 py-1 rounded-full">
                        {filteredAndSorted.length} {filteredAndSorted.length > 1 ? 'résultats' : 'résultat'}
                    </span>
                    {onRefresh && (
                        <button
                            onClick={onRefresh}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors shadow-sm"
                            title="Actualiser les données"
                        >
                            <RefreshCw className="h-4 w-4" />
                            <span className="hidden sm:inline">Rafraîchir</span>
                        </button>
                    )}
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                    {/* Search */}
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
                        <input
                            type="text"
                            placeholder="Rechercher..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-10 pr-4 py-2 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 w-full sm:w-64 bg-white/50 focus:bg-white transition-all"
                        />
                    </div>

                    {/* Status filter */}
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value as any)}
                        className="px-4 py-2 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white/50 focus:bg-white transition-all cursor-pointer"
                    >
                        <option value="all">Tous les statuts</option>
                        <option value="active">Actifs uniquement</option>
                        <option value="inactive">Inactifs uniquement</option>
                    </select>
                </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-200/60 bg-white/50">
                <table className="w-full text-left">
                    <thead>
                        <tr className="border-b border-slate-200/60 bg-slate-50/50">
                            <th
                                className="py-3.5 px-4 text-sm font-semibold text-slate-700 cursor-pointer hover:bg-slate-100/50 transition-colors"
                                onClick={() => handleSort("username")}
                            >
                                <div className="flex items-center gap-2">
                                    Nom
                                    {sortField === "username" && (
                                        sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                                    )}
                                </div>
                            </th>
                            <th className="py-3.5 px-4 text-sm font-semibold text-slate-700">
                                Statut
                            </th>
                            <th
                                className="py-3.5 px-4 text-sm font-semibold text-slate-700 cursor-pointer hover:bg-slate-100/50 transition-colors"
                                onClick={() => handleSort("total_entries")}
                            >
                                <div className="flex items-center gap-2">
                                    Saisies
                                    {sortField === "total_entries" && (
                                        sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                                    )}
                                </div>
                            </th>
                            <th
                                className="py-3.5 px-4 text-sm font-semibold text-slate-700 cursor-pointer hover:bg-slate-100/50 transition-colors"
                                onClick={() => handleSort("last_entry")}
                            >
                                <div className="flex items-center gap-2">
                                    Dernière saisie
                                    {sortField === "last_entry" && (
                                        sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                                    )}
                                </div>
                            </th>
                            <th className="py-3.5 px-4 text-sm font-semibold text-slate-700">
                                Type équipement
                            </th>
                            <th className="text-right py-3.5 px-4 text-sm font-semibold text-slate-700">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredAndSorted.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="text-center py-16">
                                    <div className="flex flex-col items-center justify-center space-y-3">
                                        <div className="p-4 bg-slate-50 rounded-full mb-2">
                                            <Users className="h-8 w-8 text-slate-400" />
                                        </div>
                                        <h3 className="text-lg font-semibold text-slate-900">Aucun technicien trouvé</h3>
                                        <p className="text-sm text-slate-500 max-w-sm">Modifiez les filtres ou ajoutez un nouveau technicien.</p>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            filteredAndSorted.map((tech) => (
                                <tr key={tech.id} className="border-b border-slate-100 hover:bg-slate-50/80 transition-colors duration-150 hover:shadow-sm group">
                                    <td className="py-3 px-4 text-sm font-medium text-slate-900">
                                        {tech.username}
                                    </td>
                                    <td className="py-3 px-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${tech.is_active
                                            ? "bg-emerald-50 text-emerald-700 border-emerald-200/50"
                                            : "bg-slate-100 text-slate-500 border-slate-200"
                                            }`}>
                                            {tech.is_active ? "Actif" : "Inactif"}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-sm text-slate-700 font-medium">
                                        {tech.total_entries.toLocaleString()}
                                    </td>
                                    <td className="py-3 px-4 text-sm text-slate-500">
                                        {formatDate(tech.last_entry)}
                                    </td>
                                    <td className="py-3 px-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getEquipmentBadgeColor(tech.equipment_type)}`}>
                                            {tech.equipment_type}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4">
                                        <div className="flex items-center justify-end gap-2 opacity-80 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={() => onViewDetail(tech.id)}
                                                className="p-1.5 text-slate-700 border border-slate-200 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                title="Voir le détail"
                                                disabled={loading}
                                            >
                                                <Eye className="h-4 w-4" />
                                            </button>
                                            <button
                                                onClick={() => onToggleStatus(tech.id, tech.is_active)}
                                                className={`p-1.5 border border-slate-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${tech.is_active
                                                    ? "text-amber-600 hover:bg-slate-100"
                                                    : "text-emerald-600 hover:bg-slate-100"
                                                    }`}
                                                title={tech.is_active ? "Désactiver" : "Activer"}
                                                disabled={loading}
                                            >
                                                <Power className="h-4 w-4" />
                                            </button>
                                            <button
                                                onClick={() => onDelete(tech.id)}
                                                className="p-1.5 text-rose-600 border border-slate-200 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                title="Supprimer"
                                                disabled={loading}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
