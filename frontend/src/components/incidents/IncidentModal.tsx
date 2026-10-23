import React, { useState, useEffect, useRef, useCallback } from 'react';
import Modal from '@/components/ui/Modal';
import { Incident, IncidentCreate, IncidentUpdate } from '@/types/incident';
import { Loader2 } from 'lucide-react';
import { API_BASE } from '@/lib/config'
import { authHeaders } from '@/lib/auth'

interface IncidentModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (data: IncidentCreate | IncidentUpdate) => Promise<void>;
    incident?: Incident;
    isSaving?: boolean;
    isViewMode?: boolean;
}

interface PlatformUser {
    id: number;
    username: string;
    role: string;
}

const API_URL = API_BASE;

const LIGNES = ["Ligne 1", "Ligne 2", "Traitement Eaux"];
const EQUIPEMENTS = ["Remplisseuse", "Osmoseur", "Etiqueteuse", "Fardeleuse", "Palettiseur", "Convoyeur", "Mixer", "Chaudière"];
const TYPES = ["Panne Mécanique", "Panne Électrique", "Qualité", "Sécurité", "Manque Matière", "Autre"];
const CRITICITES = [
    { value: "Critique", label: "Critique (Arrêt total)", color: "text-red-600" },
    { value: "Élevé", label: "Élevé (Ralentissement)", color: "text-orange-600" },
    { value: "Moyen", label: "Moyen (Risque)", color: "text-yellow-600" },
    { value: "Faible", label: "Faible (Amélioration)", color: "text-gray-600" }
];

const IncidentModal: React.FC<IncidentModalProps> = ({ isOpen, onClose, onSave, incident, isSaving, isViewMode }) => {
    const [formData, setFormData] = useState<Partial<IncidentCreate>>({
        ligne: '',
        equipement: '',
        type_incident: '',
        criticite: 'Moyen',
        description_probleme: '',
        cause_racine: '',
        action_corrective: '',
        responsable: '',
        deadline: new Date().toISOString().split('T')[0]
    });

    // Autocomplete state for responsable
    const [userSearch, setUserSearch] = useState('');
    const [userResults, setUserResults] = useState<PlatformUser[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (incident) {
            setFormData({
                ligne: incident.ligne,
                equipement: incident.equipement,
                type_incident: incident.type_incident,
                criticite: incident.criticite,
                description_probleme: incident.description_probleme,
                cause_racine: incident.cause_racine || '',
                action_corrective: incident.action_corrective || '',
                responsable: incident.responsable,
                deadline: incident.deadline
            });
            setUserSearch(incident.responsable);
        } else {
            setFormData({
                ligne: '',
                equipement: '',
                type_incident: '',
                criticite: 'Moyen',
                description_probleme: '',
                cause_racine: '',
                action_corrective: '',
                responsable: '',
                deadline: new Date().toISOString().split('T')[0]
            });
            setUserSearch('');
        }
    }, [incident, isOpen]);

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Debounced user search
    const searchUsers = useCallback(async (query: string) => {
        if (query.length < 1) {
            setUserResults([]);
            setShowDropdown(false);
            return;
        }
        setIsSearching(true);
        try {
            const res = await fetch(`${API_URL}/api/users/list?search=${encodeURIComponent(query)}`, { headers: authHeaders() });
            if (res.ok) {
                const data: PlatformUser[] = await res.json();
                setUserResults(data);
                setShowDropdown(data.length > 0);
            }
        } catch {
            setUserResults([]);
        } finally {
            setIsSearching(false);
        }
    }, []);

    const handleUserSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setUserSearch(value);
        // Clear the responsable — user hasn't selected yet
        setFormData(prev => ({ ...prev, responsable: '' }));

        // Debounce the API call (250ms)
        if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
        searchTimeoutRef.current = setTimeout(() => searchUsers(value), 250);
    };

    const handleSelectUser = (user: PlatformUser) => {
        setUserSearch(user.username);
        setFormData(prev => ({ ...prev, responsable: user.username }));
        setShowDropdown(false);
    };

    // Load all users on focus (shows full list for quick selection)
    const handleSearchFocus = () => {
        if (userSearch.length === 0) {
            searchUsers(''); // Will not trigger if < 1 char
            // Instead, fetch all users
            fetch(`${API_URL}/api/users/list?search=`, { headers: authHeaders() })
                .then(res => res.ok ? res.json() : [])
                .then((data: PlatformUser[]) => {
                    setUserResults(data);
                    setShowDropdown(data.length > 0);
                })
                .catch(() => { });
        } else {
            searchUsers(userSearch);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.responsable) {
            alert('Veuillez sélectionner un responsable parmi les utilisateurs de la plateforme.');
            return;
        }
        await onSave(formData as IncidentCreate);
    };

    const getRoleBadge = (role: string) => {
        switch (role) {
            case 'manager': return 'bg-purple-100 text-purple-700';
            case 'technician': return 'bg-green-100 text-green-700';
            default: return 'bg-gray-100 text-gray-600';
        }
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={isViewMode ? "Détails de l'Incident" : incident ? "Modifier l'Incident" : "Nouvel Incident"}
            className="max-w-3xl"
        >
            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Ligne */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Ligne de Production *</label>
                        <select
                            name="ligne"
                            value={formData.ligne}
                            onChange={handleChange}
                            required
                            disabled={isViewMode}
                            className="w-full h-10 px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-75 disabled:bg-gray-50"
                        >
                            <option value="">Sélectionner une ligne</option>
                            {LIGNES.map(l => <option key={l} value={l}>{l}</option>)}
                        </select>
                    </div>

                    {/* Equipement */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Équipement *</label>
                        <select
                            name="equipement"
                            value={formData.equipement}
                            onChange={handleChange}
                            required
                            disabled={isViewMode}
                            className="w-full h-10 px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-75 disabled:bg-gray-50"
                        >
                            <option value="">Sélectionner un équipement</option>
                            {EQUIPEMENTS.map(e => <option key={e} value={e}>{e}</option>)}
                        </select>
                    </div>

                    {/* Type Incident */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Type d&apos;Incident *</label>
                        <select
                            name="type_incident"
                            value={formData.type_incident}
                            onChange={handleChange}
                            required
                            disabled={isViewMode}
                            className="w-full h-10 px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-75 disabled:bg-gray-50"
                        >
                            <option value="">Sélectionner le type</option>
                            {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>

                    {/* Criticité */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Criticité *</label>
                        <select
                            name="criticite"
                            value={formData.criticite}
                            onChange={handleChange}
                            required
                            disabled={isViewMode}
                            className="w-full h-10 px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-75 disabled:bg-gray-50"
                        >
                            {CRITICITES.map(c => (
                                <option key={c.value} value={c.value} className={c.color}>
                                    {c.label}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Description du problème */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Description du problème *</label>
                    <textarea
                        name="description_probleme"
                        value={formData.description_probleme}
                        onChange={handleChange}
                        required
                        disabled={isViewMode}
                        rows={4}
                        className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none disabled:opacity-75 disabled:bg-gray-50"
                        placeholder="Décrivez le problème en détail..."
                    />
                </div>

                {/* Analyse & Action (Optional/Edit) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Cause Racine (Optionnel)</label>
                        <textarea
                            name="cause_racine"
                            value={formData.cause_racine}
                            onChange={handleChange}
                            disabled={isViewMode}
                            rows={3}
                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none disabled:opacity-75 disabled:bg-gray-50"
                            placeholder="5 Pourquoi..."
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Action Corrective (Optionnel)</label>
                        <textarea
                            name="action_corrective"
                            value={formData.action_corrective}
                            onChange={handleChange}
                            disabled={isViewMode}
                            rows={3}
                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none disabled:opacity-75 disabled:bg-gray-50"
                            placeholder="Action immédiate..."
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Responsable — Searchable Autocomplete */}
                    <div className="space-y-2" ref={dropdownRef}>
                        <label className="text-sm font-medium text-gray-700">Responsable Action *</label>
                        <div className="relative">
                            <input
                                type="text"
                                value={userSearch}
                                onChange={handleUserSearchChange}
                                onFocus={handleSearchFocus}
                                placeholder="Rechercher un utilisateur..."
                                autoComplete="off"
                                disabled={isViewMode}
                                className="w-full h-10 px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-75 disabled:bg-gray-50"
                            />
                            {isSearching && (
                                <div className="absolute right-3 top-2.5">
                                    <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                                </div>
                            )}

                            {/* Validation indicator */}
                            {formData.responsable && (
                                <div className="absolute right-3 top-2.5 text-green-500 text-sm">✓</div>
                            )}

                            {/* Dropdown results */}
                            {showDropdown && userResults.length > 0 && (
                                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                                    {userResults.map(user => (
                                        <button
                                            key={user.id}
                                            type="button"
                                            onClick={() => handleSelectUser(user)}
                                            className="w-full text-left px-4 py-2.5 hover:bg-red-50 transition-colors flex items-center justify-between border-b border-gray-50 last:border-0"
                                        >
                                            <span className="font-medium text-gray-800 text-sm">{user.username}</span>
                                            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${getRoleBadge(user.role)}`}>
                                                {user.role}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* No results message */}
                            {showDropdown === false && userSearch.length > 0 && !isSearching && !formData.responsable && userResults.length === 0 && (
                                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg px-4 py-3 text-sm text-gray-500">
                                    Aucun utilisateur trouvé
                                </div>
                            )}
                        </div>
                        {/* Helper text */}
                        <p className="text-xs text-gray-400">
                            Tapez un nom pour rechercher parmi les utilisateurs inscrits
                        </p>
                    </div>

                    {/* Deadline */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">Deadline *</label>
                        <input
                            type="date"
                            name="deadline"
                            value={formData.deadline}
                            onChange={handleChange}
                            required
                            disabled={isViewMode}
                            className="w-full h-10 px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-75 disabled:bg-gray-50"
                        />
                    </div>
                </div>

                {/* Footer Actions */}
                <div className="flex justify-end pt-4 space-x-3 border-t border-gray-100">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                        {isViewMode ? "Fermer" : "Annuler"}
                    </button>
                    {!isViewMode && (
                        <button
                            type="submit"
                            disabled={isSaving}
                            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isSaving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                            Enregistrer
                        </button>
                    )}
                </div>
            </form>
        </Modal>
    );
};

export default IncidentModal;
