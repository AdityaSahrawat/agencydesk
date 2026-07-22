"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import {
    useTask, useComments, useCreateComment, useDeleteComment,
    useFiles, useUploadFile, useUpdateFileApproval, useDeleteFile,
    useTimeEntries, useCreateTimeEntry, useDeleteTimeEntry,
    useProject, useProjectMembers,
} from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ArrowLeft, Send, Trash2, Clock, Paperclip, Check, X, AlertCircle, Lock, Eye } from "lucide-react";
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS, PRIORITY_LABELS, PRIORITY_COLORS, APPROVAL_LABELS, APPROVAL_COLORS } from "@/lib/constants";
import { VisibilityBadge } from "@/components/shared/visibility-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { toast } from "sonner";
import type { TaskStatus, Priority, FileApprovalStatus, Visibility, User, Comment, TaskFile, TimeEntry } from "@/types";

export default function TaskDetailPage() {
    const params = useParams();
    const router = useRouter();
    const { user } = useAuth();
    const taskId = params.id as string;
    const isAdmin = user?.role === "agency_admin";
    const isClient = user?.role === "client_user";
    const isMember = user?.role === "agency_member";
    const isAgency = isAdmin || isMember;

    const { data: task, isLoading } = useTask(taskId);
    const { data: project } = useProject(task?.projectId ?? "");
    const { data: members } = useProjectMembers(task?.projectId ?? "");

    const { data: comments, isLoading: commentsLoading } = useComments(taskId);
    const { data: files } = useFiles(taskId, isAgency);
    const { data: timeEntries, isLoading: timeLoading } = useTimeEntries(taskId);

    const createCommentMut = useCreateComment();
    const deleteCommentMut = useDeleteComment();
    const uploadFileMut = useUploadFile();
    const approveFileMut = useUpdateFileApproval();
    const deleteFileMut = useDeleteFile();
    const createTimeMut = useCreateTimeEntry();
    const deleteTimeMut = useDeleteTimeEntry();

    const [commentText, setCommentText] = useState("");
    const [commentInternal, setCommentInternal] = useState(false);
    const [timeHours, setTimeHours] = useState("");
    const [timeDate, setTimeDate] = useState(new Date().toISOString().slice(0, 10));
    const [timeNote, setTimeNote] = useState("");
    const [fileName, setFileName] = useState("");
    const [fileVisibility, setFileVisibility] = useState<Visibility>("client_visible");

    const memberName = (id?: string) => members?.find((m: User) => m.id === id)?.name ?? "Unassigned";

    const handleComment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!commentText.trim()) return;
        try {
            await createCommentMut.mutateAsync({
                taskId,
                userId: user!.id,
                userName: user!.name,
                content: commentText,
                internal: isAgency ? commentInternal : false,
            });
            setCommentText("");
            setCommentInternal(false);
            toast.success("Comment added");
        } catch {
            toast.error("Failed to add comment");
        }
    };

    const handleAddTime = async (e: React.FormEvent) => {
        e.preventDefault();
        const hours = parseFloat(timeHours);
        if (!hours || hours <= 0) return;
        try {
            await createTimeMut.mutateAsync({
                taskId,
                userId: user!.id,
                userName: user!.name,
                durationHours: hours,
                date: timeDate,
                note: timeNote,
            });
            setTimeHours("");
            setTimeNote("");
            toast.success("Time entry added");
        } catch {
            toast.error("Failed to add time entry");
        }
    };

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!fileName.trim()) return;
        try {
            await uploadFileMut.mutateAsync({
                taskId,
                name: fileName,
                url: "#",
                mimeType: "application/octet-stream",
                size: 0,
                uploaderId: user!.id,
                uploaderName: user!.name,
                visibility: fileVisibility,
                approvalStatus: "pending",
            });
            setFileName("");
            toast.success("File uploaded");
        } catch {
            toast.error("Failed to upload file");
        }
    };

    const handleApproval = async (fileId: string, status: FileApprovalStatus) => {
        try {
            await approveFileMut.mutateAsync({ id: fileId, status, taskId });
            toast.success(status === "approved" ? "File approved" : "Marked as needs changes");
        } catch {
            toast.error("Failed to update approval");
        }
    };

    if (isLoading) {
        return (
            <div>
                <Navbar title="Task" />
                <div className="space-y-4 p-6">
                    <Skeleton className="h-40 rounded-lg" />
                    <Skeleton className="h-64 rounded-lg" />
                </div>
            </div>
        );
    }

    if (!task) {
        return (
            <div>
                <Navbar title="Task Not Found" />
                <div className="p-6">
                    <EmptyState icon={AlertCircle} title="Task not found" />
                </div>
            </div>
        );
    }

    const totalTime = (timeEntries ?? []).reduce((s: number, te: TimeEntry) => s + te.durationHours, 0);

    return (
        <div>
            <Navbar title={task.title} subtitle={project?.name} />
            <div className="space-y-6 p-6">
                <Button variant="ghost" size="sm" onClick={() => router.push(`/projects/${task.projectId}`)} className="mb-2">
                    <ArrowLeft className="mr-1 h-4 w-4" />
                    Back to Project
                </Button>

                {/* Task Info */}
                <Card>
                    <CardContent className="p-5">
                        <div className="flex flex-wrap items-start justify-between gap-4">
                            <div className="flex-1">
                                <div className="flex flex-wrap items-center gap-2">
                                    <h2 className="text-xl font-semibold">{task.title}</h2>
                                    <VisibilityBadge internal={task.internal} />
                                </div>
                                <p className="mt-2 text-sm text-muted-foreground">{task.description || "No description"}</p>
                            </div>
                            <div className="flex flex-wrap items-center gap-2">
                                <Badge className={TASK_STATUS_COLORS[task.status as TaskStatus]} variant="secondary">
                                    {TASK_STATUS_LABELS[task.status as TaskStatus]}
                                </Badge>
                                <Badge className={PRIORITY_COLORS[task.priority as Priority]} variant="secondary">
                                    {PRIORITY_LABELS[task.priority as Priority]}
                                </Badge>
                            </div>
                        </div>
                        <div className="mt-5 grid grid-cols-2 gap-4 border-t border-border pt-4 sm:grid-cols-3">
                            <div>
                                <p className="text-xs text-muted-foreground">Assignee</p>
                                <p className="mt-1 text-sm font-medium">{memberName(task.assigneeId)}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Due Date</p>
                                <p className="mt-1 text-sm font-medium">{task.dueDate ?? "—"}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Created</p>
                                <p className="mt-1 text-sm font-medium">{task.createdAt.slice(0, 10)}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Tabs */}
                <Tabs defaultValue="comments">
                    <TabsList>
                        <TabsTrigger value="comments">Comments</TabsTrigger>
                        <TabsTrigger value="files">Files</TabsTrigger>
                        {isAgency && <TabsTrigger value="time">Time Tracking</TabsTrigger>}
                    </TabsList>

                    {/* Comments */}
                    <TabsContent value="comments" className="mt-4 space-y-4">
                        {commentsLoading ? (
                            <div className="space-y-2">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-lg" />)}</div>
                        ) : (comments ?? []).length === 0 ? (
                            <EmptyState icon={Send} title="No comments yet" description="Start the conversation by adding a comment." />
                        ) : (
                            <div className="space-y-3">
                                {(comments ?? []).map((c: Comment) => (
                                    <Card key={c.id}>
                                        <CardContent className="p-4">
                                            <div className="flex items-start gap-3">
                                                <Avatar className="h-8 w-8">
                                                    <AvatarFallback className="bg-primary/10 text-primary text-xs">
                                                        {c.userName.charAt(0)}
                                                    </AvatarFallback>
                                                </Avatar>
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2">
                                                        <p className="text-sm font-medium">{c.userName}</p>
                                                        {c.internal && <VisibilityBadge internal={c.internal} />}
                                                        <span className="text-xs text-muted-foreground">{c.createdAt.slice(0, 10)}</span>
                                                    </div>
                                                    <p className="mt-1 text-sm">{c.content}</p>
                                                </div>
                                                {(isAgency || c.userId === user?.id) && (
                                                    <Button variant="ghost" size="icon" onClick={async () => { await deleteCommentMut.mutateAsync({ id: c.id, taskId }); toast.success("Comment deleted"); }}>
                                                        <Trash2 className="h-4 w-4 text-destructive" />
                                                    </Button>
                                                )}
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}

                        {/* Add Comment */}
                        <form onSubmit={handleComment} className="space-y-3">
                            <Textarea
                                value={commentText}
                                onChange={(e) => setCommentText(e.target.value)}
                                placeholder="Write a comment..."
                                rows={3}
                            />
                            {isAgency && (
                                <label className="flex items-center gap-2 text-sm">
                                    <input
                                        type="checkbox"
                                        checked={commentInternal}
                                        onChange={(e) => setCommentInternal(e.target.checked)}
                                        className="h-4 w-4 rounded border-border"
                                    />
                                    <span className="flex items-center gap-1">
                                        <Lock className="h-3 w-3" />
                                        Internal comment (hidden from client)
                                    </span>
                                </label>
                            )}
                            <div className="flex justify-end">
                                <Button type="submit" size="sm" disabled={createCommentMut.isPending || !commentText.trim()}>
                                    <Send className="mr-1 h-4 w-4" />
                                    Comment
                                </Button>
                            </div>
                        </form>
                    </TabsContent>

                    {/* Files */}
                    <TabsContent value="files" className="mt-4 space-y-4">
                        {(files ?? []).length === 0 ? (
                            <EmptyState icon={Paperclip} title="No files" description="Upload files for this task." />
                        ) : (
                            <div className="space-y-2">
                                {(files ?? []).map((f: TaskFile) => (
                                    <Card key={f.id}>
                                        <CardContent className="p-4">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                                                        <Paperclip className="h-5 w-5 text-muted-foreground" />
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-medium">{f.name}</p>
                                                        <p className="text-xs text-muted-foreground">
                                                            {f.uploaderName} · {f.createdAt.slice(0, 10)}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    {f.visibility === "internal" ? (
                                                        <VisibilityBadge internal />
                                                    ) : (
                                                        <Badge variant="outline" className="gap-1 border-blue-200 bg-blue-50 text-blue-700">
                                                            <Eye className="h-3 w-3" />
                                                            Client Visible
                                                        </Badge>
                                                    )}
                                                    <Badge className={APPROVAL_COLORS[f.approvalStatus]} variant="secondary">
                                                        {APPROVAL_LABELS[f.approvalStatus]}
                                                    </Badge>
                                                </div>
                                            </div>

                                            {/* Approval buttons */}
                                            {isClient && f.visibility === "client_visible" && f.approvalStatus === "pending" && (
                                                <div className="mt-3 flex gap-2 border-t border-border pt-3">
                                                    <Button size="sm" variant="default" onClick={() => handleApproval(f.id, "approved")}>
                                                        <Check className="mr-1 h-4 w-4" />
                                                        Approve
                                                    </Button>
                                                    <Button size="sm" variant="outline" onClick={() => handleApproval(f.id, "needs_changes")}>
                                                        <X className="mr-1 h-4 w-4" />
                                                        Needs Changes
                                                    </Button>
                                                </div>
                                            )}

                                            {isAgency && (
                                                <div className="mt-3 flex justify-end border-t border-border pt-3">
                                                    <Button variant="ghost" size="icon" onClick={async () => { await deleteFileMut.mutateAsync({ id: f.id, taskId }); toast.success("File deleted"); }}>
                                                        <Trash2 className="h-4 w-4 text-destructive" />
                                                    </Button>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}

                        {/* Upload */}
                        {isAgency && (
                            <form onSubmit={handleUpload} className="space-y-3 rounded-lg border border-border p-4">
                                <p className="text-sm font-medium">Upload File</p>
                                <div className="flex flex-wrap items-end gap-3">
                                    <div className="flex-1 space-y-2">
                                        <Label htmlFor="fileName">File Name</Label>
                                        <Input id="fileName" value={fileName} onChange={(e) => setFileName(e.target.value)} placeholder="document.pdf" />
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Visibility</Label>
                                        <Select value={fileVisibility} onValueChange={(v) => setFileVisibility(v as Visibility)}>
                                            <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="client_visible">Client Visible</SelectItem>
                                                <SelectItem value="internal">Internal</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <Button type="submit" size="sm" disabled={uploadFileMut.isPending || !fileName.trim()}>
                                        <Paperclip className="mr-1 h-4 w-4" />
                                        Upload
                                    </Button>
                                </div>
                            </form>
                        )}
                    </TabsContent>

                    {/* Time Tracking */}
                    {isAgency && (
                        <TabsContent value="time" className="mt-4 space-y-4">
                            <Card>
                                <CardContent className="p-5">
                                    <div className="flex items-center gap-2">
                                        <Clock className="h-5 w-5 text-amber-600" />
                                        <p className="text-sm text-muted-foreground">Total time logged:</p>
                                        <p className="text-lg font-semibold">{totalTime}h</p>
                                    </div>
                                </CardContent>
                            </Card>

                            {(timeEntries ?? []).length > 0 && (
                                <div className="space-y-2">
                                    {(timeEntries ?? []).map((te: TimeEntry) => (
                                        <Card key={te.id}>
                                            <CardContent className="flex items-center justify-between p-4">
                                                <div className="flex items-center gap-3">
                                                    <Avatar className="h-8 w-8">
                                                        <AvatarFallback className="bg-primary/10 text-primary text-xs">
                                                            {te.userName.charAt(0)}
                                                        </AvatarFallback>
                                                    </Avatar>
                                                    <div>
                                                        <p className="text-sm font-medium">{te.userName}</p>
                                                        <p className="text-xs text-muted-foreground">{te.date} · {te.note}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="secondary">{te.durationHours}h</Badge>
                                                    <Button variant="ghost" size="icon" onClick={async () => { await deleteTimeMut.mutateAsync({ id: te.id, taskId }); toast.success("Time entry deleted"); }}>
                                                        <Trash2 className="h-4 w-4 text-destructive" />
                                                    </Button>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            )}

                            <form onSubmit={handleAddTime} className="space-y-3 rounded-lg border border-border p-4">
                                <p className="text-sm font-medium">Add Time Entry</p>
                                <div className="flex flex-wrap items-end gap-3">
                                    <div className="space-y-2">
                                        <Label htmlFor="timeHours">Hours</Label>
                                        <Input id="timeHours" type="number" step="0.5" min="0.5" value={timeHours} onChange={(e) => setTimeHours(e.target.value)} placeholder="2.5" className="w-24" />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="timeDate">Date</Label>
                                        <Input id="timeDate" type="date" value={timeDate} onChange={(e) => setTimeDate(e.target.value)} className="w-40" />
                                    </div>
                                    <div className="flex-1 space-y-2">
                                        <Label htmlFor="timeNote">Note</Label>
                                        <Input id="timeNote" value={timeNote} onChange={(e) => setTimeNote(e.target.value)} placeholder="What did you work on?" />
                                    </div>
                                    <Button type="submit" size="sm" disabled={createTimeMut.isPending}>
                                        <Clock className="mr-1 h-4 w-4" />
                                        Log Time
                                    </Button>
                                </div>
                            </form>
                        </TabsContent>
                    )}
                </Tabs>
            </div>
        </div>
    );
}
