"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/services/api";
import type { Client, Project, Task, TaskFile, Comment, TimeEntry, User, PaginatedResponse } from "@/types";

type TaskParams = {
    projectId?: string;
    projectIds?: string[];
    assigneeId?: string;
    status?: string;
    priority?: string;
    internal?: boolean;
    page?: number;
    pageSize?: number;
};

type ProjectParams = {
    clientId?: string;
    search?: string;
    status?: string;
    page?: number;
    pageSize?: number;
};

type ClientParams = {
    search?: string;
    page?: number;
    pageSize?: number;
};

// ── CLIENTS ────────────────────────────────────────
export function useClients(agencyId: string, params: ClientParams = {}) {
    return useQuery<PaginatedResponse<Client>>({
        queryKey: ["clients", agencyId, params],
        queryFn: () => api.getClients(agencyId, params),
        enabled: !!agencyId,
    });
}

export function useAllClients(agencyId: string) {
    return useQuery<PaginatedResponse<Client>>({
        queryKey: ["clients", agencyId, "all"],
        queryFn: () => api.getClients(agencyId, { pageSize: 500 }),
        enabled: !!agencyId,
    });
}

export function useCreateClient() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: Parameters<typeof api.createClient>[0]) => api.createClient(data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }),
    });
}

export function useUpdateClient() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<Client> }) =>
            api.updateClient(id, data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }),
    });
}

export function useDeleteClient() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => api.deleteClient(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }),
    });
}

// ── PROJECTS ───────────────────────────────────────
export function useProjects(agencyId: string, params: ProjectParams = {}) {
    return useQuery<PaginatedResponse<Project>>({
        queryKey: ["projects", agencyId, params],
        queryFn: () => api.getProjects(agencyId, params),
        enabled: !!agencyId,
    });
}

export function useAllProjects(agencyId: string) {
    return useQuery<PaginatedResponse<Project>>({
        queryKey: ["projects", agencyId, "all"],
        queryFn: () => api.getProjects(agencyId, { pageSize: 500 }),
        enabled: !!agencyId,
    });
}

export function useProject(id: string) {
    return useQuery<Project | null>({
        queryKey: ["project", id],
        queryFn: () => api.getProject(id),
        enabled: !!id,
    });
}

export function useProjectsForClient(clientId: string) {
    return useQuery<Project[]>({
        queryKey: ["projects", "client", clientId],
        queryFn: () => api.getProjectsForClient(clientId),
        enabled: !!clientId,
    });
}

export function useCreateProject() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: Parameters<typeof api.createProject>[0]) => api.createProject(data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
    });
}

export function useUpdateProject() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) =>
            api.updateProject(id, data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
    });
}

export function useDeleteProject() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => api.deleteProject(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
    });
}

// ── TASKS ──────────────────────────────────────────
export function useTasks(params: TaskParams = {}) {
    return useQuery<PaginatedResponse<Task>>({
        queryKey: ["tasks", params],
        queryFn: () => api.getTasks(params),
    });
}

export function useAllTasks(params: TaskParams = {}) {
    return useQuery<PaginatedResponse<Task>>({
        queryKey: ["tasks", "all", params],
        queryFn: () => api.getTasks({ pageSize: 500, ...params }),
    });
}

export function useTask(id: string) {
    return useQuery<Task | null>({
        queryKey: ["task", id],
        queryFn: () => api.getTask(id),
        enabled: !!id,
    });
}

export function useCreateTask() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: Parameters<typeof api.createTask>[0]) => api.createTask(data),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["tasks"] });
            qc.invalidateQueries({ queryKey: ["projectStats"] });
        },
    });
}

export function useUpdateTask() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<Task> }) =>
            api.updateTask(id, data),
        onSuccess: (_data: unknown, vars: { id: string; data: Partial<Task> }) => {
            qc.invalidateQueries({ queryKey: ["tasks"] });
            qc.invalidateQueries({ queryKey: ["task", vars.id] });
            qc.invalidateQueries({ queryKey: ["projectStats"] });
        },
    });
}

export function useDeleteTask() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => api.deleteTask(id),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["tasks"] });
            qc.invalidateQueries({ queryKey: ["projectStats"] });
        },
    });
}

// ── COMMENTS ───────────────────────────────────────
export function useComments(taskId: string) {
    return useQuery<Comment[]>({
        queryKey: ["comments", taskId],
        queryFn: () => api.getComments(taskId),
        enabled: !!taskId,
    });
}

export function useCreateComment() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: Parameters<typeof api.createComment>[0]) => api.createComment(data),
        onSuccess: (_d: unknown, vars: any) => qc.invalidateQueries({ queryKey: ["comments", vars.taskId] }),
    });
}

export function useDeleteComment() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, taskId }: { id: string; taskId: string }) =>
            api.deleteComment(id),
        onSuccess: (_d: unknown, vars: any) => qc.invalidateQueries({ queryKey: ["comments", vars.taskId] }),
    });
}

// ── FILES ───────────────────────────────────────────
export function useFiles(taskId: string, internal: boolean) {
    return useQuery<TaskFile[]>({
        queryKey: ["files", taskId, internal],
        queryFn: () => api.getFiles(taskId, internal),
        enabled: !!taskId,
    });
}

export function useUploadFile() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: Parameters<typeof api.uploadFile>[0]) => api.uploadFile(data),
        onSuccess: (_d: unknown, vars: any) =>
            qc.invalidateQueries({ queryKey: ["files", vars.taskId] }),
    });
}

export function useUpdateFileApproval() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, status, taskId }: { id: string; status: TaskFile["approvalStatus"]; taskId: string }) =>
            api.updateFileApproval(id, status),
        onSuccess: (_d: unknown, vars: any) =>
            qc.invalidateQueries({ queryKey: ["files", vars.taskId] }),
    });
}

export function useDeleteFile() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, taskId }: { id: string; taskId: string }) => api.deleteFile(id),
        onSuccess: (_d: unknown, vars: any) =>
            qc.invalidateQueries({ queryKey: ["files", vars.taskId] }),
    });
}

// ── TIME ENTRIES ────────────────────────────────────
export function useTimeEntries(taskId: string) {
    return useQuery<TimeEntry[]>({
        queryKey: ["timeEntries", taskId],
        queryFn: () => api.getTimeEntries(taskId),
        enabled: !!taskId,
    });
}

export function useCreateTimeEntry() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: Parameters<typeof api.createTimeEntry>[0]) => api.createTimeEntry(data),
        onSuccess: (_d: unknown, vars: any) => {
            if (vars?.taskId) {
                qc.invalidateQueries({ queryKey: ["timeEntries", vars.taskId] });
            }
        },
    });
}

export function useDeleteTimeEntry() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, taskId }: { id: string; taskId: string }) =>
            api.deleteTimeEntry(id),
        onSuccess: (_d: unknown, vars: any) =>
            qc.invalidateQueries({ queryKey: ["timeEntries", vars.taskId] }),
    });
}

// ── USERS ───────────────────────────────────────────
export function useUsers(agencyId: string) {
    return useQuery<User[]>({
        queryKey: ["users", agencyId],
        queryFn: () => api.getUsers(agencyId),
        enabled: !!agencyId,
    });
}

export function useProjectMembers(projectId: string) {
    return useQuery<User[]>({
        queryKey: ["projectMembers", projectId],
        queryFn: () => api.getProjectMembers(projectId),
        enabled: !!projectId,
    });
}

// ── DASHBOARD ───────────────────────────────────────
export function useDashboardStats(agencyId: string) {
    return useQuery<api.DashboardStats>({
        queryKey: ["dashboardStats", agencyId],
        queryFn: () => api.getDashboardStats(agencyId),
        enabled: !!agencyId,
    });
}

export function useClientDashboardStats(clientId: string) {
    return useQuery<{
        totalProjects: number;
        totalTasks: number;
        completedTasks: number;
        totalHours: number;
    }>({
        queryKey: ["clientDashboardStats", clientId],
        queryFn: () => api.getClientDashboardStats(clientId),
        enabled: !!clientId,
    });
}
