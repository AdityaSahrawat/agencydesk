import axios from "axios";
import { API_BASE_URL } from "@/lib/constants";
import type { Client, Project, Task, TaskFile, Comment, TimeEntry, User, PaginatedResponse } from "@/types";

const instance = axios.create({
    baseURL: API_BASE_URL.endsWith("/api/v1") ? API_BASE_URL : `${API_BASE_URL}/v1`,
    headers: {
        "Content-Type": "application/json",
    },
});

export function setAuthToken(token: string | null) {
    if (token) {
        instance.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
        delete instance.defaults.headers.common["Authorization"];
    }
}

export function setAgencyIdHeader(agencyId: string | null) {
    if (agencyId) {
        instance.defaults.headers.common["X-Agency-ID"] = agencyId;
    } else {
        delete instance.defaults.headers.common["X-Agency-ID"];
    }
}

export function clearAuth() {
    delete instance.defaults.headers.common["Authorization"];
    delete instance.defaults.headers.common["X-Agency-ID"];
}

// ── AUTH ──────────────────────────────────────────────────
export async function login(email: string, password: string) {
    const res = await instance.post("/auth/login", { email, password });
    return res.data; // { access_token, refresh_token, token_type }
}

export async function register(email: string, password: string, full_name?: string) {
    const res = await instance.post("/auth/register", { email, password, full_name });
    return res.data;
}

export async function getMe() {
    const res = await instance.get("/auth/me");
    return res.data; // { id, email, full_name, is_active, created_at, memberships: [...] }
}

// ── CLIENTS ───────────────────────────────────────────────
export async function getClients(agencyId: string, params: { search?: string; page?: number; pageSize?: number } = {}): Promise<PaginatedResponse<Client>> {
    const page = params.page || 1;
    const pageSize = params.pageSize || 100;
    const skip = (page - 1) * pageSize;
    
    let res;
    if (params.search) {
        res = await instance.get("/clients/search", { params: { q: params.search } });
    } else {
        res = await instance.get("/clients/", { params: { skip, limit: pageSize } });
    }

    const rawList = Array.isArray(res.data) ? res.data : (res.data.data || []);
    const items: Client[] = rawList.map((c: any) => ({
        id: c.id,
        agencyId: c.agency_id || agencyId,
        name: c.company_name || c.name,
        email: c.contact_email || c.email || "",
        contactPerson: c.name || c.contact_person || "",
        phone: c.contact_phone || c.phone,
        createdAt: c.created_at || new Date().toISOString(),
    }));

    return {
        data: items,
        total: items.length,
        page,
        pageSize,
    };
}

export async function createClient(data: { name: string; email?: string; contact_email?: string; contactPerson?: string; phone?: string; contact_phone?: string; agencyId?: string; company_name?: string }): Promise<Client> {
    const payload = {
        name: data.name || data.contactPerson || "",
        company_name: data.company_name || data.name,
        contact_email: data.contact_email || data.email || "",
        contact_phone: data.contact_phone || data.phone,
    };
    const res = await instance.post("/clients/", payload);
    const c = res.data;
    return {
        id: c.id,
        agencyId: c.agency_id || data.agencyId || "",
        name: c.company_name || c.name,
        email: c.contact_email,
        contactPerson: c.name,
        phone: c.contact_phone,
        createdAt: c.created_at,
    };
}

export async function updateClient(id: string, data: Partial<Client>): Promise<Client> {
    const payload: any = {};
    if (data.name) {
        payload.name = data.name;
        payload.company_name = data.name;
    }
    if (data.email) payload.contact_email = data.email;
    if (data.phone) payload.contact_phone = data.phone;

    const res = await instance.patch(`/clients/${id}`, payload);
    const c = res.data;
    return {
        id: c.id,
        agencyId: c.agency_id,
        name: c.company_name || c.name,
        email: c.contact_email,
        contactPerson: c.name,
        phone: c.contact_phone,
        createdAt: c.created_at,
    };
}

export async function deleteClient(id: string): Promise<void> {
    await instance.delete(`/clients/${id}`);
}

// ── PROJECTS ──────────────────────────────────────────────
function mapProject(p: any): Project {
    return {
        id: p.id,
        agencyId: p.agency_id,
        clientId: p.client_id,
        name: p.name,
        description: p.description || "",
        status: p.status || "active",
        members: (p.members || []).map((m: any) => ({
            userId: m.id || m.user_id,
            role: m.role || "agency_member",
        })),
        createdAt: p.created_at || new Date().toISOString(),
    };
}

export async function getProjects(agencyId: string, params: { clientId?: string; search?: string; status?: string; page?: number; pageSize?: number } = {}): Promise<PaginatedResponse<Project>> {
    const page = params.page || 1;
    const pageSize = params.pageSize || 100;
    const skip = (page - 1) * pageSize;

    let res;
    if (params.search) {
        res = await instance.get("/projects/search", { params: { q: params.search } });
    } else {
        res = await instance.get("/projects/", { params: { skip, limit: pageSize } });
    }

    let rawList: any[] = Array.isArray(res.data) ? res.data : (res.data.data || []);
    if (params.clientId) {
        rawList = rawList.filter((p: any) => p.client_id === params.clientId);
    }
    if (params.status && params.status !== "all") {
        rawList = rawList.filter((p: any) => p.status === params.status);
    }

    const items = rawList.map(mapProject);
    return {
        data: items,
        total: items.length,
        page,
        pageSize,
    };
}

export async function getProject(id: string): Promise<Project> {
    const res = await instance.get(`/projects/${id}`);
    return mapProject(res.data);
}

export async function getProjectsForClient(clientId: string): Promise<Project[]> {
    const res = await instance.get("/projects/", { params: { limit: 100 } });
    const rawList: any[] = Array.isArray(res.data) ? res.data : [];
    return rawList.filter((p: any) => p.client_id === clientId).map(mapProject);
}

export async function createProject(data: { name: string; description?: string; clientId: string; status?: string; agencyId?: string; members?: any[] }): Promise<Project> {
    const payload = {
        name: data.name,
        description: data.description,
        client_id: data.clientId,
        status: data.status || "planning",
    };
    const res = await instance.post("/projects/", payload);
    return mapProject(res.data);
}

export async function updateProject(id: string, data: Partial<Project>): Promise<Project> {
    const payload: any = {};
    if (data.name) payload.name = data.name;
    if (data.description !== undefined) payload.description = data.description;
    if (data.status) payload.status = data.status;

    const res = await instance.patch(`/projects/${id}`, payload);
    return mapProject(res.data);
}

export async function deleteProject(id: string): Promise<void> {
    await instance.delete(`/projects/${id}`);
}

// ── TASKS ─────────────────────────────────────────────────
function mapTask(t: any): Task {
    return {
        id: t.id,
        projectId: t.project_id,
        title: t.title,
        description: t.description || "",
        status: t.status || "todo",
        priority: t.priority || "medium",
        dueDate: t.due_date || t.dueDate,
        assigneeId: t.assigned_to || t.assigneeId,
        internal: Boolean(t.is_internal),
        createdAt: t.created_at || new Date().toISOString(),
        updatedAt: t.updated_at || new Date().toISOString(),
    };
}

export async function getTasks(params: { projectId?: string; assigneeId?: string; status?: string; priority?: string; internal?: boolean; page?: number; pageSize?: number } = {}): Promise<PaginatedResponse<Task>> {
    const page = params.page || 1;
    const pageSize = params.pageSize || 100;
    const skip = (page - 1) * pageSize;

    const queryParams: any = { skip, limit: pageSize };
    if (params.projectId) queryParams.project_id = params.projectId;
    if (params.assigneeId) queryParams.assigned_to = params.assigneeId;
    if (params.status && params.status !== "all") queryParams.task_status = params.status;

    const res = await instance.get("/tasks/", { params: queryParams });
    let rawList: any[] = Array.isArray(res.data) ? res.data : [];

    if (params.priority && params.priority !== "all") {
        rawList = rawList.filter((t: any) => t.priority === params.priority);
    }
    if (params.internal !== undefined) {
        rawList = rawList.filter((t: any) => Boolean(t.is_internal) === params.internal);
    }

    const items = rawList.map(mapTask);
    return {
        data: items,
        total: items.length,
        page,
        pageSize,
    };
}

export async function getTask(id: string): Promise<Task> {
    const res = await instance.get(`/tasks/${id}`);
    return mapTask(res.data);
}

export async function createTask(data: { projectId: string; title: string; description?: string; status?: string; priority?: string; dueDate?: string; assigneeId?: string; internal?: boolean }): Promise<Task> {
    const payload = {
        project_id: data.projectId,
        title: data.title,
        description: data.description,
        status: data.status || "todo",
        priority: data.priority || "medium",
        due_date: data.dueDate,
        assigned_to: data.assigneeId,
        is_internal: data.internal ?? false,
    };
    const res = await instance.post("/tasks/", payload);
    return mapTask(res.data);
}

export async function updateTask(id: string, data: Partial<Task>): Promise<Task> {
    const payload: any = {};
    if (data.title) payload.title = data.title;
    if (data.description !== undefined) payload.description = data.description;
    if (data.status) payload.status = data.status;
    if (data.priority) payload.priority = data.priority;
    if (data.dueDate !== undefined) payload.due_date = data.dueDate;
    if (data.assigneeId !== undefined) payload.assigned_to = data.assigneeId;
    if (data.internal !== undefined) payload.is_internal = data.internal;

    const res = await instance.patch(`/tasks/${id}`, payload);
    return mapTask(res.data);
}

export async function deleteTask(id: string): Promise<void> {
    await instance.delete(`/tasks/${id}`);
}

// ── COMMENTS ──────────────────────────────────────────────
export async function getComments(taskId: string): Promise<Comment[]> {
    const res = await instance.get(`/comments/task/${taskId}`);
    const rawList: any[] = Array.isArray(res.data) ? res.data : [];
    return rawList.map((c: any) => ({
        id: c.id,
        taskId: c.task_id,
        userId: c.author_id || c.user_id,
        userName: c.author?.full_name || c.author?.email || c.user_name || "User",
        content: c.content,
        internal: Boolean(c.is_internal),
        createdAt: c.created_at || new Date().toISOString(),
    }));
}

export async function createComment(data: { taskId: string; content: string; is_internal?: boolean; internal?: boolean; userId?: string; userName?: string }): Promise<Comment> {
    const payload = {
        task_id: data.taskId,
        content: data.content,
        is_internal: data.is_internal ?? data.internal ?? false,
    };
    const res = await instance.post("/comments/", payload);
    const c = res.data;
    return {
        id: c.id,
        taskId: c.task_id,
        userId: c.author_id,
        userName: c.author?.full_name || c.author?.email || data.userName || "User",
        content: c.content,
        internal: Boolean(c.is_internal),
        createdAt: c.created_at,
    };
}

export async function deleteComment(id: string): Promise<void> {
    await instance.delete(`/comments/${id}`);
}

// ── FILES ─────────────────────────────────────────────────
export async function getFiles(taskId: string, internal?: boolean): Promise<TaskFile[]> {
    const res = await instance.get(`/files/task/${taskId}`);
    let rawList: any[] = Array.isArray(res.data) ? res.data : [];
    if (internal !== undefined) {
        rawList = rawList.filter((f: any) => Boolean(f.is_internal) === internal);
    }
    return rawList.map((f: any) => ({
        id: f.id,
        taskId: f.task_id,
        name: f.filename,
        url: `${instance.defaults.baseURL}/files/${f.id}/download`,
        mimeType: f.content_type || "application/octet-stream",
        size: f.file_size || 0,
        uploaderId: f.uploader_id,
        uploaderName: f.uploader?.full_name || f.uploader?.email || "User",
        visibility: f.is_internal ? "internal" : "client_visible",
        approvalStatus: f.approval_status || "pending",
        createdAt: f.created_at || new Date().toISOString(),
    }));
}

export async function uploadFile(data: { taskId: string; file?: File; isInternal?: boolean; name?: string; url?: string; mimeType?: string; size?: number; visibility?: any; approvalStatus?: any; uploaderId?: string; uploaderName?: string }): Promise<TaskFile> {
    const formData = new FormData();
    formData.append("task_id", data.taskId);
    formData.append("is_internal", data.isInternal ? "true" : "false");
    if (data.file) {
        formData.append("file", data.file);
    }

    const res = await instance.post("/files/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    const f = res.data;
    return {
        id: f.id,
        taskId: f.task_id,
        name: f.filename,
        url: `${instance.defaults.baseURL}/files/${f.id}/download`,
        mimeType: f.content_type || "application/octet-stream",
        size: f.file_size || 0,
        uploaderId: f.uploader_id,
        uploaderName: f.uploader?.full_name || f.uploader?.email || "User",
        visibility: f.is_internal ? "internal" : "client_visible",
        approvalStatus: f.approval_status || "pending",
        createdAt: f.created_at,
    };
}

export async function updateFileApproval(id: string, status: string): Promise<TaskFile> {
    const res = await instance.patch(`/files/${id}/approve`, { approval_status: status });
    const f = res.data;
    return {
        id: f.id,
        taskId: f.task_id,
        name: f.filename,
        url: `${instance.defaults.baseURL}/files/${f.id}/download`,
        mimeType: f.content_type,
        size: f.file_size,
        uploaderId: f.uploader_id,
        uploaderName: f.uploader?.full_name || f.uploader?.email || "User",
        visibility: f.is_internal ? "internal" : "client_visible",
        approvalStatus: f.approval_status,
        createdAt: f.created_at,
    };
}

export async function deleteFile(id: string): Promise<void> {
    await instance.delete(`/files/${id}`);
}

// ── TIME ENTRIES ──────────────────────────────────────────
export async function getTimeEntries(taskId: string): Promise<TimeEntry[]> {
    const res = await instance.get("/time-entries/", { params: { task_id: taskId } });
    const rawList: any[] = Array.isArray(res.data) ? res.data : [];
    return rawList.map((t: any) => ({
        id: t.id,
        taskId: t.task_id || taskId,
        userId: t.user_id,
        userName: t.user?.full_name || t.user?.email || "User",
        durationHours: t.duration_hours,
        date: t.entry_date || new Date().toISOString(),
        note: t.description || "",
        createdAt: t.created_at || new Date().toISOString(),
    }));
}

export async function createTimeEntry(data: { projectId?: string; taskId?: string; durationHours: number; date: string; note?: string; userId?: string; userName?: string }): Promise<TimeEntry> {
    const payload = {
        project_id: data.projectId || "",
        task_id: data.taskId,
        duration_hours: data.durationHours,
        entry_date: data.date,
        description: data.note,
    };
    const res = await instance.post("/time-entries/", payload);
    const t = res.data;
    return {
        id: t.id,
        taskId: t.task_id || data.taskId || "",
        userId: t.user_id,
        userName: t.user?.full_name || t.user?.email || data.userName || "User",
        durationHours: t.duration_hours,
        date: t.entry_date,
        note: t.description || "",
        createdAt: t.created_at,
    };
}

export async function deleteTimeEntry(id: string): Promise<void> {
    await instance.delete(`/time-entries/${id}`);
}

// ── USERS ─────────────────────────────────────────────────
export async function getUsers(agencyId: string): Promise<User[]> {
    const res = await instance.get("/users/members");
    const rawList: any[] = Array.isArray(res.data) ? res.data : [];
    return rawList.map((u: any) => ({
        id: u.id,
        email: u.email,
        name: u.full_name || u.email.split("@")[0],
        role: "agency_member",
        agencyId,
        createdAt: u.created_at || new Date().toISOString(),
    }));
}

export async function getProjectMembers(projectId: string): Promise<User[]> {
    const res = await instance.get(`/projects/${projectId}`);
    const members: any[] = res.data.members || [];
    return members.map((u: any) => ({
        id: u.id,
        email: u.email,
        name: u.full_name || u.email.split("@")[0],
        role: "agency_member",
        agencyId: res.data.agency_id || "",
        createdAt: u.created_at || new Date().toISOString(),
    }));
}

// ── DASHBOARD ─────────────────────────────────────────────
export interface DashboardStats {
    totalClients: number;
    activeProjects: number;
    totalProjects?: number;
    pendingTasks: number;
    totalTasks?: number;
    completedTasks?: number;
    totalHours?: number;
    totalHoursLogged: number;
}

export async function getDashboardStats(agencyId: string): Promise<DashboardStats> {
    const res = await instance.get("/dashboard/summary");
    const data = res.data;
    const totalProjects = data.active_projects || 0;
    const completedTasks = data.tasks_by_status?.done || 0;
    const totalTasks = (data.tasks_by_status?.todo || 0) + (data.tasks_by_status?.in_progress || 0) + (data.tasks_by_status?.review || 0) + completedTasks;
    const totalHours = data.total_hours_logged || 0;
    return {
        totalClients: data.total_clients || 0,
        activeProjects: totalProjects,
        totalProjects,
        pendingTasks: (data.tasks_by_status?.todo || 0) + (data.tasks_by_status?.in_progress || 0) + (data.tasks_by_status?.review || 0),
        totalTasks,
        completedTasks,
        totalHours,
        totalHoursLogged: totalHours,
    };
}

export async function getClientDashboardStats(clientId: string): Promise<{ totalProjects: number; totalTasks: number; completedTasks: number; totalHours: number }> {
    const res = await instance.get("/dashboard/summary");
    const data = res.data;
    return {
        totalProjects: data.active_projects || 0,
        totalTasks: (data.tasks_by_status?.todo || 0) + (data.tasks_by_status?.in_progress || 0) + (data.tasks_by_status?.review || 0) + (data.tasks_by_status?.done || 0),
        completedTasks: data.tasks_by_status?.done || 0,
        totalHours: data.total_hours_logged || 0,
    };
}
