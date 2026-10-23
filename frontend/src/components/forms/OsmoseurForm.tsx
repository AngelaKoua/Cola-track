"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { CheckCircle, Save } from "lucide-react"
import { useAuth } from "@/context/AuthContext"

import { OsmoseurData } from "@/types"

interface OsmoseurFormProps {
    onSubmit: (data: OsmoseurData) => void
    initialData?: OsmoseurData | null
    onCancel?: () => void
}

export function OsmoseurForm({ onSubmit, initialData, onCancel }: OsmoseurFormProps) {
    const { user } = useAuth()
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isSuccess, setIsSuccess] = useState(false)
    const [calculatedTaux, setCalculatedTaux] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        setIsSubmitting(true)

        const formData = new FormData(e.currentTarget)
        const data: OsmoseurData = {
            id: initialData?.id,
            technicianName: initialData?.technicianName || user?.username || "Inconnu",
            debitPermeat: formData.get("debitPermeat") as string,
            debitConcentrat: formData.get("debitConcentrat") as string,
            conductivitePermeat: formData.get("conductivitePermeat") as string,
            phEntree: formData.get("phEntree") as string,
            phSortie: formData.get("phSortie") as string,
            turbidite: formData.get("turbidite") as string,
            chloreLibre: formData.get("chloreLibre") as string,
            dureteTotale: formData.get("dureteTotale") as string,
            tds: formData.get("tds") as string,
            date: initialData?.date || new Date().toISOString(),
        }

        // Simulate small delay for UX
        await new Promise(resolve => setTimeout(resolve, 500))

        onSubmit(data)
        setIsSubmitting(false)
        setIsSuccess(true)
        setTimeout(() => setIsSuccess(false), 2000)
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>{initialData ? "Modifier Relevé Osmoseur" : "Relevé Osmoseur"}</CardTitle>
                <CardDescription>Saisissez les paramètres de fonctionnement de l'osmoseur.</CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Débit Perméat (L/h)</label>
                            <Input name="debitPermeat" type="number" defaultValue={initialData?.debitPermeat} placeholder="Ex: 15000" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Débit Concentrat (L/h)</label>
                            <Input name="debitConcentrat" type="number" defaultValue={initialData?.debitConcentrat} placeholder="Ex: 5000" required />
                        </div>
                        {initialData?.tauxRecuperation && (
                            <div className="space-y-2 md:col-span-2 bg-green-50 p-3 rounded-lg border border-green-200">
                                <label className="text-sm font-medium text-green-800">Taux de Récupération (calculé automatiquement)</label>
                                <div className="text-2xl font-bold text-green-600">{initialData.tauxRecuperation}%</div>
                            </div>
                        )}
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Conductivité Perméat (µS/cm)</label>
                            <Input name="conductivitePermeat" type="number" defaultValue={initialData?.conductivitePermeat} placeholder="Ex: 15" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">pH Entrée</label>
                            <Input name="phEntree" type="number" step="0.1" defaultValue={initialData?.phEntree} placeholder="Ex: 7.2" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">pH Sortie</label>
                            <Input name="phSortie" type="number" step="0.1" defaultValue={initialData?.phSortie} placeholder="Ex: 6.8" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Turbidité (NTU)</label>
                            <Input name="turbidite" type="number" step="0.01" defaultValue={initialData?.turbidite} placeholder="Ex: 0.5" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Chlore Libre (mg/L)</label>
                            <Input name="chloreLibre" type="number" step="0.01" defaultValue={initialData?.chloreLibre} placeholder="Ex: 0.1" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Dureté Totale (°f)</label>
                            <Input name="dureteTotale" type="number" defaultValue={initialData?.dureteTotale} placeholder="Ex: 0" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">TDS (ppm)</label>
                            <Input name="tds" type="number" defaultValue={initialData?.tds} placeholder="Ex: 10" required />
                        </div>
                    </div>

                    <div className="pt-4 flex gap-2">
                        <Button
                            type="submit"
                            className="w-full md:w-auto"
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? (
                                "Enregistrement..."
                            ) : isSuccess ? (
                                <>
                                    <CheckCircle className="mr-2 h-4 w-4" /> Enregistré
                                </>
                            ) : (
                                <>
                                    <Save className="mr-2 h-4 w-4" /> {initialData ? "Mettre à jour" : "Enregistrer"}
                                </>
                            )}
                        </Button>
                        {onCancel && (
                            <Button type="button" variant="outline" onClick={onCancel}>
                                Annuler
                            </Button>
                        )}
                    </div>
                </form>
            </CardContent>
        </Card>
    )
}
