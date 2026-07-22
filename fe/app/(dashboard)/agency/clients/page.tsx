"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { useClients, useCreateClient, useDeleteClient } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { SearchBar } from "@/components/shared/search-bar";
import { DataTable, Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Building2, Trash2, Pencil, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { useProjects } from "@/hooks/use-api";
import type { Client, Project } from "@/types";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const clientSchema = z.object({
    name: z.string().min(1, "Name is required"),
    email: z.string().email("Invalid email"),
    contactPerson: z.string().min(1, "Contact person is required"),
    phone: z.string().optional(),
});
type ClientForm = z.infer<typeof clientSchema>;

export default function ClientsPage() {
    const router = useRouter();
    const { user } = useAuth();
    const agencyId = user?.agencyId ?? "";
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [editTarget, setEditTarget] = useState<Client | null>(null);
    const [deleteTarget, setDeleteTarget] = useState<Client | null>(null);

    const { data, isLoading } = useClients(agencyId, { search, page });
    const { data: allProjects } = useProjects(agencyId, { pageSize: 100 });
    const createMut = useCreateClient();
    const deleteMut = useDeleteClient();

    const { register, handleSubmit, reset, formState: { errors } } = useForm<ClientForm>({
        resolver: zodResolver(clientSchema),
    });

    const projectCount = (clientId: string) =>
        (allProjects?.data ?? []).filter((p: Project) => p.clientId === clientId).length;

    const openCreate = () => {
        setEditTarget(null);
        reset({ name: "", email: "", contactPerson: "", phone: "" });
        setDialogOpen(true);
    };

    const openEdit = (c: Client) => {
        setEditTarget(c);
        reset({ name: c.name, email: c.email, contactPerson: c.contactPerson, phone: c.phone ?? "" });
        setDialogOpen(true);
    };

    const onSubmit = async (vals: ClientForm) => {
        try {
            if (editTarget) {
                // reuse create endpoint pattern — but we have updateClient in api
                const { updateClient } = await import("@/services/api");
                await updateClient(editTarget.id, vals);
                toast.success("Client updated");
            } else {
                await createMut.mutateAsync({ ...vals, agencyId });
                toast.success("Client created");
            }
            setDialogOpen(false);
        } catch {
            toast.error("Something went wrong");
        }
    };

    const confirmDelete = async () => {
        if (!deleteTarget) return;
        try {
            await deleteMut.mutateAsync(deleteTarget.id);
            toast.success("Client deleted");
            setDeleteTarget(null);
        } catch {
            toast.error("Failed to delete client");
        }
    };

    const columns: Column<Client>[] = [
        {
            key: "name",
            header: "Name",
            render: (c) => <span className="font-medium">{c.name}</span>,
        },
        { key: "email", header: "Email" },
        { key: "contactPerson", header: "Contact" },
        {
            key: "projects",
            header: "Projects",
            render: (c) => <span className="text-muted-foreground">{projectCount(c.id)}</span>,
        },
        {
            key: "actions",
            header: "",
            className: "text-right",
            render: (c) => (
                <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); openEdit(c); }}>
                        <Pencil className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); setDeleteTarget(c); }}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                </div>
            ),
        },
    ];

    return (
        <div>
            <Navbar title="Clients" subtitle="Manage your agency's clients" />
            <div className="space-y-4 p-6">
                <div className="flex items-center justify-between gap-4">
                    <SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Search clients..." />
                    <Button onClick={openCreate} size="sm">
                        <Plus className="mr-1 h-4 w-4" />
                        New Client
                    </Button>
                </div>

                {isLoading ? (
                    <div className="space-y-2">
                        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" />)}
                    </div>
                ) : (data?.data ?? []).length === 0 ? (
                    <EmptyState
                        icon={Building2}
                        title="No clients yet"
                        description="Create your first client to start managing their projects."
                        actionLabel="New Client"
                        onAction={openCreate}
                    />
                ) : (
                    <DataTable
                        columns={columns}
                        data={data?.data ?? []}
                        rowKey={(c) => c.id}
                        onRowClick={(c) => router.push(`/clients/${c.id}`)}
                    />
                )}

                {/* Pagination */}
                {(data?.total ?? 0) > 10 && (
                    <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">
                            Page {data?.page} of {Math.ceil((data?.total ?? 0) / 10)}
                        </p>
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
                            <Button variant="outline" size="sm" disabled={(data?.page ?? 1) * 10 >= (data?.total ?? 0)} onClick={() => setPage(p => p + 1)}>Next</Button>
                        </div>
                    </div>
                )}
            </div>

            {/* Create / Edit Dialog */}
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{editTarget ? "Edit Client" : "New Client"}</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Company Name</Label>
                            <Input id="name" {...register("name")} />
                            {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input id="email" type="email" {...register("email")} />
                            {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="contactPerson">Contact Person</Label>
                            <Input id="contactPerson" {...register("contactPerson")} />
                            {errors.contactPerson && <p className="text-xs text-destructive">{errors.contactPerson.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="phone">Phone (optional)</Label>
                            <Input id="phone" {...register("phone")} />
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                            <Button type="submit" disabled={createMut.isPending}>
                                {editTarget ? "Save Changes" : "Create Client"}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            {/* Delete Confirm */}
            <Dialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Client</DialogTitle>
                    </DialogHeader>
                    <div className="flex items-start gap-3 py-2">
                        <AlertCircle className="mt-0.5 h-5 w-5 text-destructive" />
                        <p className="text-sm text-muted-foreground">
                            Are you sure you want to delete <strong>{deleteTarget?.name}</strong>? This action cannot be undone.
                        </p>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={confirmDelete} disabled={deleteMut.isPending}>
                            Delete
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
