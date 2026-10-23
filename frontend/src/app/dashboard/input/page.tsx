"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { OsmoseurForm } from "@/components/forms/OsmoseurForm"
import { RemplisseuseForm } from "@/components/forms/RemplisseuseForm"
import { OsmoseurData, RemplisseuseData } from "@/types"
import { useData } from "@/context/DataContext"
import { DataTable } from "@/components/data-table/DataTable"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { LayoutList, PlusCircle, Table as TableIcon } from "lucide-react"

type ViewMode = "entry" | "table"
type EquipmentType = "osmoseur" | "remplisseuse"

export default function InputPage() {
    const [activeTab, setActiveTab] = useState<EquipmentType>("osmoseur")
    const [viewMode, setViewMode] = useState<ViewMode>("entry")
    const [dateFilter, setDateFilter] = useState("")

    // Data State (Managed by Context)
    const {
        osmoseurList,
        remplisseuseList,
        addOsmoseurData,
        updateOsmoseurData,
        deleteOsmoseurData,
        addRemplisseuseData,
        updateRemplisseuseData,
        deleteRemplisseuseData
    } = useData()

    // Editing State
    const [editingOsmoseur, setEditingOsmoseur] = useState<OsmoseurData | null>(null)
    const [editingRemplisseuse, setEditingRemplisseuse] = useState<RemplisseuseData | null>(null)

    const handleOsmoseurSubmit = async (data: OsmoseurData) => {
        try {
            if (data.id) {
                // Update existing
                await updateOsmoseurData(data)
                setEditingOsmoseur(null)
            } else {
                // Add new
                await addOsmoseurData(data)
            }
            // If we were editing, go back to table, otherwise stay on entry (or maybe go to table? let's stay for rapid entry)
            if (editingOsmoseur) {
                setViewMode("table")
            }
        } catch (error) {
            console.error("Error submitting osmoseur data:", error)
            alert(`Erreur: ${error instanceof Error ? error.message : String(error)}`)
        }
    }

    const handleRemplisseuseSubmit = async (data: RemplisseuseData) => {
        try {
            if (data.id) {
                await updateRemplisseuseData(data)
                setEditingRemplisseuse(null)
            } else {
                await addRemplisseuseData(data)
            }
            if (editingRemplisseuse) {
                setViewMode("table")
            }
        } catch (error) {
            console.error("Error submitting remplisseuse data:", error)
            alert(`Erreur: ${error instanceof Error ? error.message : String(error)}`)
        }
    }

    const startEdit = (item: any) => {
        if (activeTab === "osmoseur") {
            setEditingOsmoseur(item)
        } else {
            setEditingRemplisseuse(item)
        }
        setViewMode("entry")
    }

    const handleDelete = async (id: string) => {
        if (confirm("Êtes-vous sûr de vouloir supprimer cet enregistrement ?")) {
            try {
                if (activeTab === "osmoseur") {
                    await deleteOsmoseurData(id)
                } else {
                    await deleteRemplisseuseData(id)
                }
            } catch (error) {
                console.error("Error deleting data:", error)
                alert("Erreur lors de la suppression des données.")
            }
        }
    }

    const cancelEdit = () => {
        setEditingOsmoseur(null)
        setEditingRemplisseuse(null)
        setViewMode("table")
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-foreground">Gestion des Relevés</h2>
                    <p className="text-gray-500">Saisie et consultation des données de production.</p>
                </div>

                <div className="flex items-center gap-4">
                    {/* View Switcher */}
                    <div className="flex bg-gray-100 p-1 rounded-lg">
                        <Button
                            variant={viewMode === "entry" ? "outline" : "ghost"}
                            size="sm"
                            onClick={() => {
                                setViewMode("entry")
                                setEditingOsmoseur(null)
                                setEditingRemplisseuse(null)
                            }}
                            className={viewMode === "entry" ? "bg-white shadow-sm" : "text-gray-500"}
                        >
                            <PlusCircle className="mr-2 h-4 w-4" />
                            Saisie
                        </Button>
                        <Button
                            variant={viewMode === "table" ? "outline" : "ghost"}
                            size="sm"
                            onClick={() => setViewMode("table")}
                            className={viewMode === "table" ? "bg-white shadow-sm" : "text-gray-500"}
                        >
                            <TableIcon className="mr-2 h-4 w-4" />
                            Tableau
                        </Button>
                    </div>

                    {/* Equipment Switcher */}
                    <div className="flex space-x-2 bg-white p-1 rounded-lg border border-gray-200">
                        <Button
                            variant={activeTab === "osmoseur" ? "default" : "ghost"}
                            onClick={() => setActiveTab("osmoseur")}
                            className="w-28"
                        >
                            Osmoseur
                        </Button>
                        <Button
                            variant={activeTab === "remplisseuse" ? "tech" : "ghost"}
                            onClick={() => setActiveTab("remplisseuse")}
                            className="w-28"
                        >
                            Remplisseuse
                        </Button>
                    </div>
                </div>
            </div>

            <AnimatePresence mode="wait">
                <motion.div
                    key={`${activeTab}-${viewMode}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                >
                    {viewMode === "entry" ? (
                        activeTab === "osmoseur" ? (
                            <OsmoseurForm
                                onSubmit={handleOsmoseurSubmit}
                                initialData={editingOsmoseur}
                                onCancel={editingOsmoseur ? cancelEdit : undefined}
                            />
                        ) : (
                            <RemplisseuseForm
                                onSubmit={handleRemplisseuseSubmit}
                                initialData={editingRemplisseuse}
                                onCancel={editingRemplisseuse ? cancelEdit : undefined}
                            />
                        )
                    ) : (
                        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                            <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <h3 className="text-lg font-semibold">
                                    Historique {activeTab === "osmoseur" ? "Osmoseur" : "Remplisseuse"}
                                </h3>
                                <div className="flex items-center gap-2">
                                    <label className="text-sm font-medium text-gray-700">Filtrer par date:</label>
                                    <Input
                                        type="date"
                                        value={dateFilter}
                                        onChange={(e) => setDateFilter(e.target.value)}
                                        className="w-auto"
                                    />
                                    {dateFilter && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => setDateFilter("")}
                                            className="text-gray-500"
                                        >
                                            Effacer
                                        </Button>
                                    )}
                                </div>
                            </div>
                            {activeTab === "osmoseur" ? (
                                <DataTable
                                    data={osmoseurList.filter(item => !dateFilter || item.date.startsWith(dateFilter))}
                                    onEdit={startEdit}
                                    onDelete={(item) => handleDelete(item.id!)}
                                    columns={[
                                        {
                                            header: "Date",
                                            accessorKey: "date",
                                            render: (val) => {
                                                const d = new Date(val)
                                                return (
                                                    <div className="flex flex-col text-xs">
                                                        <span className="font-medium">{d.toLocaleDateString()}</span>
                                                        <span className="text-gray-500">{d.toLocaleTimeString()}</span>
                                                    </div>
                                                )
                                            }
                                        },
                                        { header: "Technicien", accessorKey: "technicianName" },
                                        { header: "Débit Perm. (L/h)", accessorKey: "debitPermeat" },
                                        { header: "Débit Conc. (L/h)", accessorKey: "debitConcentrat" },
                                        { header: "Taux Recup. (%)", accessorKey: "tauxRecuperation" },
                                        { header: "Cond. Perm. (µS)", accessorKey: "conductivitePermeat" },
                                        { header: "pH Entrée", accessorKey: "phEntree" },
                                        { header: "pH Sortie", accessorKey: "phSortie" },
                                        { header: "Turbidité (NTU)", accessorKey: "turbidite" },
                                        { header: "Chlore (mg/L)", accessorKey: "chloreLibre" },
                                        { header: "Dureté (°f)", accessorKey: "dureteTotale" },
                                        { header: "TDS (ppm)", accessorKey: "tds" },
                                    ]}
                                />
                            ) : (
                                <DataTable
                                    data={remplisseuseList.filter(item => !dateFilter || item.date.startsWith(dateFilter))}
                                    onEdit={startEdit}
                                    onDelete={(item) => handleDelete(item.id!)}
                                    columns={[
                                        {
                                            header: "Date",
                                            accessorKey: "date",
                                            render: (val) => {
                                                const d = new Date(val)
                                                return (
                                                    <div className="flex flex-col text-xs">
                                                        <span className="font-medium">{d.toLocaleDateString()}</span>
                                                        <span className="text-gray-500">{d.toLocaleTimeString()}</span>
                                                    </div>
                                                )
                                            }
                                        },
                                        { header: "Technicien", accessorKey: "technicianName" },
                                        { header: "Temp. (°C)", accessorKey: "temperatureRemplissage" },
                                        { header: "Vol. (L)", accessorKey: "volumeRemplissage" },
                                        { header: "CO2 (g/L)", accessorKey: "carbonation" },
                                        { header: "Unités Conformes", accessorKey: "unitesProduitesConformes" },
                                        { header: "Heures Arrêt", accessorKey: "heuresArret" },
                                        { header: "MTBF (h)", accessorKey: "mtbf" },
                                        { header: "Rendement (%)", accessorKey: "rendement" },
                                        { header: "Conso Air/CO2", accessorKey: "consoAirCO2" },
                                        { header: "Vibrations", accessorKey: "vibrations" },
                                    ]}
                                />
                            )}
                        </div>
                    )}
                </motion.div>
            </AnimatePresence>
        </div>
    )
}
