"use client"

import { Button } from "@/components/ui/Button"
import { Edit2, Trash2 } from "lucide-react"

interface Column<T> {
    header: string
    accessorKey: keyof T
    render?: (value: any, item: T) => React.ReactNode
}

interface DataTableProps<T> {
    data: T[]
    columns: Column<T>[]
    onEdit: (item: T) => void
    onDelete: (item: T) => void
}

export function DataTable<T extends { id?: string }>({ data, columns, onEdit, onDelete }: DataTableProps<T>) {
    return (
        <div className="rounded-md border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 text-gray-700 uppercase">
                        <tr>
                            {columns.map((col, idx) => (
                                <th key={idx} className="px-6 py-3 font-medium">
                                    {col.header}
                                </th>
                            ))}
                            <th className="px-6 py-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {data.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length + 1} className="px-6 py-8 text-center text-gray-500">
                                    Aucune donnée disponible
                                </td>
                            </tr>
                        ) : (
                            data.map((item, rowIdx) => (
                                <tr key={item.id || rowIdx} className="hover:bg-gray-50">
                                    {columns.map((col, colIdx) => {
                                        const value = item[col.accessorKey]
                                        return (
                                            <td key={colIdx} className="px-6 py-4">
                                                {col.render ? col.render(value, item) : (value as React.ReactNode)}
                                            </td>
                                        )
                                    })}
                                    <td className="px-6 py-4 text-right space-x-2">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => onEdit(item)}
                                            className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                        >
                                            <Edit2 className="h-4 w-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => onDelete(item)}
                                            className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
