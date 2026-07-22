"use client";

import { useAuth } from "@/providers/auth-provider";
import { useDashboardStats, useProjects, useTasks, useClients } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { StatCard } from "@/components/shared/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { FolderKanban, CheckCircle2, Clock, ListTodo, Building2 } from "lucide-react";
import { PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS, TASK_STATUS_LABELS, TASK_STATUS_COLORS, PRIORITY_LABELS, PRIORITY_COLORS } from "@/lib/constants";
import type { TaskStatus, Priority, ProjectStatus, Task, Project } from "@/types";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend,
} from "recharts";

const PIE_COLORS = ["#64748b", "#3b82f6", "#22c55e"];

export default function ReportsPage() {
    const { user } = useAuth();
    const agencyId = user?.agencyId ?? "";
    const { data: stats, isLoading } = useDashboardStats(agencyId);
    const { data: projectsData } = useProjects(agencyId, { pageSize: 1000 });
    const { data: tasksData } = useTasks({ pageSize: 1000 });
    const { data: clientsData } = useClients(agencyId, { pageSize: 1000 });

    const tasks = tasksData?.data ?? [];
    const projects = projectsData?.data ?? [];
    const clients = clientsData?.data ?? [];

    const statusData = (["todo", "doing", "done"] as TaskStatus[]).map((s) => ({
        name: TASK_STATUS_LABELS[s],
        count: tasks.filter((t: Task) => t.status === s).length,
    }));

    const priorityData = (["low", "medium", "high"] as Priority[]).map((p) => ({
        name: PRIORITY_LABELS[p],
        count: tasks.filter((t: Task) => t.priority === p).length,
    }));

    const projectStatusData = (["planning", "active", "on_hold", "completed"] as ProjectStatus[]).map((s) => ({
        name: PROJECT_STATUS_LABELS[s],
        count: projects.filter((p: Project) => p.status === s).length,
    }));

    const tasksPerProject = projects.map((p: Project) => ({
        name: p.name.length > 15 ? p.name.slice(0, 12) + "..." : p.name,
        tasks: tasks.filter((t: Task) => t.projectId === p.id).length,
    }));

    return (
        <div>
            <Navbar title="Reports" subtitle="Agency performance overview" />
            <div className="space-y-6 p-6">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {isLoading ? (
                        Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-lg" />)
                    ) : (
                        <>
                            <StatCard label="Total Clients" value={stats?.totalClients ?? 0} icon={Building2} accent="blue" />
                            <StatCard label="Total Projects" value={stats?.totalProjects ?? 0} icon={FolderKanban} accent="default" />
                            <StatCard label="Completed Tasks" value={stats?.completedTasks ?? 0} icon={CheckCircle2} accent="green" />
                            <StatCard label="Hours Logged" value={`${stats?.totalHours ?? 0}h`} icon={Clock} accent="amber" />
                        </>
                    )}
                </div>

                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                    {/* Task Status Distribution */}
                    <Card>
                        <CardHeader><CardTitle className="text-base">Task Status Distribution</CardTitle></CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={250}>
                                <PieChart>
                                    <Pie data={statusData} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                                        {statusData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                                    </Pie>
                                    <Tooltip />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Tasks per Project */}
                    <Card>
                        <CardHeader><CardTitle className="text-base">Tasks per Project</CardTitle></CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={250}>
                                <BarChart data={tasksPerProject}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                                    <Tooltip />
                                    <Bar dataKey="tasks" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Priority Distribution */}
                    <Card>
                        <CardHeader><CardTitle className="text-base">Priority Distribution</CardTitle></CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={250}>
                                <BarChart data={priorityData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                                    <Tooltip />
                                    <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Project Status */}
                    <Card>
                        <CardHeader><CardTitle className="text-base">Project Status Breakdown</CardTitle></CardHeader>
                        <CardContent className="space-y-3 pt-4">
                            {projectStatusData.map((d) => (
                                <div key={d.name} className="flex items-center justify-between">
                                    <span className="text-sm">{d.name}</span>
                                    <Badge variant="secondary">{d.count}</Badge>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
