"use client";

import { useParams, useRouter } from "next/navigation";
import { useClients, useProjects } from "@/hooks/use-api";
import { useAuth } from "@/providers/auth-provider";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Mail, Phone, User } from "lucide-react";
import { PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS } from "@/lib/constants";
import Link from "next/link";
import type { Client, Project } from "@/types";
import { EmptyState } from "@/components/shared/empty-state";
import { Building2 } from "lucide-react";

export default function ClientDetailPage() {
    const params = useParams();
    const router = useRouter();
    const { user } = useAuth();
    const agencyId = user?.agencyId ?? "";
    const clientId = params.id as string;

    const { data: clientsData } = useClients(agencyId, { pageSize: 100 });
    const client = (clientsData?.data ?? []).find((c: Client) => c.id === clientId);
    const { data: projectsData, isLoading } = useProjects(agencyId, { clientId, pageSize: 100 });

    const projects = projectsData?.data ?? [];

    return (
        <div>
            <Navbar title={client?.name ?? "Client"} subtitle={client?.contactPerson} />
            <div className="space-y-6 p-6">
                <Button variant="ghost" size="sm" onClick={() => router.push("/clients")} className="mb-2">
                    <ArrowLeft className="mr-1 h-4 w-4" />
                    Back to Clients
                </Button>

                {/* Client Info */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Client Information</CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div className="flex items-center gap-2 text-sm">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            <span>{client?.email ?? "—"}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Phone className="h-4 w-4 text-muted-foreground" />
                            <span>{client?.phone ?? "—"}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <User className="h-4 w-4 text-muted-foreground" />
                            <span>{client?.contactPerson ?? "—"}</span>
                        </div>
                    </CardContent>
                </Card>

                {/* Projects */}
                <div>
                    <h2 className="mb-3 text-base font-semibold">Projects</h2>
                    {isLoading ? (
                        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                            {Array.from({ length: 2 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-lg" />)}
                        </div>
                    ) : projects.length === 0 ? (
                        <EmptyState icon={Building2} title="No projects" description="This client has no projects yet." />
                    ) : (
                        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {projects.map((p: Project) => (
                                <Link key={p.id} href={`/projects/${p.id}`}>
                                    <Card className="hover:border-primary/40">
                                        <CardContent className="p-4">
                                            <div className="flex items-center justify-between">
                                                <p className="font-medium">{p.name}</p>
                                                <Badge className={PROJECT_STATUS_COLORS[p.status]} variant="secondary">
                                                    {PROJECT_STATUS_LABELS[p.status]}
                                                </Badge>
                                            </div>
                                            <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{p.description}</p>
                                        </CardContent>
                                    </Card>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
