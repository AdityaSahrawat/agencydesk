"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";
import { FolderKanban, CheckSquare, FileText, LogOut, ChevronsLeftRight } from "lucide-react";

const navItems = [
    { href: "/portal", label: "My Projects", icon: FolderKanban },
    { href: "/portal/tasks", label: "My Tasks", icon: CheckSquare },
    { href: "/portal/files", label: "Files", icon: FileText },
];

export function ClientSidebar() {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    return (
        <aside className="flex h-screen w-56 flex-col border-r border-border bg-card">
            <div className="flex h-16 items-center gap-2 border-b border-border px-5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <ChevronsLeftRight className="h-4 w-4" />
                </div>
                <span className="text-base font-semibold tracking-tight">Client Portal</span>
            </div>

            <nav className="flex-1 space-y-1 px-3 py-4">
                {navItems.map((item) => {
                    const active = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                                active
                                    ? "bg-primary text-primary-foreground"
                                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                            )}
                        >
                            <item.icon className="h-4 w-4" />
                            {item.label}
                        </Link>
                    );
                })}
            </nav>

            <div className="border-t border-border p-3">
                <div className="flex items-center gap-3 px-3 py-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                        {user?.name?.charAt(0) ?? "?"}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="truncate text-sm font-medium">{user?.name}</p>
                        <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
                    </div>
                    <button
                        onClick={logout}
                        className="rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                        title="Logout"
                    >
                        <LogOut className="h-4 w-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
}
