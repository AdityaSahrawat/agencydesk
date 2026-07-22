"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

export interface Column<T> {
    key: string;
    header: string;
    render?: (row: T) => ReactNode;
    className?: string;
}

interface DataTableProps<T> {
    columns: Column<T>[];
    data: T[];
    rowKey: (row: T) => string;
    onRowClick?: (row: T) => void;
    empty?: ReactNode;
}

export function DataTable<T>({ columns, data, rowKey, onRowClick, empty }: DataTableProps<T>) {
    if (data.length === 0 && empty) return <>{empty}</>;

    return (
        <div className="overflow-hidden rounded-lg border border-border">
            <table className="w-full text-sm">
                <thead className="border-b border-border bg-muted/50">
                    <tr>
                        {columns.map((col) => (
                            <th
                                key={col.key}
                                className={cn("px-4 py-3 text-left font-medium text-muted-foreground", col.className)}
                            >
                                {col.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row) => (
                        <tr
                            key={rowKey(row)}
                            onClick={() => onRowClick?.(row)}
                            className={cn(
                                "border-b border-border last:border-0",
                                onRowClick && "cursor-pointer hover:bg-muted/30"
                            )}
                        >
                            {columns.map((col) => (
                                <td key={col.key} className={cn("px-4 py-3", col.className)}>
                                    {col.render ? col.render(row) : (row as Record<string, ReactNode>)[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
