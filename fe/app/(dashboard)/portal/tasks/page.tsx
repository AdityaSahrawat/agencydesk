"use client";

import { useAuth } from "@/providers/auth-provider";
import { useProjectsForClient, useTasks } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { SearchBar } from "@/components/shared/search-bar";
import { CheckSquare } from "lucide-react";
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS, PRIORITY_LABELS, PRIORITY_COLORS } from "@/lib/constants";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { TaskStatus, Priority, Project, Task } from "@/types";

export default function ClientTasksPage() {
    const { user } = useAuth();
    const router = useRouter();
    const clientId = user?.clientId ?? "";
    const [search, setSearch] = useState("");

    const { data: projects } = useProjectsForClient(clientId);
    const { data: tasksData, isLoading } = useTasks({ pageSize: 1000, internal: false });

    const projectIds = (projects ?? []).map((p: Project) => p.id);
    const allTasks = (tasksData?.data ?? []).filter((t: Task) => projectIds.includes(t.projectId));
    const filtered = search
        ? allTasks.filter((t: Task) => t.title.toLowerCase().includes(search.toLowerCase()))
        : allTasks;

    return (
        <div>
            <Navbar title="My Tasks" subtitle="View all tasks across your projects" />
            <div className="space-y-4 p-6">
                <SearchBar value={search} onChange={setSearch} placeholder="Search tasks..." className="w-64" />

                {isLoading ? (
                    <div className="space-y-2">
                        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16 rounded-lg" />)}
                    </div>
                ) : filtered.length === 0 ? (
                    <EmptyState icon={CheckSquare} title="No tasks" description="No client-visible tasks found." />
                ) : (
                    <div className="space-y-2">
                        {filtered.map((t: Task) => {
                            const project = (projects ?? []).find((p: Project) => p.id === t.projectId);
                            return (
                                <Card key={t.id} className="cursor-pointer hover:bg-accent" onClick={() => router.push(`/portal/tasks/${t.id}`)}>
                                    <CardContent className="flex items-center justify-between p-4">
                                        <div className="flex items-center gap-3">
                                            <Badge className={TASK_STATUS_COLORS[t.status as TaskStatus]} variant="secondary">
                                                {TASK_STATUS_LABELS[t.status as TaskStatus]}
                                            </Badge>
                                            <div>
                                                <p className="font-medium">{t.title}</p>
                                                <p className="text-xs text-muted-foreground">{project?.name}</p>
                                            </div>
                                        </div>
                                        <Badge className={PRIORITY_COLORS[t.priority as Priority]} variant="secondary">
                                            {PRIORITY_LABELS[t.priority as Priority]}
                                        </Badge>
                                    </CardContent>
                                </Card>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
