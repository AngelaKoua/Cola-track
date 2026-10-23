"use client"

import React, { createContext, useContext, useState, useEffect } from "react"
import { OsmoseurData, RemplisseuseData, OsmoseurApiRequest, RemplisseuseApiRequest } from "@/types"
import { osmoseurApi, remplisseuseApi } from "@/lib/api"

interface DataContextType {
    osmoseurList: OsmoseurData[]
    remplisseuseList: RemplisseuseData[]
    addOsmoseurData: (data: OsmoseurData) => Promise<void>
    updateOsmoseurData: (data: OsmoseurData) => Promise<void>
    deleteOsmoseurData: (id: string) => Promise<void>
    addRemplisseuseData: (data: RemplisseuseData) => Promise<void>
    updateRemplisseuseData: (data: RemplisseuseData) => Promise<void>
    deleteRemplisseuseData: (id: string) => Promise<void>
    isLoading: boolean
    error: string | null
}

const DataContext = createContext<DataContextType | undefined>(undefined)

function osmoseurToApiRequest(data: OsmoseurData): OsmoseurApiRequest {
    return {
        technician_name: data.technicianName,
        debit_permeat: parseFloat(data.debitPermeat) || 0,
        debit_concentrat: parseFloat(data.debitConcentrat) || 0,
        conductivite_permeat: parseFloat(data.conductivitePermeat) || 0,
        ph_entree: parseFloat(data.phEntree) || 0,
        ph_sortie: parseFloat(data.phSortie) || 0,
        turbidite: parseFloat(data.turbidite) || 0,
        chlore_libre: parseFloat(data.chloreLibre) || 0,
        durete_totale: parseFloat(data.dureteTotale) || 0,
        tds: parseFloat(data.tds) || 0,
    }
}

function remplisseuseToApiRequest(data: RemplisseuseData): RemplisseuseApiRequest {
    return {
        technician_name: data.technicianName,
        temperature_remplissage: parseFloat(data.temperatureRemplissage) || 0,
        volume_remplissage: parseFloat(data.volumeRemplissage) || 0,
        carbonation: parseFloat(data.carbonation) || 0,
        unites_produites_conformes: parseFloat(data.unitesProduitesConformes) || 0,
        heures_arret: parseFloat(data.heuresArret) || 0,
        mtbf: parseFloat(data.mtbf) || 0,
        conso_air_co2: parseFloat(data.consoAirCO2) || 0,
        vibrations: parseFloat(data.vibrations) || 0,
    }
}

function apiResponseToOsmoseur(response: any): OsmoseurData {
    return {
        id: response.id,
        technicianName: response.technician_name,
        debitPermeat: response.debit_permeat.toString(),
        debitConcentrat: response.debit_concentrat.toString(),
        tauxRecuperation: response.taux_recuperation.toString(),
        conductivitePermeat: response.conductivite_permeat.toString(),
        phEntree: response.ph_entree.toString(),
        phSortie: response.ph_sortie.toString(),
        turbidite: response.turbidite.toString(),
        chloreLibre: response.chlore_libre.toString(),
        dureteTotale: response.durete_totale.toString(),
        tds: response.tds.toString(),
        date: response.created_at,
    }
}

function apiResponseToRemplisseuse(response: any): RemplisseuseData {
    return {
        id: response.id,
        technicianName: response.technician_name,
        temperatureRemplissage: response.temperature_remplissage.toString(),
        volumeRemplissage: response.volume_remplissage.toString(),
        carbonation: response.carbonation.toString(),
        unitesProduitesConformes: response.unites_produites_conformes.toString(),
        heuresArret: response.heures_arret.toString(),
        mtbf: response.mtbf.toString(),
        rendement: response.rendement.toString(),
        consoAirCO2: response.conso_air_co2.toString(),
        vibrations: response.vibrations.toString(),
        date: response.created_at,
    }
}

export function DataProvider({ children }: { children: React.ReactNode }) {
    const [osmoseurList, setOsmoseurList] = useState<OsmoseurData[]>([])
    const [remplisseuseList, setRemplisseuseList] = useState<RemplisseuseData[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        setIsLoading(true)
        setError(null)
        try {
            const [osmoseurResponse, remplisseuseResponse] = await Promise.all([
                osmoseurApi.getAll(),
                remplisseuseApi.getAll()
            ])

            setOsmoseurList((osmoseurResponse as any).data.map(apiResponseToOsmoseur))
            setRemplisseuseList((remplisseuseResponse as any).data.map(apiResponseToRemplisseuse))
        } catch (err) {
            console.error("Failed to load data:", err)
            setError("Impossible de charger les données. Vérifiez que le serveur backend est démarré.")
        } finally {
            setIsLoading(false)
        }
    }

    const addOsmoseurData = async (data: OsmoseurData) => {
        try {
            const apiRequest = osmoseurToApiRequest(data)
            const response = await osmoseurApi.create(apiRequest)
            const newItem = apiResponseToOsmoseur(response)
            setOsmoseurList(prev => [newItem, ...prev])
        } catch (err) {
            console.error("Failed to add osmoseur data:", err)
            throw new Error(`Échec de l'enregistrement des données Osmoseur: ${err instanceof Error ? err.message : String(err)}`)
        }
    }

    const updateOsmoseurData = async (data: OsmoseurData) => {
        if (!data.id) throw new Error("ID manquant pour la mise à jour")

        try {
            const apiRequest = osmoseurToApiRequest(data)
            const response = await osmoseurApi.update(data.id, apiRequest)
            const updatedItem = apiResponseToOsmoseur(response)
            setOsmoseurList(prev => prev.map(item => item.id === data.id ? updatedItem : item))
        } catch (err) {
            console.error("Failed to update osmoseur data:", err)
            throw new Error("Échec de la mise à jour des données Osmoseur")
        }
    }

    const deleteOsmoseurData = async (id: string) => {
        try {
            await osmoseurApi.delete(id)
            setOsmoseurList(prev => prev.filter(item => item.id !== id))
        } catch (err) {
            console.error("Failed to delete osmoseur data:", err)
            throw new Error("Échec de la suppression des données Osmoseur")
        }
    }

    const addRemplisseuseData = async (data: RemplisseuseData) => {
        try {
            const apiRequest = remplisseuseToApiRequest(data)
            const response = await remplisseuseApi.create(apiRequest)
            const newItem = apiResponseToRemplisseuse(response)
            setRemplisseuseList(prev => [newItem, ...prev])
        } catch (err) {
            console.error("Failed to add remplisseuse data:", err)
            throw new Error(`Échec de l'enregistrement des données Remplisseuse: ${err instanceof Error ? err.message : String(err)}`)
        }
    }

    const updateRemplisseuseData = async (data: RemplisseuseData) => {
        if (!data.id) throw new Error("ID manquant pour la mise à jour")

        try {
            const apiRequest = remplisseuseToApiRequest(data)
            const response = await remplisseuseApi.update(data.id, apiRequest)
            const updatedItem = apiResponseToRemplisseuse(response)
            setRemplisseuseList(prev => prev.map(item => item.id === data.id ? updatedItem : item))
        } catch (err) {
            console.error("Failed to update remplisseuse data:", err)
            throw new Error("Échec de la mise à jour des données Remplisseuse")
        }
    }

    const deleteRemplisseuseData = async (id: string) => {
        try {
            await remplisseuseApi.delete(id)
            setRemplisseuseList(prev => prev.filter(item => item.id !== id))
        } catch (err) {
            console.error("Failed to delete remplisseuse data:", err)
            throw new Error("Échec de la suppression des données Remplisseuse")
        }
    }

    return (
        <DataContext.Provider value={{
            osmoseurList,
            remplisseuseList,
            addOsmoseurData,
            updateOsmoseurData,
            deleteOsmoseurData,
            addRemplisseuseData,
            updateRemplisseuseData,
            deleteRemplisseuseData,
            isLoading,
            error
        }}>
            {children}
        </DataContext.Provider>
    )
}

export function useData() {
    const context = useContext(DataContext)
    if (context === undefined) {
        throw new Error("useData must be used within a DataProvider")
    }
    return context
}
