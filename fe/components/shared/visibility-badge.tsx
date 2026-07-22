import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Lock, Eye } from "lucide-react";

interface VisibilityBadgeProps {
    internal: boolean;
    className?: string;
}

export function VisibilityBadge({ internal, className }: VisibilityBadgeProps) {
    if (!internal) return null;
    return (
        <Badge variant="outline" className={cn("gap-1 border-amber-200 bg-amber-50 text-amber-700", className)}>
            <Lock className="h-3 w-3" />
            Internal
        </Badge>
    );
}

export function ClientVisibleBadge({ className }: { className?: string }) {
    return (
        <Badge variant="outline" className={cn("gap-1 border-blue-200 bg-blue-50 text-blue-700", className)}>
            <Eye className="h-3 w-3" />
            Client Visible
        </Badge>
    );
}
