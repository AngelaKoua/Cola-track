"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "@/lib/dynamicCharts"

const data = [
    { time: "08:00", temp: 24, pressure: 1013, energy: 45 },
    { time: "09:00", temp: 25, pressure: 1015, energy: 52 },
    { time: "10:00", temp: 26, pressure: 1012, energy: 48 },
    { time: "11:00", temp: 28, pressure: 1018, energy: 60 },
    { time: "12:00", temp: 27, pressure: 1016, energy: 55 },
    { time: "13:00", temp: 29, pressure: 1020, energy: 65 },
    { time: "14:00", temp: 30, pressure: 1019, energy: 70 },
]

export function MainChart() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Performance de Production</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                            data={data}
                            margin={{
                                top: 5,
                                right: 30,
                                left: 20,
                                bottom: 5,
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                            <XAxis
                                dataKey="time"
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <YAxis
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => `${value}`}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #f0f0f0' }}
                                itemStyle={{ fontSize: '12px' }}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="temp"
                                name="Température (°C)"
                                stroke="#E41E26"
                                strokeWidth={2}
                                dot={false}
                                activeDot={{ r: 6 }}
                            />
                            <Line
                                type="monotone"
                                dataKey="pressure"
                                name="Pression (hPa)"
                                stroke="#1976D2"
                                strokeWidth={2}
                                dot={false}
                            />
                            <Line
                                type="monotone"
                                dataKey="energy"
                                name="Énergie (kWh)"
                                stroke="#2ECC71"
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    )
}
