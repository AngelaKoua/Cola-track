"use client"

import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Incident, IncidentFilters, IncidentKPI } from '@/types/incident';
import incidentService from '@/services/incidentService';
import IncidentTable from '@/components/incidents/IncidentTable';
import IncidentFiltersBar from '@/components/incidents/IncidentFilters';
import IncidentModal from '@/components/incidents/IncidentModal';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { toast } from 'react-hot-toast';

export default function IncidentsPage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [kpis, setKpis] = useState<IncidentKPI | null>(null);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState<IncidentFilters>({});

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedIncident, setSelectedIncident] = useState<Incident | undefined>(undefined);
    const [isSaving, setIsSaving] = useState(false);
    const [isViewMode, setIsViewMode] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [incidentsData, kpisData] = await Promise.all([
                incidentService.getAll(1, 100, filters),
                incidentService.getKPIs()
            ]);
            setIncidents(incidentsData.data);
            setKpis(kpisData);
        } catch (error) {
            console.error("Failed to fetch data", error);
            toast.error("Erreur lors du chargement des données");
        } finally {
            setLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleCreate = () => {
        setSelectedIncident(undefined);
        setIsViewMode(false);
        setIsModalOpen(true);
    };

    const handleView = useCallback((incident: Incident) => {
        setSelectedIncident(incident);
        setIsViewMode(true);
        setIsModalOpen(true);
    }, []);

    // Handle viewIncident query param when arriving from notification
    useEffect(() => {
        const viewId = searchParams?.get('viewIncident');
        if (viewId && incidents.length > 0) {
            const incidentToView = incidents.find(inc => inc.id === viewId);
            if (incidentToView) {
                handleView(incidentToView);
                // Clean up the URL to prevent re-opening on refresh
                router.replace('/dashboard/incidents', { scroll: false });
            }
        }
    }, [searchParams, incidents, router, handleView]);

    const handleSave = async (data: any) => {
        try {
            setIsSaving(true);
            if (selectedIncident) {
                await incidentService.update(selectedIncident.id, data);
                toast.success("Incident mis à jour");
            } else {
                await incidentService.create(data);
                toast.success("Incident créé avec succès");
            }
            setIsModalOpen(false);
            fetchData();
        } catch (error) {
            console.error("Save error", error);
            toast.error("Erreur lors de l'enregistrement");
        } finally {
            setIsSaving(false);
        }
    };

    const handleResolve = async (id: string) => {
        try {
            // Optimistic update could be done here
            await incidentService.resolve(id);
            toast.success("Incident résolu !");
            fetchData();
        } catch (error) {
            console.error("Resolve error", error);
            toast.error("Erreur lors de la résolution");
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Êtes-vous sûr de vouloir supprimer cet incident ?")) return;
        try {
            await incidentService.delete(id);
            toast.success("Incident supprimé avec succès");
            fetchData();
        } catch (error) {
            console.error("Delete error", error);
            toast.error("Erreur lors de la suppression de l'incident");
        }
    };

    return (
        <div className="p-8 space-y-8 bg-gray-50/50 min-h-screen">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Gestion des Incidents</h1>
                </div>
                <button
                    onClick={handleCreate}
                    className="flex items-center gap-2 px-5 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 active:bg-red-800 transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                    <span>Nouvel incident</span>
                </button>
            </div>

            {/* KPI Cards */}
            {kpis && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Card className="border-none shadow-sm bg-white hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                            <CardTitle className="text-sm font-medium text-gray-500">Total Incidents</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-gray-900">{kpis.total_incidents}</div>
                        </CardContent>
                    </Card>

                    <Card className="border-none shadow-sm bg-white hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                            <CardTitle className="text-sm font-medium text-gray-500">Ouverts</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-orange-600">{kpis.incidents_ouverts}</div>
                            <p className="text-xs text-gray-500 mt-1">En attente de résolution</p>
                        </CardContent>
                    </Card>

                    <Card className="border-none shadow-sm bg-white hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                            <CardTitle className="text-sm font-medium text-gray-500">MTTR Moyen</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-red-600">{Math.round(kpis.mttr_moyen_heures)} h</div>
                            <p className="text-xs text-gray-500 mt-1">Temps de résolution</p>
                        </CardContent>
                    </Card>

                    <Card className="border-none shadow-sm bg-white hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                            <CardTitle className="text-sm font-medium text-gray-500">Respect Deadline</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-green-600">{Math.round(kpis.respect_deadline_percent)}%</div>
                            <p className="text-xs text-gray-500 mt-1">Objectif {">"} 90%</p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Main Content */}
            <div className="space-y-4">
                <IncidentFiltersBar filters={filters} onFilterChange={setFilters} />

                <IncidentTable
                    incidents={incidents}
                    isLoading={loading}
                    onView={handleView}
                    onResolve={handleResolve}
                    onDelete={handleDelete}
                />
            </div>

            {/* Modal */}
            <IncidentModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSave}
                incident={selectedIncident}
                isSaving={isSaving}
                isViewMode={isViewMode}
            />
        </div>
    );
}

