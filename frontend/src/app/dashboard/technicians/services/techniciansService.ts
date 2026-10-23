/**
 * Technicians Service
 * 
 * Handles all API calls for technician management.
 * Provides typed interfaces for API responses.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface TechnicianSummaryStats {
    total: number
    active: number
    inactive: number
    total_entries: number
    period_days: number
}

export interface TechnicianListItem {
    id: number
    username: string
    is_active: boolean
    created_at: string | null
    total_entries: number
    last_entry: string | null
    equipment_type: string
    osmo_entries: number
    remp_entries: number
}

export interface EntriesByDay {
    date: string
    count: number
}

export interface TechnicianDetail {
    id: number
    username: string
    is_active: boolean
    created_at: string | null
    updated_at: string | null
    last_activity: string | null
    entries_by_day: EntriesByDay[]
    entries_by_equipment: {
        Osmoseur: number
        Remplisseuse: number
    }
    entries_by_hour: number[]
}

export interface TechnicianCreate {
    username: string
    email: string
}

export interface TechnicianUpdate {
    username?: string
}

export interface TechnicianStatusUpdate {
    is_active: boolean
}

export interface TechnicianResponse {
    id: number
    username: string
    is_active: boolean
    role: string
    created_at: string | null
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

export class TechniciansService {
    /**
     * Get summary KPIs for all technicians
     */
    static async getSummaryStats(periodDays: number = 30): Promise<TechnicianSummaryStats> {
        const params = new URLSearchParams({
            period_days: periodDays.toString()
        })

        const response = await fetch(
            `${API_BASE}/api/technicians/stats/summary?${params}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`)
        }

        return response.json()
    }

    /**
     * Get list of all technicians with statistics
     */
    static async getTechniciansList(periodDays: number = 30): Promise<TechnicianListItem[]> {
        const params = new URLSearchParams({
            period_days: periodDays.toString()
        })

        const response = await fetch(
            `${API_BASE}/api/technicians?${params}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`)
        }

        return response.json()
    }

    /**
     * Get detailed statistics for a specific technician
     */
    static async getTechnicianDetail(
        technicianId: number,
        periodDays: number = 30
    ): Promise<TechnicianDetail> {
        const params = new URLSearchParams({
            period_days: periodDays.toString()
        })

        const response = await fetch(
            `${API_BASE}/api/technicians/${technicianId}?${params}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`)
        }

        return response.json()
    }

    /**
     * Create a new technician
     */
    static async createTechnician(data: TechnicianCreate): Promise<TechnicianResponse> {
        const response = await fetch(
            `${API_BASE}/api/technicians`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            }
        )

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || "Failed to create technician")
        }

        return response.json()
    }

    /**
     * Update a technician
     */
    static async updateTechnician(
        technicianId: number,
        data: TechnicianUpdate
    ): Promise<TechnicianResponse> {
        const response = await fetch(
            `${API_BASE}/api/technicians/${technicianId}`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            }
        )

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || "Failed to update technician")
        }

        return response.json()
    }

    /**
     * Update technician status (activate/deactivate)
     */
    static async updateTechnicianStatus(
        technicianId: number,
        isActive: boolean
    ): Promise<TechnicianResponse> {
        const response = await fetch(
            `${API_BASE}/api/technicians/${technicianId}/status`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ is_active: isActive })
            }
        )

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || "Failed to update status")
        }

        return response.json()
    }

    /**
     * Delete (deactivate) a technician
     */
    static async deleteTechnician(technicianId: number): Promise<void> {
        const response = await fetch(
            `${API_BASE}/api/technicians/${technicianId}`,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || "Failed to delete technician")
        }
    }
}
