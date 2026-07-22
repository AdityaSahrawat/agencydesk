"use client";

import { RouteGuard } from "@/components/layout/route-guard";
import { ClientSidebar } from "@/components/layout/client-sidebar";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
    return (
        <RouteGuard roles={["client_user"]}>
            <div className="flex h-screen overflow-hidden">
                <ClientSidebar />
                <main className="flex-1 overflow-y-auto">{children}</main>
            </div>
        </RouteGuard>
    );
}
