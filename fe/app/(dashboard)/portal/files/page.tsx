"use client";

import { useAuth } from "@/providers/auth-provider";
import { useProjectsForClient, useTasks } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { Paperclip, FileText, Eye } from "lucide-react";
import type { Project, Task } from "@/types";
import { useRouter } from "next/navigation";

export default function ClientFilesPage() {
    const { user } = useAuth();
    const router = useRouter();
    const clientId = user?.clientId ?? "";

    const { data: projects, isLoading } = useProjectsForClient(clientId);
    const { data: tasksData } = useTasks({ pageSize: 1000, internal: false });

    const projectIds = (projects ?? []).map((p: Project) => p.id);
    const tasks = (tasksData?.data ?? []).filter((t: Task) => projectIds.includes(t.projectId));

    return (
        <div>
            <Navbar title="Files" subtitle="All files shared with you" />
            <div className="space-y-4 p-6">
                {isLoading ? (
                    <div className="space-y-2">
                        {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-lg" />)}
                    </div>
                ) : tasks.length === 0 ? (
                    <EmptyState icon={FileText} title="No files" description="No files have been shared with you yet." />
                ) : (
                    <div className="space-y-2">
                        {tasks.map((t: Task) => {
                            const project = (projects ?? []).find((p: Project) => p.id === t.projectId);
                            return (
                                <Card key={t.id} className="cursor-pointer hover:bg-accent" onClick={() => router.push(`/portal/tasks/${t.id}`)}>
                                    <CardContent className="flex items-center gap-3 p-4">
                                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                                            <Paperclip className="h-5 w-5 text-muted-foreground" />
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-medium">{t.title}</p>
                                            <p className="text-xs text-muted-foreground">{project?.name} · Click to view files</p>
                                        </div>
                                        <Badge variant="outline" className="gap-1 border-blue-200 bg-blue-50 text-blue-700">
                                            <Eye className="h-3 w-3" />
                                            Client View
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
