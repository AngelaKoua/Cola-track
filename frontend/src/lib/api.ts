import { OsmoseurApiRequest, OsmoseurApiResponse, RemplisseuseApiRequest, RemplisseuseApiResponse } from '@/types'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

// Osmoseur API functions
export const osmoseurApi = {
    async create(data: OsmoseurApiRequest): Promise<OsmoseurApiResponse> {
        const response = await fetch(`${API_BASE_URL}/osmoseur`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            const errorMessage = errorData.detail
                ? JSON.stringify(errorData.detail)
                : response.statusText
            throw new Error(`Failed to create osmoseur record: ${errorMessage}`)
        }

        return response.json()
    },

    async getAll(): Promise<OsmoseurApiResponse[]> {
        const response = await fetch(`${API_BASE_URL}/osmoseur`)

        if (!response.ok) {
            throw new Error(`Failed to fetch osmoseur records: ${response.statusText}`)
        }

        return response.json()
    },

    async getById(id: string): Promise<OsmoseurApiResponse> {
        const response = await fetch(`${API_BASE_URL}/osmoseur/${id}`)

        if (!response.ok) {
            throw new Error(`Failed to fetch osmoseur record: ${response.statusText}`)
        }

        return response.json()
    },

    async update(id: string, data: Partial<OsmoseurApiRequest>): Promise<OsmoseurApiResponse> {
        const response = await fetch(`${API_BASE_URL}/osmoseur/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            throw new Error(`Failed to update osmoseur record: ${response.statusText}`)
        }

        return response.json()
    },

    async delete(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/osmoseur/${id}`, {
            method: 'DELETE',
        })

        if (!response.ok) {
            throw new Error(`Failed to delete osmoseur record: ${response.statusText}`)
        }
    },
}

// Remplisseuse API functions
export const remplisseuseApi = {
    async create(data: RemplisseuseApiRequest): Promise<RemplisseuseApiResponse> {
        const response = await fetch(`${API_BASE_URL}/remplisseuse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            const errorMessage = errorData.detail
                ? JSON.stringify(errorData.detail)
                : response.statusText
            throw new Error(`Failed to create remplisseuse record: ${errorMessage}`)
        }

        return response.json()
    },

    async getAll(): Promise<RemplisseuseApiResponse[]> {
        const response = await fetch(`${API_BASE_URL}/remplisseuse`)

        if (!response.ok) {
            throw new Error(`Failed to fetch remplisseuse records: ${response.statusText}`)
        }

        return response.json()
    },

    async getById(id: string): Promise<RemplisseuseApiResponse> {
        const response = await fetch(`${API_BASE_URL}/remplisseuse/${id}`)

        if (!response.ok) {
            throw new Error(`Failed to fetch remplisseuse record: ${response.statusText}`)
        }

        return response.json()
    },

    async update(id: string, data: Partial<RemplisseuseApiRequest>): Promise<RemplisseuseApiResponse> {
        const response = await fetch(`${API_BASE_URL}/remplisseuse/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            throw new Error(`Failed to update remplisseuse record: ${response.statusText}`)
        }

        return response.json()
    },

    async delete(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/remplisseuse/${id}`, {
            method: 'DELETE',
        })

        if (!response.ok) {
            throw new Error(`Failed to delete remplisseuse record: ${response.statusText}`)
        }
    },
}

// Auth API
export const authApi = {
    async login(username: string, password: string): Promise<{ access_token: string, token_type: string, role: string, username: string, user_id: number }> {
        // Note: The token endpoint is at root, not /api/token
        const formBody = new URLSearchParams()
        formBody.append('username', username)
        formBody.append('password', password)

        const response = await fetch('http://127.0.0.1:8000/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formBody,
        })

        if (!response.ok) {
            throw new Error('Login failed: Invalid credentials')
        }

        return response.json()
    }
}

// Profile API
export const profileApi = {
    async getProfile(userId: number): Promise<Record<string, unknown>> {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_BASE_URL}/users/${userId}/profile`, {
            headers: { 'Authorization': `Bearer ${token}` },
        })

        if (!response.ok) {
            throw new Error(`Failed to fetch profile: ${response.statusText}`)
        }

        return response.json()
    },

    async updateProfile(userId: number, data: Record<string, string>): Promise<Record<string, unknown>> {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_BASE_URL}/users/${userId}/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            throw new Error(`Failed to update profile: ${response.statusText}`)
        }

        return response.json()
    },

    async changePassword(userId: number, data: { current_password: string, new_password: string }): Promise<Record<string, unknown>> {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_BASE_URL}/users/${userId}/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            throw new Error(`Failed to change password: ${response.statusText}`)
        }

        return response.json()
    },
}
