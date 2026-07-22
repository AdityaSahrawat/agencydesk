"use client";

import { useAuth } from "@/providers/auth-provider";
import { ROLE_LABELS, ROLE_COLORS } from "@/lib/constants";
import { Role } from "@/types";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface NavbarProps {
    title: string;
    subtitle?: string;
}

export function Navbar({ title, subtitle }: NavbarProps) {
    const { user } = useAuth();

    return (
        <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
            <div>
                <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
                {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
            </div>
            <div className="flex items-center gap-4">
                <div className="relative hidden md:block">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                        placeholder="Search..."
                        className="w-64 pl-9"
                        readOnly
                    />
                </div>
                {user && user.role && (
                    <Badge className={ROLE_COLORS[user.role as Role]} variant="secondary">
                        {ROLE_LABELS[user.role as Role]}
                    </Badge>
                )}
            </div>
        </header>
    );
}
