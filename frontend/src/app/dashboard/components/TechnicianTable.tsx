"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"

interface Technician {
    original_name: string
    intervention_count: number
    avg_efficiency: number
}

interface TechnicianTableProps {
    data: Technician[]
    title: string
}

export function TechnicianTable({ data, title }: TechnicianTableProps) {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>{title}</CardTitle>
                <CardDescription>Classement par efficacité moyenne</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b">
                            <tr>
                                <th className="px-4 py-3 font-medium">Technicien</th>
                                <th className="px-4 py-3 font-medium text-center">Interventions</th>
                                <th className="px-4 py-3 font-medium text-right">Efficacité Moy.</th>
                                <th className="px-4 py-3 font-medium text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {data.map((tech, index) => (
                                <tr key={tech.original_name} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-4 py-3 font-medium text-gray-900">
                                        {tech.original_name}
                                    </td>
                                    <td className="px-4 py-3 text-center text-gray-600">
                                        {tech.intervention_count}
                                    </td>
                                    <td className="px-4 py-3 text-right font-semibold">
                                        <span className={
                                            tech.avg_efficiency >= 90 ? "text-emerald-600" :
                                                tech.avg_efficiency >= 80 ? "text-amber-600" : "text-rose-600"
                                        }>
                                            {Number(tech.avg_efficiency).toFixed(1)}%
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-center">
                                        {index === 0 && <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800 border border-yellow-200">Top 1</span>}
                                        {index > 0 && tech.avg_efficiency < 85 && <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800 border border-red-200">Critique</span>}
                                        {index > 0 && tech.avg_efficiency >= 85 && <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 border border-green-200">OK</span>}
                                    </td>
                                </tr>
                            ))}
                            {data.length === 0 && (
                                <tr>
                                    <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                                        Aucune donnée disponible pour cette période.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    )
}
