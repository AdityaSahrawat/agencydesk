"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { useProjects, useClients, useCreateProject } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { SearchBar } from "@/components/shared/search-bar";
import { FilterBar } from "@/components/shared/filter-bar";
import { EmptyState } from "@/components/shared/empty-state";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, FolderKanban, Clock, CheckCircle2, ListTodo } from "lucide-react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTasks } from "@/hooks/use-api";
import { PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS } from "@/lib/constants";
import type { ProjectStatus, Client, Task, Project } from "@/types";

const projectSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().min(1, "Description is required"),
    clientId: z.string().min(1, "Client is required"),
    status: z.enum(["planning", "active", "on_hold", "completed"]),
});
type ProjectForm = z.infer<typeof projectSchema>;

export default function ProjectsPage() {
    const router = useRouter();
    const { user } = useAuth();
    const agencyId = user?.agencyId ?? "";
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("all");
    const [dialogOpen, setDialogOpen] = useState(false);

    const { data, isLoading } = useProjects(agencyId, { search, status });
    const { data: clientsData } = useClients(agencyId, { pageSize: 100 });
    const { data: tasksData } = useTasks({ pageSize: 1000 });
    const createMut = useCreateProject();

    const clients = clientsData?.data ?? [];
    const allTasks = tasksData?.data ?? [];

    const clientName = (id: string) => clients.find((c: Client) => c.id === id)?.name ?? "—";
    const taskStats = (projectId: string) => {
        const tasks = allTasks.filter((t: Task) => t.projectId === projectId);
        return {
            total: tasks.length,
            done: tasks.filter((t: Task) => t.status === "done").length,
        };
    };

    const { register, handleSubmit, reset, formState: { errors }, setValue, watch } = useForm<ProjectForm>({
        resolver: zodResolver(projectSchema),
        defaultValues: { status: "planning" },
    });

    const onSubmit = async (vals: ProjectForm) => {
        try {
            await createMut.mutateAsync({ ...vals, agencyId, members: [] });
            toast.success("Project created");
            setDialogOpen(false);
            reset({ name: "", description: "", clientId: "", status: "planning" });
        } catch {
            toast.error("Failed to create project");
        }
    };

    return (
        <div>
            <Navbar title="Projects" subtitle="Manage all agency projects" />
            <div className="space-y-4 p-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex flex-1 flex-wrap items-center gap-3">
                        <SearchBar value={search} onChange={setSearch} placeholder="Search projects..." className="w-64" />
                        <FilterBar status={status} onStatusChange={setStatus} />
                    </div>
                    <Button onClick={() => { reset({ name: "", description: "", clientId: "", status: "planning" }); setDialogOpen(true); }} size="sm">
                        <Plus className="mr-1 h-4 w-4" />
                        New Project
                    </Button>
                </div>

                {isLoading ? (
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-40 rounded-lg" />)}
                    </div>
                ) : (data?.data ?? []).length === 0 ? (
                    <EmptyState
                        icon={FolderKanban}
                        title="No projects found"
                        description="Create your first project to start tracking tasks and time."
                        actionLabel="New Project"
                        onAction={() => setDialogOpen(true)}
                    />
                ) : (
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {(data?.data ?? []).map((p: Project) => {
                            const stats = taskStats(p.id);
                            return (
                                <Card key={p.id} className="cursor-pointer hover:border-primary/40" onClick={() => router.push(`/projects/${p.id}`)}>
                                    <CardContent className="p-5">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <p className="font-semibold">{p.name}</p>
                                                <p className="mt-1 text-xs text-muted-foreground">{clientName(p.clientId)}</p>
                                            </div>
                                            <Badge className={PROJECT_STATUS_COLORS[p.status]} variant="secondary">
                                                {PROJECT_STATUS_LABELS[p.status]}
                                            </Badge>
                                        </div>
                                        <p className="mt-3 line-clamp-2 text-sm text-muted-foreground">{p.description}</p>
                                        <div className="mt-4 flex items-center gap-4 border-t border-border pt-3 text-xs text-muted-foreground">
                                            <span className="flex items-center gap-1">
                                                <ListTodo className="h-3.5 w-3.5" />
                                                {stats.total} tasks
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                                                {stats.done} done
                                            </span>
                                        </div>
                                    </CardContent>
                                </Card>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Create Project Dialog */}
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent className="max-w-lg">
                    <DialogHeader>
                        <DialogTitle>New Project</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Project Name</Label>
                            <Input id="name" {...register("name")} />
                            {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea id="description" rows={3} {...register("description")} />
                            {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label>Client</Label>
                            <Select value={watch("clientId")} onValueChange={(v) => v !== null && setValue("clientId", v)}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a client" />
                                </SelectTrigger>
                                <SelectContent>
                                    {clients.map((c: Client) => (
                                        <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            {errors.clientId && <p className="text-xs text-destructive">{errors.clientId.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label>Status</Label>
                            <Select value={watch("status")} onValueChange={(v) => setValue("status", v as ProjectStatus)}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select status" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="planning">Planning</SelectItem>
                                    <SelectItem value="active">Active</SelectItem>
                                    <SelectItem value="on_hold">On Hold</SelectItem>
                                    <SelectItem value="completed">Completed</SelectItem>
                                </SelectContent>
                            </Select>
                            {errors.status && <p className="text-xs text-destructive">{errors.status.message}</p>}
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                            <Button type="submit" disabled={createMut.isPending}>Create Project</Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>
        </div>
    );
}
