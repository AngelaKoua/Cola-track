"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { KPICard } from "@/components/dashboard/KPICard"
import { Zap, Droplets, Wind, Flame } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from "@/lib/dynamicCharts"

const energyMix = [
    { name: 'Électricité', value: 45, color: '#1976D2' },
    { name: 'Gaz Naturel', value: 30, color: '#FF9F43' },
    { name: 'Air Comprimé', value: 15, color: '#2ECC71' },
    { name: 'Vapeur', value: 10, color: '#E41E26' },
]

const consumptionData = [
    { name: 'Ligne 1', elec: 4000, air: 2400, water: 2400 },
    { name: 'Ligne 2', elec: 3000, air: 1398, water: 2210 },
    { name: 'Ligne 3', elec: 2000, air: 9800, water: 2290 },
    { name: 'Utilités', elec: 2780, air: 3908, water: 2000 },
]

export default function EnergyPage() {
    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-foreground">Performance Énergétique</h2>
                    <p className="text-gray-500">Suivi des consommations et optimisation des ressources.</p>
                </div>
            </div>

            {/* KPIs */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <KPICard
                    title="Électricité"
                    value="12,450 kWh"
                    icon={Zap}
                    trend="-2.5%"
                    trendUp={true}
                    description="Conso. journalière"
                    color="text-blue-500"
                />
                <KPICard
                    title="Eau Industrielle"
                    value="850 m³"
                    icon={Droplets}
                    trend="+1.2%"
                    trendUp={false}
                    description="Conso. journalière"
                    color="text-blue-400"
                />
                <KPICard
                    title="Air Comprimé"
                    value="4,200 Nm³"
                    icon={Wind}
                    trend="-0.8%"
                    trendUp={true}
                    description="Conso. journalière"
                    color="text-green-500"
                />
                <KPICard
                    title="Énergie Thermique"
                    value="3,100 kWh"
                    icon={Flame}
                    trend="+0.5%"
                    trendUp={false}
                    description="Vapeur & Eau chaude"
                    color="text-orange-500"
                />
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Consumption by Line */}
                <Card className="col-span-2">
                    <CardHeader>
                        <CardTitle>Consommation par Zone</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={consumptionData}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                                    <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        cursor={{ fill: '#f5f6fa' }}
                                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #f0f0f0' }}
                                    />
                                    <Legend />
                                    <Bar dataKey="elec" name="Électricité" fill="#1976D2" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="air" name="Air Comprimé" fill="#2ECC71" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="water" name="Eau" fill="#4FC3F7" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* Energy Mix */}
                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle>Mix Énergétique</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={energyMix}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {energyMix.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
