"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { useAuth } from "@/context/AuthContext"
import { profileApi } from "@/lib/api"
import {
    User,
    Shield,
    Lock,
    Eye,
    EyeOff,
    Check,
    X,
    Calendar,
    Clock,
    Hash,
    AlertTriangle,
    Save,
    Mail,
    Phone,
    Briefcase,
    Info,
    Download
} from "lucide-react"

// ── Password validation rules ───────────────────────────────────────
const PASSWORD_RULES = [
    { id: "length", label: "8 caractères minimum", test: (v: string) => v.length >= 8 },
    { id: "upper", label: "1 lettre majuscule", test: (v: string) => /[A-Z]/.test(v) },
    { id: "digit", label: "1 chiffre", test: (v: string) => /\d/.test(v) },
    { id: "special", label: "1 caractère spécial", test: (v: string) => /[^A-Za-z0-9]/.test(v) },
]

export default function ProfilePage() {
    const { user } = useAuth()

    // ── Personal info state ─────────────────────────────────────────
    const [personalInfo, setPersonalInfo] = useState({
        lastName: "",
        firstName: "",
        email: "",
        phone: "",
        function: "",
    })
    const [personalSaved, setPersonalSaved] = useState(false)

    // ── Security state ──────────────────────────────────────────────
    const [passwords, setPasswords] = useState({
        current: "",
        newPassword: "",
        confirm: "",
    })
    const [showPasswords, setShowPasswords] = useState({
        current: false,
        newPassword: false,
        confirm: false,
    })
    const [passwordSaved, setPasswordSaved] = useState(false)
    const [passwordError, setPasswordError] = useState("")

    // ── Helpers ─────────────────────────────────────────────────────
    const getInitials = (name: string) =>
        name
            .split(" ")
            .map((p) => p[0])
            .join("")
            .toUpperCase()
            .slice(0, 2)

    const formatRole = (role: string) => {
        const map: Record<string, string> = {
            manager: "Manager Production",
            technician: "Technicien Sur Site",
        }
        return map[role] || role
    }

    // Simulated system info (will come from backend later)
    const systemInfo = useMemo(
        () => ({
            username: user?.username || "—",
            role: user?.role ? formatRole(user.role) : "—",
            lastLogin: new Date().toLocaleDateString("fr-FR", {
                day: "numeric",
                month: "long",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            }),
            createdAt: "15 janvier 2025",
            totalLogins: 47,
        }),
        [user]
    )

    // Password validation
    const passwordValidation = useMemo(
        () => PASSWORD_RULES.map((r) => ({ ...r, valid: r.test(passwords.newPassword) })),
        [passwords.newPassword]
    )
    const allPasswordRulesValid = passwordValidation.every((r) => r.valid)
    const passwordsMatch = passwords.newPassword === passwords.confirm && passwords.confirm.length > 0

    // ── Handlers ────────────────────────────────────────────────────
    const handlePersonalSave = () => {
        setPersonalSaved(true)
        setTimeout(() => setPersonalSaved(false), 3000)
    }

    const handlePasswordChange = async () => {
        setPasswordError("")
        if (!passwords.current) {
            setPasswordError("Veuillez saisir votre mot de passe actuel.")
            return
        }
        if (!allPasswordRulesValid) {
            setPasswordError("Le nouveau mot de passe ne respecte pas toutes les règles.")
            return
        }
        if (!passwordsMatch) {
            setPasswordError("Les mots de passe ne correspondent pas.")
            return
        }

        try {
            if (!user?.userId) {
                setPasswordError("Utilisateur non identifié.")
                return
            }
            await profileApi.changePassword(user.userId, {
                current_password: passwords.current,
                new_password: passwords.newPassword
            })
            setPasswordSaved(true)
            setPasswords({ current: "", newPassword: "", confirm: "" })
            setTimeout(() => setPasswordSaved(false), 3000)
        } catch (error: any) {
            setPasswordError(error.message || "Erreur lors de la modification du mot de passe.")
        }
    }

    // ── Role badge styling ──────────────────────────────────────────
    const roleBadge = user?.role === "manager"
        ? "bg-blue-100 text-blue-700 border-blue-200"
        : "bg-emerald-100 text-emerald-700 border-emerald-200"

    return (
        <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 animate-fade-in-up">
            {/* ═══════════════════════════════════════════════════════════
                PAGE HEADER
               ═══════════════════════════════════════════════════════════ */}
            <div>
                <h1 className="text-2xl font-semibold text-slate-900">Mon Compte</h1>
                <p className="text-sm text-slate-500 mt-1">
                    Gestion de votre identité et paramètres de sécurité
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* ═══════════════════════════════════════════════════════════
                    LEFT COLUMN: IDENTITÉ & RÉSUMÉ (4 columns)
                   ═══════════════════════════════════════════════════════════ */}
                <div className="lg:col-span-4 space-y-6">
                    {/* 1. EXECUTIVE ID CARD */}
                    <div className="rounded-2xl overflow-hidden shadow-sm border border-slate-200 bg-white transition-all hover:shadow-md">
                        {/* Banner */}
                        <div className="h-24 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-white/5 via-transparent to-white/5" />
                        </div>

                        {/* Content */}
                        <div className="px-6 pb-6 relative">
                            {/* Avatar + Identity (Zone 1) */}
                            <div className="flex flex-col items-center -mt-12 text-center pb-6 border-b border-slate-200/60">
                                <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-700 flex items-center justify-center text-white text-3xl font-bold shadow-lg ring-4 ring-white mb-4">
                                    {user?.username ? getInitials(user.username) : <User className="h-10 w-10" />}
                                </div>
                                <h2 className="text-xl font-bold text-slate-900 capitalize">
                                    {user?.username || "Invité"}
                                </h2>
                                <p className="text-sm text-slate-500 font-medium mt-1">
                                    {user?.role ? formatRole(user.role) : "—"}
                                </p>
                            </div>

                            {/* System Meta (Zone 2) */}
                            <div className="py-4 border-b border-slate-200/60 space-y-3">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-slate-500">Statut</span>
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
                                        Actif
                                    </span>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-slate-500">Création</span>
                                    <span className="text-slate-900 font-medium">{systemInfo.createdAt}</span>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-slate-500">Rôle système</span>
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold border ${roleBadge}`}>
                                        {user?.role === 'manager' ? 'Admin' : 'Utilisateur'}
                                    </span>
                                </div>
                            </div>

                            {/* Actions (Zone 3) */}
                            <div className="pt-4">
                                <Button variant="outline" className="w-full text-sm text-slate-600 border-slate-200 hover:bg-slate-50">
                                    <Download className="h-4 w-4 mr-2" />
                                    Exporter mes données
                                </Button>
                            </div>
                        </div>
                    </div>

                    {/* 2. SYSTEM INFO (Mini Dashboard) */}
                    <div className="space-y-3">
                        <h3 className="text-xs uppercase tracking-wider font-semibold text-slate-500 mb-2 px-1 flex items-center gap-2">
                            <Shield className="h-3.5 w-3.5" /> Audit d'activité
                        </h3>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="rounded-2xl bg-white border border-slate-200 p-4 hover:shadow-sm transition-all text-center">
                                <span className="block text-xs uppercase tracking-wider font-medium text-slate-400 mb-1">Connexions</span>
                                <span className="text-2xl font-semibold text-slate-900">{systemInfo.totalLogins}</span>
                            </div>
                            <div className="rounded-2xl bg-white border border-slate-200 p-4 hover:shadow-sm transition-all text-center flex flex-col justify-center">
                                <span className="block text-xs uppercase tracking-wider font-medium text-slate-400 mb-1">Activité</span>
                                <span className="text-xs font-medium text-slate-900">
                                    {systemInfo.lastLogin.split('à')[0].trim()}
                                </span>
                                <span className="text-[10px] text-slate-500 mt-0.5">
                                    à {systemInfo.lastLogin.split('à')[1]?.trim()}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ═══════════════════════════════════════════════════════════
                    RIGHT COLUMN: PARAMÈTRES & SÉCURITÉ (8 columns)
                   ═══════════════════════════════════════════════════════════ */}
                <div className="lg:col-span-8 space-y-8">

                    {/* 3. INFORMATIONS PERSONNELLES (Fiche Structurée) */}
                    <div className="rounded-2xl border border-slate-200/70 bg-white shadow-sm overflow-hidden flex flex-col transition-all hover:shadow-md">
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-semibold text-slate-900">Fiche collaborateur</h3>
                            </div>
                            <div className="hidden sm:block">
                                <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                                    <Briefcase className="h-5 w-5 text-slate-400" />
                                </div>
                            </div>
                        </div>

                        <div className="p-6 space-y-8 flex-1">
                            {/* Niveau 1 - Identité */}
                            <div className="space-y-5">
                                <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 border-b border-slate-100 pb-2">
                                    Identité professionnelle
                                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                    <div className="space-y-1.5 focus-within:relative z-10">
                                        <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Nom</label>
                                        <Input
                                            value={personalInfo.lastName}
                                            onChange={(e) => setPersonalInfo({ ...personalInfo, lastName: e.target.value })}
                                            className="rounded-xl bg-slate-50 border-slate-200 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                        />
                                    </div>
                                    <div className="space-y-1.5 focus-within:relative z-10">
                                        <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Prénom</label>
                                        <Input
                                            value={personalInfo.firstName}
                                            onChange={(e) => setPersonalInfo({ ...personalInfo, firstName: e.target.value })}
                                            className="rounded-xl bg-slate-50 border-slate-200 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                        />
                                    </div>
                                    <div className="space-y-1.5 md:col-span-2 focus-within:relative z-10">
                                        <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Fonction</label>
                                        <Input
                                            value={personalInfo.function}
                                            onChange={(e) => setPersonalInfo({ ...personalInfo, function: e.target.value })}
                                            className="rounded-xl bg-slate-50 border-slate-200 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Niveau 2 - Contact */}
                            <div className="space-y-5">
                                <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 border-b border-slate-100 pb-2">
                                    Coordonnées
                                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                    <div className="space-y-1.5 focus-within:relative z-10">
                                        <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Email professionnel</label>
                                        <Input
                                            type="email"
                                            value={personalInfo.email}
                                            onChange={(e) => setPersonalInfo({ ...personalInfo, email: e.target.value })}
                                            className="rounded-xl bg-slate-50 border-slate-200 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                        />
                                    </div>
                                    <div className="space-y-1.5 focus-within:relative z-10">
                                        <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Téléphone</label>
                                        <Input
                                            type="tel"
                                            value={personalInfo.phone}
                                            onChange={(e) => setPersonalInfo({ ...personalInfo, phone: e.target.value })}
                                            className="rounded-xl bg-slate-50 border-slate-200 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="p-5 bg-slate-50 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 mt-auto">
                            <div className="w-full sm:w-auto overflow-hidden">
                                {personalSaved && (
                                    <div className="inline-flex items-center gap-2 text-sm text-emerald-700 font-medium bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-2.5 animate-fade-in-up w-full sm:w-auto">
                                        <Check className="h-4 w-4 shrink-0" />
                                        Modifications sauvegardées
                                    </div>
                                )}
                            </div>
                            <Button
                                onClick={handlePersonalSave}
                                className="rounded-xl shadow-sm hover:shadow-md transition-all px-8 bg-slate-900 hover:bg-slate-800 text-white w-full sm:w-auto"
                            >
                                Mettre à jour vos informations
                            </Button>
                        </div>
                    </div>

                </div>
            </div>

            {/* 4. SÉCURITÉ (Bloc Premium Critique) */}
            <div className="rounded-2xl border border-amber-200/60 bg-white shadow-sm flex flex-col transition-all hover:shadow-md">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-semibold text-slate-900">Sécurité et Accès</h3>
                        <p className="text-sm text-slate-500 mt-0.5">Gestion de vos identifiants de connexion.</p>
                    </div>
                    <div className="hidden sm:block">
                        <div className="p-2 rounded-xl bg-amber-50 border border-amber-100 text-amber-600">
                            <Lock className="h-5 w-5" />
                        </div>
                    </div>
                </div>

                <div className="p-6 grid grid-cols-1 md:grid-cols-5 gap-8 flex-1">
                    {/* Colonne gauche : Champs password */}
                    <div className="md:col-span-3 space-y-6">
                        <div className="space-y-1.5 focus-within:relative z-10">
                            <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Mot de passe actuel</label>
                            <div className="relative">
                                <Input
                                    type={showPasswords.current ? "text" : "password"}
                                    value={passwords.current}
                                    onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                                    className="rounded-xl bg-slate-50 border-slate-200 pr-10 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all font-mono"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPasswords({ ...showPasswords, current: !showPasswords.current })}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                                >
                                    {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </button>
                            </div>
                        </div>

                        <div className="space-y-1.5 focus-within:relative z-10">
                            <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Nouveau mot de passe</label>
                            <div className="relative">
                                <Input
                                    type={showPasswords.newPassword ? "text" : "password"}
                                    value={passwords.newPassword}
                                    onChange={(e) => setPasswords({ ...passwords, newPassword: e.target.value })}
                                    className="rounded-xl bg-slate-50 border-slate-200 pr-10 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all font-mono"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPasswords({ ...showPasswords, newPassword: !showPasswords.newPassword })}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                                >
                                    {showPasswords.newPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </button>
                            </div>
                        </div>

                        <div className="space-y-1.5 focus-within:relative z-10">
                            <label className="text-xs uppercase tracking-wide text-slate-500 font-medium">Confirmer le mot de passe</label>
                            <div className="relative border-b border-transparent">
                                <Input
                                    type={showPasswords.confirm ? "text" : "password"}
                                    value={passwords.confirm}
                                    onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                                    className={`rounded-xl bg-slate-50 border-slate-200 pr-10 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all font-mono ${passwords.confirm.length > 0 && !passwordsMatch ? "border-red-300 focus:border-red-500 focus:ring-red-500" : ""
                                        }`}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                                >
                                    {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </button>
                            </div>
                            {passwords.confirm.length > 0 && (
                                <div className="mt-2 pl-1">
                                    {!passwordsMatch ? (
                                        <p className="text-xs text-red-500 flex items-center gap-1.5 font-medium animate-fade-in-up">
                                            <X className="h-3 w-3" /> Mot de passe différent
                                        </p>
                                    ) : (
                                        <p className="text-xs text-emerald-600 flex items-center gap-1.5 font-medium animate-fade-in-up">
                                            <Check className="h-3 w-3" /> Correspondance validée
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>

                        {passwordError && (
                            <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-red-50 border border-red-100 text-red-700 text-sm animate-fade-in-up">
                                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                                <span>{passwordError}</span>
                            </div>
                        )}
                    </div>

                    {/* Colonne droite : Règles */}
                    <div className="md:col-span-2 flex flex-col">
                        <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 h-full flex flex-col">
                            <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-700 mb-5 flex items-center gap-2">
                                Exigences
                            </h4>
                            <div className="space-y-3.5 flex-1">
                                {passwordValidation.map((rule) => {
                                    const isValid = passwords.newPassword.length > 0 && rule.valid;
                                    const isTyping = passwords.newPassword.length > 0;
                                    return (
                                        <div
                                            key={rule.id}
                                            className={`flex items-start gap-2.5 text-sm transition-colors duration-300 ${!isTyping ? "text-slate-500" :
                                                isValid ? "text-emerald-700 font-medium" : "text-slate-400"
                                                }`}
                                        >
                                            <div className="mt-0.5 shrink-0">
                                                {isValid ? (
                                                    <Check className="h-4 w-4 text-emerald-600" />
                                                ) : (
                                                    <div className="h-1.5 w-1.5 rounded-full bg-slate-300 m-[5px] mt-[6px]" />
                                                )}
                                            </div>
                                            <span className="leading-tight">{rule.label}</span>
                                        </div>
                                    )
                                })}
                            </div>
                            <div className="mt-6 pt-5 border-t border-slate-200/60">
                                <p className="text-[11px] text-slate-500 uppercase tracking-wide font-medium">
                                    ℹ️ Reconnexion requise après modification.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="p-5 bg-slate-50 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 mt-auto">
                    <div className="w-full sm:w-auto overflow-hidden">
                        {passwordSaved && (
                            <div className="inline-flex items-center gap-2 text-sm text-emerald-700 font-medium bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-2.5 animate-fade-in-up w-full sm:w-auto">
                                <Check className="h-4 w-4 shrink-0" />
                                Mot de passe modifié avec succès
                            </div>
                        )}
                    </div>
                    <Button
                        onClick={handlePasswordChange}
                        disabled={!allPasswordRulesValid || !passwordsMatch || !passwords.current}
                        className="bg-amber-600 hover:bg-amber-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:border-slate-200 text-white rounded-xl shadow-sm hover:shadow-md transition-all min-w-[200px] w-full sm:w-auto font-medium"
                    >
                        Modifier le mot de passe
                    </Button>
                </div>
            </div>
        </div>
    )
}
