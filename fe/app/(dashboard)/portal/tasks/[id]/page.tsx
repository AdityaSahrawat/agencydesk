"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import {
    useTask, useProject, useComments, useCreateComment,
    useFiles, useUpdateFileApproval,
} from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ArrowLeft, Send, Paperclip, Check, X, AlertCircle, Eye } from "lucide-react";
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS, PRIORITY_LABELS, PRIORITY_COLORS, APPROVAL_LABELS, APPROVAL_COLORS } from "@/lib/constants";
import { EmptyState } from "@/components/shared/empty-state";
import { toast } from "sonner";
import type { FileApprovalStatus, TaskStatus, Priority, TaskFile, Comment } from "@/types";

export default function ClientTaskDetailPage() {
    const params = useParams();
    const router = useRouter();
    const { user } = useAuth();
    const taskId = params.id as string;

    const { data: task, isLoading } = useTask(taskId);
    const { data: project } = useProject(task?.projectId ?? "");
    const { data: comments, isLoading: commentsLoading } = useComments(taskId);
    const { data: files } = useFiles(taskId, false);

    const createCommentMut = useCreateComment();
    const approveFileMut = useUpdateFileApproval();

    const [commentText, setCommentText] = useState("");

    // Guard: if task is internal, client should not see it
    if (task?.internal) {
        return (
            <div>
                <Navbar title="Task Not Found" />
                <div className="p-6">
                    <EmptyState icon={AlertCircle} title="Task not found" description="You may not have access to this task." />
                </div>
            </div>
        );
    }

    const handleComment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!commentText.trim()) return;
        try {
            await createCommentMut.mutateAsync({
                taskId,
                userId: user!.id,
                userName: user!.name,
                content: commentText,
                internal: false,
            });
            setCommentText("");
            toast.success("Comment added");
        } catch {
            toast.error("Failed to add comment");
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

    return (
        <div>
            <Navbar title={task.title} subtitle={project?.name} />
            <div className="space-y-6 p-6">
                <Button variant="ghost" size="sm" onClick={() => router.back()} className="mb-2">
                    <ArrowLeft className="mr-1 h-4 w-4" />
                    Back
                </Button>

                {/* Task Info */}
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <h2 className="text-xl font-semibold">{task.title}</h2>
                                    <Badge variant="outline" className="gap-1 border-blue-200 bg-blue-50 text-blue-700">
                                        <Eye className="h-3 w-3" />
                                        Client View
                                    </Badge>
                                </div>
                                <p className="mt-2 text-sm text-muted-foreground">{task.description || "No description"}</p>
                            </div>
                            <div className="flex items-center gap-2">
                                <Badge className={TASK_STATUS_COLORS[task.status as TaskStatus]} variant="secondary">
                                    {TASK_STATUS_LABELS[task.status as TaskStatus]}
                                </Badge>
                                <Badge className={PRIORITY_COLORS[task.priority as Priority]} variant="secondary">
                                    {PRIORITY_LABELS[task.priority as Priority]}
                                </Badge>
                            </div>
                        </div>
                        {task.dueDate && (
                            <div className="mt-4 border-t border-border pt-3">
                                <p className="text-xs text-muted-foreground">Due Date: <span className="font-medium text-foreground">{task.dueDate}</span></p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Files */}
                <div>
                    <h3 className="mb-3 text-base font-semibold">Files</h3>
                    {(files ?? []).length === 0 ? (
                        <EmptyState icon={Paperclip} title="No files" description="No files have been shared with you for this task." />
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
                                                    <p className="text-xs text-muted-foreground">{f.uploaderName} · {f.createdAt.slice(0, 10)}</p>
                                                </div>
                                            </div>
                                            <Badge className={APPROVAL_COLORS[f.approvalStatus]} variant="secondary">
                                                {APPROVAL_LABELS[f.approvalStatus]}
                                            </Badge>
                                        </div>

                                        {f.approvalStatus === "pending" && (
                                            <div className="mt-3 flex gap-2 border-t border-border pt-3">
                                                <Button size="sm" onClick={() => handleApproval(f.id, "approved")}>
                                                    <Check className="mr-1 h-4 w-4" />
                                                    Approve
                                                </Button>
                                                <Button size="sm" variant="outline" onClick={() => handleApproval(f.id, "needs_changes")}>
                                                    <X className="mr-1 h-4 w-4" />
                                                    Needs Changes
                                                </Button>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>

                {/* Comments */}
                <div>
                    <h3 className="mb-3 text-base font-semibold">Comments</h3>
                    {commentsLoading ? (
                        <div className="space-y-2">{Array.from({ length: 2 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-lg" />)}</div>
                    ) : (comments ?? []).filter((c: Comment) => !c.internal).length === 0 ? (
                        <EmptyState icon={Send} title="No comments" description="Start the conversation." />
                    ) : (
                        <div className="space-y-3">
                            {(comments ?? []).filter((c: Comment) => !c.internal).map((c: Comment) => (
                                <Card key={c.id}>
                                    <CardContent className="p-4">
                                        <div className="flex items-start gap-3">
                                            <Avatar className="h-8 w-8">
                                                <AvatarFallback className="bg-primary/10 text-primary text-xs">
                                                    {c.userName.charAt(0)}
                                                </AvatarFallback>
                                            </Avatar>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <p className="text-sm font-medium">{c.userName}</p>
                                                    <span className="text-xs text-muted-foreground">{c.createdAt.slice(0, 10)}</span>
                                                </div>
                                                <p className="mt-1 text-sm">{c.content}</p>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}

                    <form onSubmit={handleComment} className="mt-4 space-y-3">
                        <Textarea
                            value={commentText}
                            onChange={(e) => setCommentText(e.target.value)}
                            placeholder="Write a comment..."
                            rows={3}
                        />
                        <div className="flex justify-end">
                            <Button type="submit" size="sm" disabled={createCommentMut.isPending || !commentText.trim()}>
                                <Send className="mr-1 h-4 w-4" />
                                Comment
                            </Button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
