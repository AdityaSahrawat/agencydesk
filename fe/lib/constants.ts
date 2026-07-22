import { TaskStatus, Priority, ProjectStatus, FileApprovalStatus, Role } from "@/types";

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
    todo: "To Do",
    doing: "In Progress",
    done: "Done",
};

export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
    todo: "bg-slate-100 text-slate-700",
    doing: "bg-blue-100 text-blue-700",
    done: "bg-green-100 text-green-700",
};

export const PRIORITY_LABELS: Record<Priority, string> = {
    low: "Low",
    medium: "Medium",
    high: "High",
};

export const PRIORITY_COLORS: Record<Priority, string> = {
    low: "bg-slate-100 text-slate-600",
    medium: "bg-amber-100 text-amber-700",
    high: "bg-red-100 text-red-700",
};

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
    planning: "Planning",
    active: "Active",
    on_hold: "On Hold",
    completed: "Completed",
};

export const PROJECT_STATUS_COLORS: Record<ProjectStatus, string> = {
    planning: "bg-slate-100 text-slate-700",
    active: "bg-green-100 text-green-700",
    on_hold: "bg-amber-100 text-amber-700",
    completed: "bg-blue-100 text-blue-700",
};

export const APPROVAL_LABELS: Record<FileApprovalStatus, string> = {
    pending: "Pending",
    approved: "Approved",
    needs_changes: "Needs Changes",
};

export const APPROVAL_COLORS: Record<FileApprovalStatus, string> = {
    pending: "bg-slate-100 text-slate-700",
    approved: "bg-green-100 text-green-700",
    needs_changes: "bg-red-100 text-red-700",
};

export const ROLE_LABELS: Record<Role, string> = {
    agency_admin: "Admin",
    agency_member: "Member",
    client_user: "Client",
};

export const ROLE_COLORS: Record<Role, string> = {
    agency_admin: "bg-blue-100 text-blue-700",
    agency_member: "bg-slate-100 text-slate-700",
    client_user: "bg-green-100 text-green-700",
};

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";
