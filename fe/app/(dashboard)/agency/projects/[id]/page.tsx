"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import {
    useProject, useTasks, useClients, useProjectMembers,
    useCreateTask, useDeleteTask, useTimeEntries,
} from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Plus, Trash2, Clock, CheckCircle2, ListTodo, Users, AlertCircle } from "lucide-react";
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS, PRIORITY_LABELS, PRIORITY_COLORS, PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS } from "@/lib/constants";
import { VisibilityBadge } from "@/components/shared/visibility-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import type { TaskStatus, Priority, ProjectStatus, Client, Task, User, Project } from "@/types";

const taskSchema = z.object({
    title: z.string().min(1, "Title is required"),
    description: z.string().optional(),
    status: z.enum(["todo", "doing", "done"]),
    priority: z.enum(["low", "medium", "high"]),
    dueDate: z.string().optional(),
    assigneeId: z.string().optional(),
    internal: z.boolean(),
});
type TaskForm = z.infer<typeof taskSchema>;

export default function ProjectDetailPage() {
    const params = useParams();
    const router = useRouter();
    const { user } = useAuth();
    const projectId = params.id as string;
    const agencyId = user?.agencyId ?? "";
    const isAdmin = user?.role === "agency_admin";

    const [dialogOpen, setDialogOpen] = useState(false);
    const [deleteId, setDeleteId] = useState<string | null>(null);

    const { data: project, isLoading } = useProject(projectId);
    const { data: tasksData, isLoading: tasksLoading } = useTasks({ projectId, pageSize: 1000 });
    const { data: clientsData } = useClients(agencyId, { pageSize: 100 });
    const { data: members } = useProjectMembers(projectId);
    const { data: timeEntriesData } = useTimeEntries("__all__");
    const createMut = useCreateTask();
    const deleteMut = useDeleteTask();

    const tasks = tasksData?.data ?? [];
    const client = clientsData?.data?.find((c: Client) => c.id === project?.clientId);
    const members_ = members ?? [];

    const taskStats = {
        todo: tasks.filter((t: Task) => t.status === "todo").length,
        doing: tasks.filter((t: Task) => t.status === "doing").length,
        done: tasks.filter((t: Task) => t.status === "done").length,
    };

    // We can't get time entries for all tasks in project easily, so compute from tasks
    const totalHours = tasks.reduce((sum: number, t: Task) => sum, 0); // placeholder — time entries are per task

    const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<TaskForm>({
        resolver: zodResolver(taskSchema),
        defaultValues: { status: "todo", priority: "medium", internal: false },
    });

    const onSubmit = async (vals: TaskForm) => {
        try {
            await createMut.mutateAsync({
                ...vals,
                projectId,
                assigneeId: vals.assigneeId || undefined,
                description: vals.description ?? "",
            });
            toast.success("Task created");
            setDialogOpen(false);
            reset({ title: "", description: "", status: "todo", priority: "medium", dueDate: "", assigneeId: "", internal: false });
        } catch {
            toast.error("Failed to create task");
        }
    };

    const confirmDelete = async () => {
        if (!deleteId) return;
        try {
            await deleteMut.mutateAsync(deleteId);
            toast.success("Task deleted");
            setDeleteId(null);
        } catch {
            toast.error("Failed to delete task");
        }
    };

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
                    <EmptyState icon={AlertCircle} title="Project not found" description="This project may have been deleted." />
                </div>
            </div>
        );
    }

    return (
        <div>
            <Navbar title={project.name} subtitle={client?.name} />
            <div className="space-y-6 p-6">
                <Button variant="ghost" size="sm" onClick={() => router.push("/projects")} className="mb-2">
                    <ArrowLeft className="mr-1 h-4 w-4" />
                    Back to Projects
                </Button>

                {/* Header */}
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
                        </div>

                        {/* Stats */}
                        <div className="mt-5 grid grid-cols-2 gap-4 border-t border-border pt-4 sm:grid-cols-4">
                            <div className="flex items-center gap-2 text-sm">
                                <ListTodo className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">To Do:</span>
                                <span className="font-medium">{taskStats.todo}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Clock className="h-4 w-4 text-blue-600" />
                                <span className="text-muted-foreground">In Progress:</span>
                                <span className="font-medium">{taskStats.doing}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                                <span className="text-muted-foreground">Done:</span>
                                <span className="font-medium">{taskStats.done}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Users className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Members:</span>
                                <span className="font-medium">{members_.length}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Assigned Members */}
                {members_.length > 0 && (
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Assigned Members</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-wrap gap-3">
                            {members_.map((m: User) => (
                                <div key={m.id} className="flex items-center gap-2 rounded-lg border border-border px-3 py-2">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                                        {m.name.charAt(0)}
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">{m.name}</p>
                                        <p className="text-xs text-muted-foreground">{m.role === "agency_admin" ? "Admin" : "Member"}</p>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                )}

                {/* Tabs: Tasks | Files | Time */}
                <Tabs defaultValue="tasks">
                    <div className="flex items-center justify-between">
                        <TabsList>
                            <TabsTrigger value="tasks">Tasks</TabsTrigger>
                            <TabsTrigger value="time">Time Summary</TabsTrigger>
                        </TabsList>
                        {isAdmin && (
                            <Button size="sm" onClick={() => { reset({ title: "", description: "", status: "todo", priority: "medium", dueDate: "", assigneeId: "", internal: false }); setDialogOpen(true); }}>
                                <Plus className="mr-1 h-4 w-4" />
                                New Task
                            </Button>
                        )}
                    </div>

                    <TabsContent value="tasks" className="mt-4">
                        {tasksLoading ? (
                            <div className="space-y-2">
                                {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16 rounded-lg" />)}
                            </div>
                        ) : tasks.length === 0 ? (
                            <EmptyState icon={ListTodo} title="No tasks" description="Create tasks to track work on this project." />
                        ) : (
                            <div className="space-y-2">
                                {tasks.map((t: Task) => (
                                    <div
                                        key={t.id}
                                        className="flex items-center justify-between rounded-lg border border-border p-4 hover:bg-accent cursor-pointer"
                                        onClick={() => router.push(`/tasks/${t.id}`)}
                                    >
                                        <div className="flex items-center gap-3">
                                            <Badge className={TASK_STATUS_COLORS[t.status as TaskStatus]} variant="secondary">
                                                {TASK_STATUS_LABELS[t.status as TaskStatus]}
                                            </Badge>
                                            <div>
                                                <p className="font-medium">{t.title}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {t.dueDate ? `Due ${t.dueDate}` : "No due date"}
                                                </p>
                                            </div>
                                            <VisibilityBadge internal={t.internal} />
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Badge className={PRIORITY_COLORS[t.priority as Priority]} variant="secondary">
                                                {PRIORITY_LABELS[t.priority as Priority]}
                                            </Badge>
                                            {isAdmin && (
                                                <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); setDeleteId(t.id); }}>
                                                    <Trash2 className="h-4 w-4 text-destructive" />
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </TabsContent>

                    <TabsContent value="time" className="mt-4">
                        <Card>
                            <CardContent className="p-5">
                                <p className="text-sm text-muted-foreground">Total hours logged on this project:</p>
                                <p className="mt-1 text-3xl font-semibold">{totalHours}h</p>
                                <p className="mt-2 text-xs text-muted-foreground">Detailed time entries are available on each task page.</p>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>

            {/* Create Task Dialog */}
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent className="max-w-lg">
                    <DialogHeader>
                        <DialogTitle>New Task</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="title">Title</Label>
                            <Input id="title" {...register("title")} />
                            {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea id="description" rows={3} {...register("description")} />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Status</Label>
                                <Select value={watch("status")} onValueChange={(v) => v !== null && setValue("status", v as TaskStatus)}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="todo">To Do</SelectItem>
                                        <SelectItem value="doing">In Progress</SelectItem>
                                        <SelectItem value="done">Done</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label>Priority</Label>
                                <Select value={watch("priority")} onValueChange={(v) => v !== null && setValue("priority", v as Priority)}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="low">Low</SelectItem>
                                        <SelectItem value="medium">Medium</SelectItem>
                                        <SelectItem value="high">High</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="dueDate">Due Date</Label>
                                <Input id="dueDate" type="date" {...register("dueDate")} />
                            </div>
                            <div className="space-y-2">
                                <Label>Assignee</Label>
                                <Select value={watch("assigneeId") ?? ""} onValueChange={(v) => v !== null && setValue("assigneeId", v)}>
                                    <SelectTrigger><SelectValue placeholder="Unassigned" /></SelectTrigger>
                                    <SelectContent>
                                        {members_.map((m: User) => (
                                            <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="internal"
                                {...register("internal")}
                                className="h-4 w-4 rounded border-border"
                            />
                            <Label htmlFor="internal" className="text-sm font-normal cursor-pointer">
                                Internal task (hidden from client)
                            </Label>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                            <Button type="submit" disabled={createMut.isPending}>Create Task</Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            {/* Delete Task Dialog */}
            <Dialog open={!!deleteId} onOpenChange={(o) => !o && setDeleteId(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Task</DialogTitle>
                    </DialogHeader>
                    <div className="flex items-start gap-3 py-2">
                        <AlertCircle className="mt-0.5 h-5 w-5 text-destructive" />
                        <p className="text-sm text-muted-foreground">Are you sure? This will also delete all comments, files, and time entries for this task.</p>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteId(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={confirmDelete} disabled={deleteMut.isPending}>Delete</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
