"use client";

import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { useProjectsForClient, useTasks } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ListTodo, CheckCircle2, Clock, Eye } from "lucide-react";
import { PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS, TASK_STATUS_LABELS, TASK_STATUS_COLORS, PRIORITY_LABELS, PRIORITY_COLORS } from "@/lib/constants";
import { EmptyState } from "@/components/shared/empty-state";
import type { TaskStatus, Priority, ProjectStatus, Project, Task } from "@/types";

export default function ClientProjectDetailPage() {
    const params = useParams();
    const router = useRouter();
    const { user } = useAuth();
    const clientId = user?.clientId ?? "";
    const projectId = params.id as string;

    const { data: projects, isLoading } = useProjectsForClient(clientId);
    const project = (projects ?? []).find((p: Project) => p.id === projectId);
    const { data: tasksData } = useTasks({ projectId, pageSize: 1000, internal: false });

    const tasks = tasksData?.data ?? [];

    if (isLoading) {
        return (
            <div>
                <Navbar title="Project" />
                <div className="space-y-4 p-6">
                    <Skeleton className="h-32 rounded-lg" />
                    <Skeleton className="h-64 rounded-lg" />
                </div>
            </div>
        );
    }

    if (!project) {
        return (
            <div>
                <Navbar title="Project Not Found" />
                <div className="p-6">
                    <EmptyState icon={ListTodo} title="Project not found" description="You may not have access to this project." />
                </div>
            </div>
        );
    }

    return (
        <div>
            <Navbar title={project.name} subtitle="Client View" />
            <div className="space-y-6 p-6">
                <Button variant="ghost" size="sm" onClick={() => router.push("/portal/projects")} className="mb-2">
                    <ArrowLeft className="mr-1 h-4 w-4" />
                    Back to Projects
                </Button>

                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-3">
                                    <h2 className="text-xl font-semibold">{project.name}</h2>
                                    <Badge className={PROJECT_STATUS_COLORS[project.status as ProjectStatus]} variant="secondary">
                                        {PROJECT_STATUS_LABELS[project.status as ProjectStatus]}
                                    </Badge>
                                </div>
                                <p className="mt-2 text-sm text-muted-foreground">{project.description}</p>
                            </div>
                            <Badge variant="outline" className="gap-1 border-blue-200 bg-blue-50 text-blue-700">
                                <Eye className="h-3 w-3" />
                                Client View
                            </Badge>
                        </div>

                        <div className="mt-5 grid grid-cols-3 gap-4 border-t border-border pt-4">
                            <div className="flex items-center gap-2 text-sm">
                                <ListTodo className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Total:</span>
                                <span className="font-medium">{tasks.length}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Clock className="h-4 w-4 text-blue-600" />
                                <span className="text-muted-foreground">In Progress:</span>
                                <span className="font-medium">{tasks.filter((t: Task) => t.status === "doing").length}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                                <span className="text-muted-foreground">Done:</span>
                                <span className="font-medium">{tasks.filter((t: Task) => t.status === "done").length}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader><CardTitle className="text-base">Tasks</CardTitle></CardHeader>
                    <CardContent className="space-y-2">
                        {tasks.length === 0 ? (
                            <EmptyState icon={ListTodo} title="No tasks" description="No client-visible tasks for this project." />
                        ) : (
                            tasks.map((t: Task) => (
                                <div
                                    key={t.id}
                                    className="flex items-center justify-between rounded-lg border border-border p-4 hover:bg-accent cursor-pointer"
                                    onClick={() => router.push(`/portal/tasks/${t.id}`)}
                                >
                                    <div className="flex items-center gap-3">
                                        <Badge className={TASK_STATUS_COLORS[t.status as TaskStatus]} variant="secondary">
                                            {TASK_STATUS_LABELS[t.status as TaskStatus]}
                                        </Badge>
                                        <div>
                                            <p className="font-medium">{t.title}</p>
                                            {t.dueDate && <p className="text-xs text-muted-foreground">Due {t.dueDate}</p>}
                                        </div>
                                    </div>
                                    <Badge className={PRIORITY_COLORS[t.priority as Priority]} variant="secondary">
                                        {PRIORITY_LABELS[t.priority as Priority]}
                                    </Badge>
                                </div>
                            ))
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
