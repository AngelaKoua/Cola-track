/**
 * useDashboardData Hook
 * 
 * Custom hook for fetching and managing dashboard data.
 * Handles loading states, errors, and automatic refetching.
 */

import { useState, useEffect, useCallback } from 'react'
import { DashboardService, type DashboardOverviewResponse } from '../services/dashboardService'

export interface UseDashboardDataParams {
    startDate: string
    endDate: string
    equipment?: string
}

export interface UseDashboardDataReturn {
    data: DashboardOverviewResponse | null
    loading: boolean
    error: Error | null
    refetch: () => Promise<void>
}

export function useDashboardData({
    startDate,
    endDate,
    equipment = "all"
}: UseDashboardDataParams): UseDashboardDataReturn {
    const [data, setData] = useState<DashboardOverviewResponse | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<Error | null>(null)

    const fetchData = useCallback(async () => {
        setLoading(true)
        setError(null)

        try {
            const response = await DashboardService.getDashboardOverview(
                startDate,
                endDate,
                equipment
            )
            setData(response)
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to fetch dashboard data'))
            console.error('Dashboard data fetch error:', err)
        } finally {
            setLoading(false)
        }
    }, [startDate, endDate, equipment])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    return {
        data,
        loading,
        error,
        refetch: fetchData
    }
}
