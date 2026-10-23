"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { CheckCircle, Save } from "lucide-react"
import { useAuth } from "@/context/AuthContext"

import { RemplisseuseData } from "@/types"

interface RemplisseuseFormProps {
    onSubmit: (data: RemplisseuseData) => void
    initialData?: RemplisseuseData | null
    onCancel?: () => void
}

export function RemplisseuseForm({ onSubmit, initialData, onCancel }: RemplisseuseFormProps) {
    const { user } = useAuth()
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isSuccess, setIsSuccess] = useState(false)

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        setIsSubmitting(true)

        const formData = new FormData(e.currentTarget)
        const data: RemplisseuseData = {
            id: initialData?.id,
            technicianName: initialData?.technicianName || user?.username || "Inconnu",
            temperatureRemplissage: formData.get("temperatureRemplissage") as string,
            volumeRemplissage: formData.get("volumeRemplissage") as string,
            carbonation: formData.get("carbonation") as string,
            unitesProduitesConformes: formData.get("unitesProduitesConformes") as string,
            heuresArret: formData.get("heuresArret") as string,
            mtbf: formData.get("mtbf") as string,
            consoAirCO2: formData.get("consoAirCO2") as string,
            vibrations: formData.get("vibrations") as string,
            date: initialData?.date || new Date().toISOString(),
        }

        await new Promise(resolve => setTimeout(resolve, 500))

        onSubmit(data)
        setIsSubmitting(false)
        setIsSuccess(true)
        setTimeout(() => setIsSuccess(false), 2000)
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>{initialData ? "Modifier Relevé Remplisseuse" : "Relevé Remplisseuse"}</CardTitle>
                <CardDescription>Saisissez les paramètres de production de la remplisseuse.</CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Température Remplissage (°C)</label>
                            <Input name="temperatureRemplissage" type="number" step="0.1" defaultValue={initialData?.temperatureRemplissage} placeholder="Ex: 4.0" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Volume de Remplissage (L)</label>
                            <Input name="volumeRemplissage" type="number" step="0.01" defaultValue={initialData?.volumeRemplissage} placeholder="Ex: 1.5" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Carbonation CO (g/L)</label>
                            <Input name="carbonation" type="number" step="0.1" defaultValue={initialData?.carbonation} placeholder="Ex: 8.0" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Unités Produites Conformes</label>
                            <Input name="unitesProduitesConformes" type="number" defaultValue={initialData?.unitesProduitesConformes} placeholder="Ex: 9500" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Heures d'Arrêt (h)</label>
                            <Input name="heuresArret" type="number" step="0.1" defaultValue={initialData?.heuresArret} placeholder="Ex: 2.0" required />
                        </div>
                        {initialData?.rendement && (
                            <div className="space-y-2 md:col-span-2 bg-blue-50 p-3 rounded-lg border border-blue-200">
                                <label className="text-sm font-medium text-blue-800">Rendement Production (calculé automatiquement)</label>
                                <div className="text-2xl font-bold text-blue-600">{initialData.rendement}%</div>
                            </div>
                        )}
                        <div className="space-y-2">
                            <label className="text-sm font-medium">MTBF (h)</label>
                            <Input name="mtbf" type="number" defaultValue={initialData?.mtbf} placeholder="Ex: 48" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Conso Air / CO (m/h)</label>
                            <Input name="consoAirCO2" type="number" step="0.1" defaultValue={initialData?.consoAirCO2} placeholder="Ex: 120" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Vibrations Moteurs (mm/s)</label>
                            <Input name="vibrations" type="number" step="0.1" defaultValue={initialData?.vibrations} placeholder="Ex: 2.5" required />
                        </div>
                    </div>

                    <div className="pt-4 flex gap-2">
                        <Button
                            type="submit"
                            className="w-full md:w-auto bg-accent-blue hover:bg-accent-blue/90"
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
