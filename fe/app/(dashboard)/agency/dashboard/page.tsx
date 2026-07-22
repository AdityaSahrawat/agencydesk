"use client";

import { useAuth } from "@/providers/auth-provider";
import { useDashboardStats, useProjects, useTasks } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { StatCard } from "@/components/shared/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FolderKanban, CheckCircle2, Clock, Building2, TrendingUp, ListTodo } from "lucide-react";
import { PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS, TASK_STATUS_LABELS, TASK_STATUS_COLORS, PRIORITY_COLORS, PRIORITY_LABELS } from "@/lib/constants";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import type { TaskStatus, Priority, Task, Project } from "@/types";

export default function DashboardPage() {
    const { user } = useAuth();
    const agencyId = user?.agencyId ?? "";
    const { data: stats, isLoading: statsLoading } = useDashboardStats(agencyId);
    const { data: projectsData } = useProjects(agencyId, { pageSize: 5 });
    const { data: tasksData } = useTasks({ pageSize: 5 });

    const recentProjects = projectsData?.data ?? [];
    const recentTasks = tasksData?.data ?? [];

    const taskStatusCounts = recentTasks.reduce(
        (acc: Record<TaskStatus, number>, t: Task) => { acc[t.status] = (acc[t.status] ?? 0) + 1; return acc; },
        {} as Record<TaskStatus, number>
    );

    return (
        <div>
            <Navbar title="Dashboard" subtitle={`Welcome back, ${user?.name?.split(" ")[0]}`} />

            <div className="space-y-6 p-6">
                {/* Stats */}
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {statsLoading ? (
                        Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-lg" />)
                    ) : (
                        <>
                            <StatCard label="Total Projects" value={stats?.totalProjects ?? 0} icon={FolderKanban} accent="blue" />
                            <StatCard label="Total Tasks" value={stats?.totalTasks ?? 0} icon={ListTodo} accent="default" />
                            <StatCard label="Completed Tasks" value={stats?.completedTasks ?? 0} icon={CheckCircle2} accent="green" />
                            <StatCard label="Hours Logged" value={`${stats?.totalHours ?? 0}h`} icon={Clock} accent="amber" />
                        </>
                    )}
                </div>

                <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                    {/* Recent Projects */}
                    <Card className="lg:col-span-2">
                        <CardHeader className="flex flex-row items-center justify-between">
                            <CardTitle className="text-base">Recent Projects</CardTitle>
                            <Link href="/projects" className="text-sm text-primary hover:underline">View all</Link>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {recentProjects.length === 0 ? (
                                <p className="py-8 text-center text-sm text-muted-foreground">No projects yet</p>
                            ) : (
                                recentProjects.map((p: Project) => (
                                    <Link
                                        key={p.id}
                                        href={`/projects/${p.id}`}
                                        className="flex items-center justify-between rounded-lg border border-border p-3 hover:bg-accent"
                                    >
                                        <div>
                                            <p className="font-medium">{p.name}</p>
                                            <p className="text-xs text-muted-foreground">{p.description.slice(0, 60)}</p>
                                        </div>
                                        <Badge className={PROJECT_STATUS_COLORS[p.status]} variant="secondary">
                                            {PROJECT_STATUS_LABELS[p.status]}
                                        </Badge>
                                    </Link>
                                ))
                            )}
                        </CardContent>
                    </Card>

                    {/* Task Distribution */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Task Distribution</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {(Object.keys(TASK_STATUS_LABELS) as TaskStatus[]).map((status) => (
                                <div key={status} className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Badge className={TASK_STATUS_COLORS[status]} variant="secondary">
                                            {TASK_STATUS_LABELS[status]}
                                        </Badge>
                                    </div>
                                    <span className="text-lg font-semibold">{taskStatusCounts[status] ?? 0}</span>
                                </div>
                            ))}
                            <div className="border-t border-border pt-4">
                                <div className="flex items-center gap-2 text-sm">
                                    <TrendingUp className="h-4 w-4 text-green-600" />
                                    <span className="text-muted-foreground">Active Projects: {stats?.activeProjects ?? 0}</span>
                                </div>
                                <div className="mt-2 flex items-center gap-2 text-sm">
                                    <Building2 className="h-4 w-4 text-blue-600" />
                                    <span className="text-muted-foreground">Total Clients: {stats?.totalClients ?? 0}</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Recent Tasks */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-base">Recent Tasks</CardTitle>
                        <Link href="/projects" className="text-sm text-primary hover:underline">View all</Link>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {recentTasks.length === 0 ? (
                                <p className="py-8 text-center text-sm text-muted-foreground">No tasks yet</p>
                            ) : (
                                recentTasks.map((t: Task) => (
                                    <Link
                                        key={t.id}
                                        href={`/tasks/${t.id}`}
                                        className="flex items-center justify-between rounded-lg border border-border p-3 hover:bg-accent"
                                    >
                                        <div className="flex items-center gap-3">
                                            <Badge className={TASK_STATUS_COLORS[t.status]} variant="secondary">
                                                {TASK_STATUS_LABELS[t.status]}
                                            </Badge>
                                            <span className="font-medium">{t.title}</span>
                                            {t.internal && (
                                                <Badge variant="outline" className="border-amber-200 bg-amber-50 text-amber-700">Internal</Badge>
                                            )}
                                        </div>
                                        <Badge className={PRIORITY_COLORS[t.priority as Priority]} variant="secondary">
                                            {PRIORITY_LABELS[t.priority as Priority]}
                                        </Badge>
                                    </Link>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
