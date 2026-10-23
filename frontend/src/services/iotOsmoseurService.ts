import { API_BASE } from '@/lib/config'
/**
 * IoT Osmoseur API service.
 *
 * Handles data fetching for the IoT monitoring dashboard.
 * Uses native fetch (consistent with lib/api.ts pattern).
 */

const API_BASE_URL = `${API_BASE}/api/iot/osmoseur`

export interface IoTOsmoseurReading {
    id: string
    device_id: string
    debit_in: number | null
    turb_in: number | null
    ph: number | null
    tds: number | null
    debit_out: number | null
    turb_out: number | null
    created_at: string
}

export interface IoTOsmoseurStatus {
    status: "CONNECTED" | "DISCONNECTED"
    last_seen: string | null
}

export const iotOsmoseurApi = {
    async getLatest(): Promise<IoTOsmoseurReading> {
        const response = await fetch(`${API_BASE_URL}/latest`)
        if (!response.ok) {
            throw new Error(`Failed to fetch latest reading: ${response.statusText}`)
        }
        return response.json()
    },

    async getTimeseries(minutes: number = 5): Promise<IoTOsmoseurReading[]> {
        const response = await fetch(`${API_BASE_URL}/timeseries?minutes=${minutes}`)
        if (!response.ok) {
            throw new Error(`Failed to fetch timeseries: ${response.statusText}`)
        }
        return response.json()
    },

    async getStatus(): Promise<IoTOsmoseurStatus> {
        const response = await fetch(`${API_BASE_URL}/status`)
        if (!response.ok) {
            throw new Error(`Failed to fetch status: ${response.statusText}`)
        }
        return response.json()
    },
}
