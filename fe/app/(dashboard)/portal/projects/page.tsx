"use client";

import { useAuth } from "@/providers/auth-provider";
import { useProjectsForClient, useTasks } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { FolderKanban, CheckCircle2, ListTodo, Eye } from "lucide-react";
import { PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS } from "@/lib/constants";
import type { Project, Task } from "@/types";
import Link from "next/link";

export default function ClientProjectsPage() {
    const { user } = useAuth();
    const clientId = user?.clientId ?? "";
    const { data: projects, isLoading } = useProjectsForClient(clientId);
    const { data: tasksData } = useTasks({ pageSize: 1000, internal: false });

    const projects_ = projects ?? [];
    const allTasks = tasksData?.data ?? [];

    return (
        <div>
            <Navbar title="My Projects" subtitle="View your projects" />
            <div className="space-y-4 p-6">
                {isLoading ? (
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-40 rounded-lg" />)}
                    </div>
                ) : projects_.length === 0 ? (
                    <EmptyState icon={FolderKanban} title="No projects" description="Your agency hasn't created any projects for you yet." />
                ) : (
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {projects_.map((p: Project) => {
                            const pTasks = allTasks.filter((t: Task) => t.projectId === p.id);
                            return (
                                <Link key={p.id} href={`/portal/projects/${p.id}`}>
                                    <Card className="cursor-pointer hover:border-primary/40">
                                        <CardContent className="p-5">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <p className="font-semibold">{p.name}</p>
                                                </div>
                                                <Badge className={PROJECT_STATUS_COLORS[p.status]} variant="secondary">
                                                    {PROJECT_STATUS_LABELS[p.status]}
                                                </Badge>
                                            </div>
                                            <p className="mt-3 line-clamp-2 text-sm text-muted-foreground">{p.description}</p>
                                            <div className="mt-4 flex items-center gap-4 border-t border-border pt-3 text-xs text-muted-foreground">
                                                <span className="flex items-center gap-1">
                                                    <ListTodo className="h-3.5 w-3.5" />
                                                    {pTasks.length} tasks
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                                                    {pTasks.filter((t: Task) => t.status === "done").length} done
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <Eye className="h-3.5 w-3.5" />
                                                    Client View
                                                </span>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </Link>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
