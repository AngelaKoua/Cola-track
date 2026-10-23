/**
 * useTechnicians Hook
 * 
 * Custom hook for managing technicians data and operations.
 * Handles loading states, errors, and data fetching/mutation.
 */

import { useState, useEffect, useCallback } from 'react'
import {
    TechniciansService,
    type TechnicianSummaryStats,
    type TechnicianListItem,
    type TechnicianDetail,
    type TechnicianCreate,
    type TechnicianUpdate
} from '../services/techniciansService'

export interface UseTechniciansReturn {
    // Data
    stats: TechnicianSummaryStats | null
    technicians: TechnicianListItem[]
    loading: boolean
    error: Error | null

    // Actions
    fetchData: () => Promise<void>
    createTechnician: (data: TechnicianCreate) => Promise<void>
    updateTechnician: (id: number, data: TechnicianUpdate) => Promise<void>
    toggleStatus: (id: number, isActive: boolean) => Promise<void>
    deleteTechnician: (id: number) => Promise<void>
}

export function useTechnicians(periodDays: number = 30): UseTechniciansReturn {
    const [stats, setStats] = useState<TechnicianSummaryStats | null>(null)
    const [technicians, setTechnicians] = useState<TechnicianListItem[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<Error | null>(null)

    const fetchData = useCallback(async () => {
        setLoading(true)
        setError(null)

        try {
            const [statsData, techniciansData] = await Promise.all([
                TechniciansService.getSummaryStats(periodDays),
                TechniciansService.getTechniciansList(periodDays)
            ])

            setStats(statsData)
            setTechnicians(techniciansData)
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to fetch data'))
            console.error('Error fetching technicians data:', err)
        } finally {
            setLoading(false)
        }
    }, [periodDays])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    const createTechnician = async (data: TechnicianCreate) => {
        try {
            await TechniciansService.createTechnician(data)
            await fetchData() // Refresh list
        } catch (err) {
            throw err instanceof Error ? err : new Error('Failed to create technician')
        }
    }

    const updateTechnician = async (id: number, data: TechnicianUpdate) => {
        try {
            await TechniciansService.updateTechnician(id, data)
            await fetchData() // Refresh list
        } catch (err) {
            throw err instanceof Error ? err : new Error('Failed to update technician')
        }
    }

    const toggleStatus = async (id: number, isActive: boolean) => {
        try {
            await TechniciansService.updateTechnicianStatus(id, isActive)
            await fetchData() // Refresh list
        } catch (err) {
            throw err instanceof Error ? err : new Error('Failed to update status')
        }
    }

    const deleteTechnician = async (id: number) => {
        try {
            await TechniciansService.deleteTechnician(id)
            await fetchData() // Refresh list
        } catch (err) {
            throw err instanceof Error ? err : new Error('Failed to delete technician')
        }
    }

    return {
        stats,
        technicians,
        loading,
        error,
        fetchData,
        createTechnician,
        updateTechnician,
        toggleStatus,
        deleteTechnician
    }
}
