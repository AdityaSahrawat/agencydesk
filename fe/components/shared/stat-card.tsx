import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
    label: string;
    value: string | number;
    icon: LucideIcon;
    accent?: "default" | "blue" | "green" | "amber" | "red";
}

const accentClasses = {
    default: "text-muted-foreground",
    blue: "text-blue-600",
    green: "text-green-600",
    amber: "text-amber-600",
    red: "text-red-600",
};

export function StatCard({ label, value, icon: Icon, accent = "default" }: StatCardProps) {
    return (
        <Card>
            <CardContent className="flex items-center justify-between p-5">
                <div>
                    <p className="text-sm text-muted-foreground">{label}</p>
                    <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
                </div>
                <Icon className={cn("h-8 w-8", accentClasses[accent])} />
            </CardContent>
        </Card>
    );
}
