"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { TaskStatus, Priority, ProjectStatus } from "@/types";

interface FilterBarProps {
    status?: string;
    priority?: string;
    onStatusChange?: (v: string) => void;
    onPriorityChange?: (v: string) => void;
    statusOptions?: { value: string; label: string }[];
    showPriority?: boolean;
}

const defaultStatusOptions = [
    { value: "all", label: "All Status" },
    { value: "planning", label: "Planning" },
    { value: "active", label: "Active" },
    { value: "on_hold", label: "On Hold" },
    { value: "completed", label: "Completed" },
];

const priorityOptions = [
    { value: "all", label: "All Priorities" },
    { value: "low", label: "Low" },
    { value: "medium", label: "Medium" },
    { value: "high", label: "High" },
];

export function FilterBar({
    status,
    priority,
    onStatusChange,
    onPriorityChange,
    statusOptions = defaultStatusOptions,
    showPriority = false,
}: FilterBarProps) {
    return (
        <div className="flex items-center gap-3">
            {onStatusChange && (
                <Select value={status ?? "all"} onValueChange={(v) => v !== null && onStatusChange(v)}>
                    <SelectTrigger className="w-40">
                        <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                        {statusOptions.map((o) => (
                            <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            )}
            {showPriority && onPriorityChange && (
                <Select value={priority ?? "all"} onValueChange={(v) => v !== null && onPriorityChange(v)}>
                    <SelectTrigger className="w-40">
                        <SelectValue placeholder="Priority" />
                    </SelectTrigger>
                    <SelectContent>
                        {priorityOptions.map((o) => (
                            <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            )}
        </div>
    );
}
