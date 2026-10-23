import { Incident, IncidentCreate, IncidentUpdate, IncidentKPI, IncidentFilters } from '@/types/incident';

// Use environment variable or default to localhost
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const incidentService = {
    // Get all incidents with optional filters
    getAll: async (page = 1, pageSize = 50, filters?: IncidentFilters) => {
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: pageSize.toString(),
        });

        if (filters) {
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== undefined && value !== null && value !== '') {
                    params.append(key, value);
                }
            });
        }

        const response = await fetch(`${API_URL}/incidents?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch incidents');
        return response.json();
    },

    // Get incident by ID
    getById: async (id: string): Promise<Incident> => {
        const response = await fetch(`${API_URL}/incidents/${id}`);
        if (!response.ok) throw new Error('Failed to fetch incident');
        return response.json();
    },

    // Create new incident
    create: async (data: IncidentCreate): Promise<Incident> => {
        const response = await fetch(`${API_URL}/incidents`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to create incident');
        return response.json();
    },

    // Update incident
    update: async (id: string, data: IncidentUpdate): Promise<Incident> => {
        const response = await fetch(`${API_URL}/incidents/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to update incident');
        return response.json();
    },

    // Resolve incident
    resolve: async (id: string): Promise<Incident> => {
        const response = await fetch(`${API_URL}/incidents/${id}/resolve`, {
            method: 'PATCH',
        });
        if (!response.ok) throw new Error('Failed to resolve incident');
        return response.json();
    },

    // Delete incident
    delete: async (id: string): Promise<void> => {
        const response = await fetch(`${API_URL}/incidents/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete incident');
    },

    // Get KPIs
    getKPIs: async (): Promise<IncidentKPI> => {
        const response = await fetch(`${API_URL}/incidents/kpis`);
        if (!response.ok) throw new Error('Failed to fetch KPIs');
        return response.json();
    }
};

export default incidentService;
