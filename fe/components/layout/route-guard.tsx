"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { Loader2 } from "lucide-react";

interface GuardProps {
    children: React.ReactNode;
    roles?: ("agency_admin" | "agency_member" | "client_user")[];
}

export function RouteGuard({ children, roles }: GuardProps) {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (isLoading) return;
        if (!user) {
            router.replace("/login");
            return;
        }
        if (roles && user && !roles.includes(user.role)) {
            router.replace(user.role === "client_user" ? "/portal" : "/agency/dashboard");
        }
    }, [user, isLoading, roles, router]);

    if (isLoading || !user) {
        return (
            <div className="flex h-screen items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    if (roles && user && !roles.includes(user.role)) return null;

    return <>{children}</>;
}
