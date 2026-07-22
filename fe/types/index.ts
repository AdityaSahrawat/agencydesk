export type Role = "agency_admin" | "agency_member" | "client_user";

export type TaskStatus = "todo" | "doing" | "done";
export type Priority = "low" | "medium" | "high";
export type ProjectStatus = "planning" | "active" | "on_hold" | "completed";
export type FileApprovalStatus = "pending" | "approved" | "needs_changes";
export type Visibility = "internal" | "client_visible";

export interface User {
    id: string;
    email: string;
    name: string;
    role: Role;
    agencyId: string;
    clientId?: string;
    avatarUrl?: string;
    createdAt: string;
}

export interface Agency {
    id: string;
    name: string;
    createdAt: string;
}

export interface Client {
    id: string;
    agencyId: string;
    name: string;
    email: string;
    contactPerson: string;
    phone?: string;
    createdAt: string;
}

export interface ProjectMember {
    userId: string;
    role: Role;
}

export interface Project {
    id: string;
    agencyId: string;
    clientId: string;
    name: string;
    description: string;
    status: ProjectStatus;
    members: ProjectMember[];
    createdAt: string;
}

export interface Task {
    id: string;
    projectId: string;
    title: string;
    description: string;
    status: TaskStatus;
    priority: Priority;
    dueDate?: string;
    assigneeId?: string;
    internal: boolean;
    createdAt: string;
    updatedAt: string;
}

export interface Comment {
    id: string;
    taskId: string;
    userId: string;
    userName: string;
    content: string;
    internal: boolean;
    createdAt: string;
}

export interface TaskFile {
    id: string;
    taskId: string;
    name: string;
    url: string;
    mimeType: string;
    size: number;
    uploaderId: string;
    uploaderName: string;
    visibility: Visibility;
    approvalStatus: FileApprovalStatus;
    createdAt: string;
}

export interface TimeEntry {
    id: string;
    taskId: string;
    userId: string;
    userName: string;
    durationHours: number;
    date: string;
    note: string;
    createdAt: string;
}

export interface AuthResponse {
    token: string;
    user: User;
}

export interface PaginatedResponse<T> {
    data: T[];
    total: number;
    page: number;
    pageSize: number;
}
