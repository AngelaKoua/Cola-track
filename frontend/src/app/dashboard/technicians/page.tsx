/**
 * Technicians Management Page
 * 
 * Page for managing technicians with:
 * - Summary KPI cards
 * - Technicians table with actions
 * - Modals for add, detail, and delete
 */

"use client"

import { useState } from "react"
import { UserPlus, AlertCircle } from "lucide-react"
import { TechniciansKPICards } from "./components/TechniciansKPICards"
import { TechniciansTable } from "./components/TechniciansTable"
import { AddTechnicianModal } from "./components/AddTechnicianModal"
import { TechnicianDetailModal } from "./components/TechnicianDetailModal"
import { DeleteConfirmDialog } from "./components/DeleteConfirmDialog"
import { useTechnicians } from "./hooks/useTechnicians"

export default function TechniciansPage() {
    const [periodDays] = useState(30)
    const {
        stats,
        technicians,
        loading,
        error,
        fetchData,
        createTechnician,
        toggleStatus,
        deleteTechnician
    } = useTechnicians(periodDays)

    // Modal states
    const [showAddModal, setShowAddModal] = useState(false)
    const [showDetailModal, setShowDetailModal] = useState(false)
    const [selectedTechnicianId, setSelectedTechnicianId] = useState<number | null>(null)
    const [showDeleteDialog, setShowDeleteDialog] = useState(false)
    const [technicianToDelete, setTechnicianToDelete] = useState<{ id: number; name: string } | null>(null)
    const [actionLoading, setActionLoading] = useState(false)

    // Handlers
    const handleAddTechnician = async (username: string, email: string) => {
        await createTechnician({ username, email })
    }

    const handleViewDetail = (id: number) => {
        setSelectedTechnicianId(id)
        setShowDetailModal(true)
    }

    const handleToggleStatus = async (id: number, currentStatus: boolean) => {
        setActionLoading(true)
        try {
            await toggleStatus(id, !currentStatus)
        } catch (err) {
            console.error("Error toggling status:", err)
            alert(err instanceof Error ? err.message : "Erreur lors du changement de statut")
        } finally {
            setActionLoading(false)
        }
    }

    const handleDeleteClick = (id: number) => {
        const tech = technicians.find(t => t.id === id)
        if (tech) {
            setTechnicianToDelete({ id, name: tech.username })
            setShowDeleteDialog(true)
        }
    }

    const handleDeleteConfirm = async () => {
        if (!technicianToDelete) return

        setActionLoading(true)
        try {
            await deleteTechnician(technicianToDelete.id)
            setShowDeleteDialog(false)
            setTechnicianToDelete(null)
        } catch (err) {
            console.error("Error deleting technician:", err)
            alert(err instanceof Error ? err.message : "Erreur lors de la suppression")
        } finally {
            setActionLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-50 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="max-w-[1600px] mx-auto p-4 sm:p-6 lg:p-8 space-y-8 sm:space-y-10">
                {/* Header */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 lg:gap-6 border-b border-slate-200 pb-6 mb-2">
                    <div className="space-y-2">
                        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-slate-900">
                            Gestion des techniciens
                        </h1>
                        <p className="text-sm sm:text-base text-slate-500 font-medium">
                        </p>
                    </div>

                    <button
                        onClick={() => setShowAddModal(true)}
                        disabled={actionLoading}
                        className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 active:bg-emerald-800 transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                    >
                        <UserPlus className="h-4 w-4" />
                        <span>Ajouter un technicien</span>
                    </button>
                </div>

                {/* Error Banner */}
                {error && (
                    <div className="bg-rose-50 border-l-4 border-rose-500 rounded-r-xl p-4 sm:p-5 text-rose-900 shadow-sm flex items-start sm:items-center justify-between gap-4 animate-in fade-in slide-in-from-top-2">
                        <div className="flex items-start sm:items-center gap-3">
                            <AlertCircle className="h-5 w-5 text-rose-600 mt-0.5 sm:mt-0 flex-shrink-0" />
                            <div>
                                <p className="font-semibold text-sm sm:text-base">Erreur de chargement</p>
                                <p className="text-xs sm:text-sm mt-1">{error.message}</p>
                            </div>
                        </div>
                        <button
                            onClick={() => fetchData()}
                            className="px-3 py-1.5 bg-white text-rose-700 text-sm font-medium rounded-lg border border-rose-200 hover:bg-rose-50 transition-colors shadow-sm whitespace-nowrap"
                        >
                            Réessayer
                        </button>
                    </div>
                )}

                {/* KPI Cards */}
                <section className="bg-white/80 backdrop-blur-md rounded-2xl border border-slate-200/70 shadow-lg p-6 lg:p-8 space-y-6">
                    <div className="mb-2 pb-4 border-b border-slate-100">
                        <h2 className="text-lg font-bold text-slate-800">Indicateurs de Synthèse</h2>
                        <p className="text-sm text-slate-500 mt-1">Vue consolidée des comptes de saisie</p>
                    </div>
                    <TechniciansKPICards stats={stats} loading={loading} />
                </section>

                {/* Technicians Table */}
                <section className="bg-white/80 backdrop-blur-md rounded-2xl border border-slate-200/70 shadow-lg p-6 lg:p-8 space-y-6">
                    <div className="mb-2 pb-4 border-b border-slate-100">
                        <h2 className="text-lg font-bold text-slate-800">Liste des Techniciens</h2>
                        <p className="text-sm text-slate-500 mt-1">Administration et supervision des utilisateurs</p>
                    </div>
                    <TechniciansTable
                        technicians={technicians}
                        loading={loading}
                        onViewDetail={handleViewDetail}
                        onToggleStatus={handleToggleStatus}
                        onDelete={handleDeleteClick}
                        onRefresh={fetchData}
                    />
                </section>
            </div>

            {/* Modals */}
            <AddTechnicianModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                onSubmit={handleAddTechnician}
            />

            <TechnicianDetailModal
                isOpen={showDetailModal}
                technicianId={selectedTechnicianId}
                periodDays={periodDays}
                onClose={() => {
                    setShowDetailModal(false)
                    setSelectedTechnicianId(null)
                }}
            />

            <DeleteConfirmDialog
                isOpen={showDeleteDialog}
                technicianName={technicianToDelete?.name || ""}
                onClose={() => {
                    setShowDeleteDialog(false)
                    setTechnicianToDelete(null)
                }}
                onConfirm={handleDeleteConfirm}
                loading={actionLoading}
            />
        </div>
    )
}
