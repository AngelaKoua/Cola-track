import React, { useState, useEffect } from 'react';
import { Incident } from '@/types/incident';
import { cn } from '@/lib/utils';
import { AlertCircle, Eye, Trash2, CheckCircle, ClipboardList } from 'lucide-react';
import { motion } from 'framer-motion';

interface IncidentTableProps {
    incidents: Incident[];
    isLoading: boolean;
    onView: (incident: Incident) => void;
    onResolve: (id: string) => void;
    onDelete: (id: string) => void;
}

const IncidentTable: React.FC<IncidentTableProps> = ({
    incidents,
    isLoading,
    onView,
    onResolve,
    onDelete
}) => {
    // 11️⃣ Légère animation fade-in de la table au mount
    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        // eslint-disable-next-line react-hooks/exhaustive-deps
        const timer = setTimeout(() => setMounted(true), 10);
        return () => clearTimeout(timer);
    }, []);

    const formatDate = (dateString: string) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
    };

    const formatDateLong = (dateString: string) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const formattingOptions: Intl.DateTimeFormatOptions = { day: '2-digit', month: '2-digit' };
    const formatCloture = (dateString: string) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('fr-FR', formattingOptions);
    }

    // 4️⃣ Harmonisation des Badges Criticité
    const getCriticiteColor = (criticite: string) => {
        switch (criticite) {
            case 'Critique': return 'text-rose-700 bg-rose-50 border-rose-200';
            case 'Élevé': return 'text-amber-700 bg-amber-50 border-amber-200';
            case 'Moyen': return 'text-yellow-700 bg-yellow-50 border-yellow-200';
            case 'Faible': return 'text-slate-600 bg-slate-100 border-slate-200';
            default: return 'text-slate-600 bg-slate-100 border-slate-200';
        }
    };

    // 5️⃣ Harmonisation Badges Statut
    const getStatutBadge = (statut: string) => {
        const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border";
        switch (statut) {
            case 'Ouvert': return <span className={`${baseClasses} bg-slate-100 text-slate-800 border-slate-200`}>Ouvert</span>;
            case 'En cours': return <span className={`${baseClasses} bg-amber-50 text-amber-700 border-amber-200`}>En cours</span>;
            case 'En attente': return <span className={`${baseClasses} bg-violet-50 text-violet-700 border-violet-200`}>En attente</span>;
            case 'Résolu': return <span className={`${baseClasses} bg-emerald-50 text-emerald-700 border-emerald-200`}>Résolu</span>;
            default: return null;
        }
    };

    // 🔟 Loading State – Skeleton Professionnel
    if (isLoading) {
        return (
            <div className="w-full bg-white/90 backdrop-blur-sm border border-slate-200/70 rounded-2xl shadow-xl overflow-hidden p-4 space-y-4">
                {/* Header skeleton */}
                <div className="flex gap-4 mb-6 px-2">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={`th-${i}`} className="h-4 bg-slate-200/60 rounded flex-1 animate-pulse"></div>
                    ))}
                </div>
                {/* Rows skeleton */}
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={`row-${i}`} className="flex gap-4 items-center px-2 py-3 bg-slate-50 border-b border-slate-100 rounded-xl">
                        <div className="h-10 bg-slate-200/60 rounded-lg w-[120px] animate-pulse"></div>
                        <div className="h-10 bg-slate-200/60 rounded-lg w-[150px] animate-pulse"></div>
                        <div className="h-10 bg-slate-200/60 rounded-lg w-[100px] animate-pulse"></div>
                        <div className="h-10 bg-slate-200/60 rounded-lg flex-1 animate-pulse"></div>
                        <div className="h-10 bg-slate-200/60 rounded-lg w-[120px] animate-pulse"></div>
                        <div className="h-10 bg-slate-200/60 rounded-lg w-[100px] animate-pulse"></div>
                    </div>
                ))}
            </div>
        );
    }

    // 9️⃣ Empty State – Version Premium
    if (incidents.length === 0) {
        return (
            <div className="w-full h-72 flex flex-col items-center justify-center space-y-3 text-slate-500 bg-white border border-slate-200 rounded-2xl shadow-sm">
                <ClipboardList className="h-16 w-16 text-slate-300 mb-2" strokeWidth={1.5} />
                <h3 className="text-lg font-medium text-slate-700">Aucun incident trouvé</h3>
                <p className="text-sm text-slate-500 text-center max-w-md">Modifiez les filtres ou enregistrez un nouvel incident pour voir les données apparaitre ici.</p>
            </div>
        );
    }

    // 2️⃣ Card Container – Niveau Enterprise
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: mounted ? 1 : 0, y: mounted ? 0 : 10 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="bg-white/90 backdrop-blur-sm border border-slate-200/70 rounded-2xl shadow-xl overflow-hidden"
        >
            {/* 11️⃣ Scroll horizontal avec gradient shadow si overflow */}
            <div className="overflow-x-auto relative pb-2 pt-2 px-1">
                <table className="w-full text-left text-sm border-collapse">
                    {/* 3️⃣ Header Table – Plus Structuré */}
                    <thead className="bg-slate-50 border-b border-slate-300">
                        <tr>
                            <th className="px-6 py-4 uppercase tracking-wider text-xs text-slate-500 font-semibold w-[140px]">Date/ID</th>
                            <th className="px-6 py-4 uppercase tracking-wider text-xs text-slate-500 font-semibold">Ligne & Équipement</th>
                            <th className="px-6 py-4 uppercase tracking-wider text-xs text-slate-500 font-semibold">Type & Criticité</th>
                            <th className="px-6 py-4 uppercase tracking-wider text-xs text-slate-500 font-semibold max-w-[300px]">Problème</th>
                            <th className="px-6 py-4 uppercase tracking-wider text-xs text-slate-500 font-semibold text-center">Statut</th>
                            <th className="px-6 py-4 uppercase tracking-wider text-xs text-slate-500 font-semibold">Responsable</th>
                            <th className="px-6 py-4 uppercase tracking-wider text-xs text-slate-500 font-semibold text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {incidents.map((incident) => {
                            const isOverdue = new Date(incident.deadline) < new Date() && incident.statut !== 'Résolu';

                            return (
                                // 1️⃣ Lignes – Perception Premium
                                <tr
                                    key={incident.id}
                                    className="border-b border-slate-100 hover:bg-slate-50/80 transition-all duration-150 group hover:shadow-sm"
                                >
                                    {/* Date & ID */}
                                    <td className="px-6 py-4 align-top">
                                        <div className="flex flex-col">
                                            <span className="font-medium text-slate-900 group-hover:text-primary transition-colors">
                                                {formatDate(incident.date_declaration)}
                                            </span>
                                            <span className="text-xs text-slate-400 font-mono mt-0.5">
                                                {incident.id.slice(0, 8)}...
                                            </span>
                                        </div>
                                    </td>

                                    {/* Ligne & Equipement */}
                                    <td className="px-6 py-4 align-top">
                                        <div className="flex flex-col">
                                            <span className="text-slate-900 font-medium">
                                                {incident.equipement}
                                            </span>
                                            <span className="text-xs text-slate-500 mt-0.5">{incident.ligne}</span>
                                        </div>
                                    </td>

                                    {/* Type & Criticité */}
                                    <td className="px-6 py-4 align-top">
                                        <div className="flex flex-col items-start space-y-2">
                                            <span className="text-slate-700">{incident.type_incident}</span>
                                            <span className={cn(
                                                "inline-flex self-start items-center px-2 py-0.5 rounded text-[10px] font-semibold border uppercase tracking-wide",
                                                getCriticiteColor(incident.criticite)
                                            )}>
                                                {incident.criticite}
                                            </span>
                                        </div>
                                    </td>

                                    {/* Description */}
                                    <td className="px-6 py-4 max-w-[300px] align-top">
                                        <div className="text-slate-600 line-clamp-2 pr-4 leading-relaxed" title={incident.description_probleme}>
                                            {incident.description_probleme}
                                        </div>
                                    </td>

                                    {/* Statut & Résolution */}
                                    <td className="px-6 py-4 align-top text-center border-l border-r border-slate-50 bg-slate-50/30">
                                        <div className="flex flex-col items-center justify-center h-full space-y-2.5">
                                            {getStatutBadge(incident.statut)}

                                            {/* 8️⃣ Bouton “Marquer résolu” – Amélioration */}
                                            {incident.statut !== 'Résolu' && (
                                                <button
                                                    onClick={() => onResolve(incident.id)}
                                                    className="opacity-0 group-hover:opacity-100 transition-all duration-200 flex items-center justify-center text-xs text-emerald-600 hover:text-emerald-700 font-medium focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-emerald-500 rounded px-1 outline-none"
                                                >
                                                    <CheckCircle className="w-3.5 h-3.5 mr-1" />
                                                    Résoudre
                                                </button>
                                            )}
                                            {incident.statut === 'Résolu' && (
                                                <span className="text-[10px] text-emerald-600/80 flex items-center pt-1 font-medium">
                                                    Le {incident.date_cloture ? formatCloture(incident.date_cloture) : '-'}
                                                </span>
                                            )}
                                        </div>
                                    </td>

                                    {/* Responsable & Deadline */}
                                    <td className="px-6 py-4 align-top">
                                        <div className="flex flex-col">
                                            <div className="flex items-center text-slate-900 font-medium whitespace-nowrap">
                                                {incident.responsable}
                                            </div>
                                            {/* 6️⃣ Deadline – Signal Métier Plus Intelligent */}
                                            <div className={cn(
                                                "flex items-center text-xs mt-1.5 whitespace-nowrap",
                                                isOverdue ? "text-rose-600 font-semibold" : "text-slate-500"
                                            )}>
                                                {isOverdue && <AlertCircle className="w-3.5 h-3.5 mr-1.5 inline-block text-rose-500" />}
                                                {formatDateLong(incident.deadline)}
                                            </div>
                                        </div>
                                    </td>

                                    {/* 7️⃣ Actions – Niveau Enterprise */}
                                    <td className="px-6 py-4 align-top text-right">
                                        <div className="flex justify-end items-center space-x-2">
                                            <button
                                                onClick={() => onView(incident)}
                                                title="Voir"
                                                className="p-2 text-slate-500 hover:text-slate-800 rounded-lg border border-transparent hover:border-slate-200 hover:bg-slate-100 transition-all duration-150 focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:outline-none"
                                                aria-label="Voir l'incident"
                                            >
                                                <Eye className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => onDelete(incident.id)}
                                                title="Supprimer"
                                                className="p-2 text-slate-400 hover:text-rose-600 rounded-lg border border-transparent hover:border-rose-100 hover:bg-rose-50 transition-all duration-150 focus-visible:ring-2 focus-visible:ring-rose-400 focus-visible:outline-none"
                                                aria-label="Supprimer l'incident"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>

                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </motion.div>
    );
};

export default IncidentTable;
