/**
 * Delete Confirmation Dialog Component
 * 
 * Modal for confirming technician deletion with warning message.
 */

"use client"

import { AlertTriangle, X } from "lucide-react"

interface DeleteConfirmDialogProps {
    isOpen: boolean
    technicianName: string
    onClose: () => void
    onConfirm: () => void
    loading?: boolean
}

export function DeleteConfirmDialog({
    isOpen,
    technicianName,
    onClose,
    onConfirm,
    loading = false
}: DeleteConfirmDialogProps) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-all">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-in fade-in zoom-in-95 duration-300 ease-out">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-red-100 rounded-lg">
                            <AlertTriangle className="h-5 w-5 text-red-600" />
                        </div>
                        <h2 className="text-xl font-bold text-slate-900">Confirmation de suppression</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-slate-600"
                        disabled={loading}
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-5">
                    <p className="text-slate-700 text-sm md:text-base leading-relaxed">
                        Êtes-vous sûr de vouloir supprimer le technicien <strong className="font-bold text-slate-900">{technicianName}</strong> ?
                    </p>

                    <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                        <p className="text-sm text-amber-800">
                            <strong>Note :</strong> Cette action marquera le compte comme inactif.
                            Les données historiques de saisie resteront visibles dans le système.
                        </p>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-100 bg-slate-50/50 rounded-b-2xl">
                    <button
                        onClick={onClose}
                        className="px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                        disabled={loading}
                    >
                        Annuler
                    </button>
                    <button
                        onClick={onConfirm}
                        className="px-5 py-2.5 text-sm font-semibold bg-rose-600 text-white rounded-xl hover:bg-rose-700 active:bg-rose-800 transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
                        disabled={loading}
                    >
                        {loading ? "Suppression..." : "Supprimer"}
                    </button>
                </div>
            </div>
        </div>
    )
}
