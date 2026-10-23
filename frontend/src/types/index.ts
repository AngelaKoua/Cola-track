// Type definitions for frontend data structures
export type OsmoseurData = {
    id?: string
    technicianName: string
    debitPermeat: string
    debitConcentrat: string
    tauxRecuperation?: string
    conductivitePermeat: string
    phEntree: string
    phSortie: string
    turbidite: string
    chloreLibre: string
    dureteTotale: string
    tds: string
    date: string
}

export type RemplisseuseData = {
    id?: string
    technicianName: string
    temperatureRemplissage: string
    volumeRemplissage: string
    carbonation: string
    unitesProduitesConformes: string
    heuresArret: string
    mtbf: string
    rendement?: string
    consoAirCO2: string
    vibrations: string
    date: string
}

export type OsmoseurApiRequest = {
    technician_name: string
    debit_permeat: number
    debit_concentrat: number
    conductivite_permeat: number
    ph_entree: number
    ph_sortie: number
    turbidite: number
    chlore_libre: number
    durete_totale: number
    tds: number
}

export type OsmoseurApiResponse = OsmoseurApiRequest & {
    id: string
    taux_recuperation: number
    created_at: string
    updated_at: string
}

export type RemplisseuseApiRequest = {
    technician_name: string
    temperature_remplissage: number
    volume_remplissage: number
    carbonation: number
    unites_produites_conformes: number
    heures_arret: number
    mtbf: number
    conso_air_co2: number
    vibrations: number
}

export type RemplisseuseApiResponse = RemplisseuseApiRequest & {
    id: string
    rendement: number
    created_at: string
    updated_at: string
}
