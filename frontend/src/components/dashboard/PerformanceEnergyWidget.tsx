"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip } from "@/lib/dynamicCharts"

interface PerformanceData {
    time: string
    production: number
    target: number
    energy: number
}

const mockData: PerformanceData[] = [
    { time: "08:00", production: 85, target: 90, energy: 42 },
    { time: "09:00", production: 88, target: 90, energy: 45 },
    { time: "10:00", production: 92, target: 90, energy: 48 },
    { time: "11:00", production: 90, target: 90, energy: 46 },
    { time: "12:00", production: 85, target: 90, energy: 40 },
    { time: "13:00", production: 89, target: 90, energy: 44 },
    { time: "14:00", production: 94, target: 90, energy: 50 },
]

export function PerformanceEnergyWidget() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle className="text-[#1F2937]">Performance & Énergie</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    <div>
                        <div className="flex justify-between items-end mb-2">
                            <span className="text-sm font-medium text-gray-500">Production vs Objectif</span>
                            <span className="text-sm font-bold text-[#1F2937]">94%</span>
                        </div>
                        <div className="h-[80px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={mockData}>
                                    <defs>
                                        <linearGradient id="colorProd" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#2ECC71" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#2ECC71" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <Area
                                        type="monotone"
                                        dataKey="production"
                                        stroke="#2ECC71"
                                        fillOpacity={1}
                                        fill="url(#colorProd)"
                                        strokeWidth={2}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div>
                        <div className="flex justify-between items-end mb-2">
                            <span className="text-sm font-medium text-gray-500">Conso. Énergétique</span>
                            <span className="text-sm font-bold text-[#1F2937]">450 kWh</span>
                        </div>
                        <div className="h-[80px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={mockData}>
                                    <defs>
                                        <linearGradient id="colorEnergy" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#1976D2" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#1976D2" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <Area
                                        type="monotone"
                                        dataKey="energy"
                                        stroke="#1976D2"
                                        fillOpacity={1}
                                        fill="url(#colorEnergy)"
                                        strokeWidth={2}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
