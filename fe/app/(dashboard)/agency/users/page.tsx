"use client";

import { useAuth } from "@/providers/auth-provider";
import { useUsers } from "@/hooks/use-api";
import { Navbar } from "@/components/layout/navbar";
import { DataTable, Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Users, Mail, Calendar } from "lucide-react";
import type { User } from "@/types";
import { ROLE_LABELS, ROLE_COLORS } from "@/lib/constants";

export default function UsersPage() {
    const { user } = useAuth();
    const agencyId = user?.agencyId ?? "";
    const { data: users, isLoading } = useUsers(agencyId);

    const columns: Column<User>[] = [
        {
            key: "name",
            header: "Name",
            render: (u) => (
                <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                        {u.name.charAt(0)}
                    </div>
                    <span className="font-medium">{u.name}</span>
                </div>
            ),
        },
        { key: "email", header: "Email", render: (u) => <span className="text-muted-foreground">{u.email}</span> },
        {
            key: "role",
            header: "Role",
            render: (u) => <Badge className={ROLE_COLORS[u.role]} variant="secondary">{ROLE_LABELS[u.role]}</Badge>,
        },
        {
            key: "createdAt",
            header: "Joined",
            render: (u) => <span className="text-muted-foreground">{u.createdAt.slice(0, 10)}</span>,
        },
    ];

    return (
        <div>
            <Navbar title="Users" subtitle="Team members in your agency" />
            <div className="space-y-4 p-6">
                {isLoading ? (
                    <div className="space-y-2">
                        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" />)}
                    </div>
                ) : (users ?? []).length === 0 ? (
                    <EmptyState icon={Users} title="No users" description="No team members found." />
                ) : (
                    <DataTable columns={columns} data={users ?? []} rowKey={(u) => u.id} />
                )}
            </div>
        </div>
    );
}
