"use client"

import { Factory, Database, Globe } from "lucide-react"

export type EquipmentType = "all" | "osmoseur" | "remplisseuse"

interface EquipmentSelectorProps {
    selected: EquipmentType
    onChange: (equipment: EquipmentType) => void
}

export function EquipmentSelector({ selected, onChange }: EquipmentSelectorProps) {
    const options: Array<{ value: EquipmentType; label: string; Icon: typeof Globe }> = [
        { value: "all", label: "Global", Icon: Globe },
        { value: "osmoseur", label: "Osmoseur", Icon: Database },
        { value: "remplisseuse", label: "Remplisseuse", Icon: Factory }
    ]

    return (
        <div className="inline-flex items-center bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
            {options.map(({ value, label, Icon }) => {
                const isSelected = selected === value

                return (
                    <button
                        key={value}
                        onClick={() => onChange(value)}
                        className={`
                            flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all
                            ${isSelected
                                ? 'bg-emerald-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                            }
                            ${value !== "all" ? 'border-l border-gray-200' : ''}
                        `}
                    >
                        <Icon className="h-4 w-4" />
                        <span>{label}</span>
                    </button>
                )
            })}
        </div>
    )
}
