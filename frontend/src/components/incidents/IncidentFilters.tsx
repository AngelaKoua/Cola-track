import React from 'react';
import { IncidentFilters } from '@/types/incident';

interface IncidentFiltersProps {
    filters: IncidentFilters;
    onFilterChange: (newFilters: IncidentFilters) => void;
}

const LIGNES = ["Ligne 1", "Ligne 2", "Traitement Eaux"];
const STATUTS = ["Ouvert", "En cours", "En attente", "Résolu"];
const CRITICITES = ["Critique", "Élevé", "Moyen", "Faible"];

const IncidentFiltersBar: React.FC<IncidentFiltersProps> = ({ filters, onFilterChange }) => {
    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const { name, value } = e.target;
        onFilterChange({
            ...filters,
            [name]: value === 'all' ? undefined : value
        });
    };

    return (
        <div className="flex flex-wrap gap-4 p-4 mb-6 bg-white border border-gray-100 rounded-xl shadow-sm">
            {/* Ligne Filter */}
            <div className="flex-1 min-w-[200px]">
                <label className="block text-xs font-medium text-gray-500 mb-1">Ligne de Production</label>
                <select
                    name="ligne"
                    value={filters.ligne || 'all'}
                    onChange={handleChange}
                    className="w-full h-9 px-3 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
                >
                    <option value="all">Toutes les lignes</option>
                    {LIGNES.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
            </div>

            {/* Statut Filter */}
            <div className="flex-1 min-w-[200px]">
                <label className="block text-xs font-medium text-gray-500 mb-1">Statut</label>
                <select
                    name="statut"
                    value={filters.statut || 'all'}
                    onChange={handleChange}
                    className="w-full h-9 px-3 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
                >
                    <option value="all">Tous les statuts</option>
                    {STATUTS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
            </div>

            {/* Criticité Filter */}
            <div className="flex-1 min-w-[200px]">
                <label className="block text-xs font-medium text-gray-500 mb-1">Criticité</label>
                <select
                    name="criticite"
                    value={filters.criticite || 'all'}
                    onChange={handleChange}
                    className="w-full h-9 px-3 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
                >
                    <option value="all">Toutes criticités</option>
                    {CRITICITES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
            </div>

            {/* Responsable Filter (Simple text input for now or select if list available) */}
            {/* Could be improved with a proper search input */}
        </div>
    );
};

export default IncidentFiltersBar;
