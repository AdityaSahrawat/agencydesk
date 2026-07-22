"use client";

import { RouteGuard } from "@/components/layout/route-guard";
import { AgencySidebar } from "@/components/layout/agency-sidebar";

export default function AgencyLayout({ children }: { children: React.ReactNode }) {
    return (
        <RouteGuard roles={["agency_admin", "agency_member"]}>
            <div className="flex h-screen overflow-hidden">
                <AgencySidebar />
                <main className="flex-1 overflow-y-auto">{children}</main>
            </div>
        </RouteGuard>
    );
}
