"use client";

import { useAuth } from "@/providers/auth-provider";
import { useClientDashboardStats, useProjectsForClient, useTasks } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { StatCard } from "@/components/shared/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { FolderKanban, CheckCircle2, Clock, ListTodo, Eye } from "lucide-react";
import { PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS, TASK_STATUS_LABELS, TASK_STATUS_COLORS } from "@/lib/constants";
import Link from "next/link";
import type { TaskStatus, Task, Project } from "@/types";

export default function ClientDashboardPage() {
    const { user } = useAuth();
    const clientId = user?.clientId ?? "";

    const { data: stats, isLoading } = useClientDashboardStats(clientId);
    const { data: projects } = useProjectsForClient(clientId);
    const { data: tasksData } = useTasks({ pageSize: 1000, internal: false });

    const projects_ = projects ?? [];
    const allTasks = (tasksData?.data ?? []).filter((t: Task) =>
        projects_.some((p: Project) => p.id === t.projectId)
    );

    return (
        <div>
            <Navbar title="My Dashboard" subtitle={`Welcome, ${user?.name?.split(" ")[0]}`} />
            <div className="space-y-6 p-6">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {isLoading ? (
                        Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-lg" />)
                    ) : (
                        <>
                            <StatCard label="My Projects" value={stats?.totalProjects ?? 0} icon={FolderKanban} accent="blue" />
                            <StatCard label="Total Tasks" value={stats?.totalTasks ?? 0} icon={ListTodo} accent="default" />
                            <StatCard label="Completed" value={stats?.completedTasks ?? 0} icon={CheckCircle2} accent="green" />
                            <StatCard label="Hours Logged" value={`${stats?.totalHours ?? 0}h`} icon={Clock} accent="amber" />
                        </>
                    )}
                </div>

                {/* Projects */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">My Projects</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        {projects_.length === 0 ? (
                            <EmptyState icon={FolderKanban} title="No projects" description="Your agency hasn't created any projects for you yet." />
                        ) : (
                            projects_.map((p: Project) => {
                                const pTasks = allTasks.filter((t: Task) => t.projectId === p.id);
                                return (
                                    <Link key={p.id} href={`/portal/projects/${p.id}`}>
                                        <div className="flex items-center justify-between rounded-lg border border-border p-4 hover:bg-accent">
                                            <div>
                                                <p className="font-medium">{p.name}</p>
                                                <p className="mt-1 text-xs text-muted-foreground">{pTasks.length} tasks · {pTasks.filter((t: Task) => t.status === "done").length} completed</p>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Badge variant="outline" className="gap-1 border-blue-200 bg-blue-50 text-blue-700">
                                                    <Eye className="h-3 w-3" />
                                                    Client View
                                                </Badge>
                                                <Badge className={PROJECT_STATUS_COLORS[p.status]} variant="secondary">
                                                    {PROJECT_STATUS_LABELS[p.status]}
                                                </Badge>
                                            </div>
                                        </div>
                                    </Link>
                                );
                            })
                        )}
                    </CardContent>
                </Card>

                {/* Recent Tasks */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Recent Tasks</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        {allTasks.length === 0 ? (
                            <p className="py-8 text-center text-sm text-muted-foreground">No tasks</p>
                        ) : (
                            allTasks.slice(0, 5).map((t: Task) => (
                                <Link key={t.id} href={`/portal/tasks/${t.id}`}>
                                    <div className="flex items-center justify-between rounded-lg border border-border p-3 hover:bg-accent">
                                        <div className="flex items-center gap-3">
                                            <Badge className={TASK_STATUS_COLORS[t.status as TaskStatus]} variant="secondary">
                                                {TASK_STATUS_LABELS[t.status as TaskStatus]}
                                            </Badge>
                                            <span className="font-medium">{t.title}</span>
                                        </div>
                                        <span className="text-xs text-muted-foreground">{t.dueDate ?? ""}</span>
                                    </div>
                                </Link>
                            ))
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
