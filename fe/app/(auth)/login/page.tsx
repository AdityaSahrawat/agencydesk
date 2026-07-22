"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Layers, Loader2, AlertCircle, Mail, Lock, ArrowRight, ShieldCheck, UserCheck, Briefcase } from "lucide-react";
import { toast } from "sonner";

const demoAccounts = [
    {
        label: "Agency Admin",
        email: "alice@agencyalpha.com",
        password: "Password123!",
        role: "admin",
        badge: "Full Access",
        icon: ShieldCheck,
        badgeColor: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    },
    {
        label: "Agency Member",
        email: "bob@agencyalpha.com",
        password: "Password123!",
        role: "member",
        badge: "Team Access",
        icon: Briefcase,
        badgeColor: "bg-purple-500/10 text-purple-500 border-purple-500/20",
    },
    {
        label: "Client Portal",
        email: "john@gmail.com",
        password: "Password123!",
        role: "client",
        badge: "Client Portal",
        icon: UserCheck,
        badgeColor: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    },
];

export default function LoginPage() {
    const router = useRouter();
    const { login } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const loggedUser = await login(email, password);
            toast.success("Signed in successfully!");
            if (loggedUser?.role === "client_user") {
                router.push("/portal");
            } else {
                router.push("/agency/dashboard");
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Invalid email or password");
        } finally {
            setLoading(false);
        }
    };

    const fillDemo = (acc: typeof demoAccounts[0]) => {
        setEmail(acc.email);
        setPassword(acc.password);
    };

    return (
        <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950 px-4 py-12 text-slate-100 selection:bg-indigo-500 selection:text-white">
            {/* Background Gradient Blurs */}
            <div className="pointer-events-none absolute -left-40 -top-40 h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-purple-600/20 blur-3xl" />
            
            <div className="relative w-full max-w-lg space-y-8">
                {/* Header Logo */}
                <div className="flex flex-col items-center justify-center text-center">
                    <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
                        <Layers className="h-7 w-7 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                        AgencyDesk
                    </h1>
                    <p className="mt-2 text-sm text-slate-400">
                        Multi-tenant Client & Project Management Platform
                    </p>
                </div>

                {/* Login Card */}
                <Card className="border-slate-800/80 bg-slate-900/80 shadow-2xl backdrop-blur-xl">
                    <CardHeader className="space-y-1 text-center sm:text-left">
                        <CardTitle className="text-xl font-semibold text-white">Sign in to your workspace</CardTitle>
                        <CardDescription className="text-slate-400">
                            Enter your email credentials to access your agency or client portal.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {error && (
                                <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
                                    <AlertCircle className="h-4 w-4 shrink-0" />
                                    <span>{error}</span>
                                </div>
                            )}

                            <div className="space-y-2">
                                <Label htmlFor="email" className="text-xs font-medium uppercase tracking-wider text-slate-300">
                                    Work Email
                                </Label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                                    <Input
                                        id="email"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="user@agency.com"
                                        className="border-slate-800 bg-slate-950/60 pl-9 text-slate-100 placeholder:text-slate-600 focus-visible:ring-indigo-500"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password" className="text-xs font-medium uppercase tracking-wider text-slate-300">
                                    Password
                                </Label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                                    <Input
                                        id="password"
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="••••••••"
                                        className="border-slate-800 bg-slate-950/60 pl-9 text-slate-100 placeholder:text-slate-600 focus-visible:ring-indigo-500"
                                        required
                                    />
                                </div>
                            </div>

                            <Button
                                type="submit"
                                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 py-5 font-semibold text-white shadow-md shadow-indigo-500/20 hover:from-indigo-600 hover:to-purple-700 disabled:opacity-50"
                                disabled={loading}
                            >
                                {loading ? (
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                ) : (
                                    <span className="flex items-center justify-center gap-2">
                                        Sign In <ArrowRight className="h-4 w-4" />
                                    </span>
                                )}
                            </Button>
                        </form>

                        {/* Quick Demo Login Cards */}
                        <div className="space-y-3 pt-2">
                            <div className="relative flex items-center justify-center">
                                <div className="w-full border-t border-slate-800" />
                                <span className="absolute bg-slate-900 px-3 text-xs font-medium text-slate-500">
                                    OR ONE-CLICK DEMO ACCOUNTS
                                </span>
                            </div>

                            <div className="grid gap-2 sm:grid-cols-3">
                                {demoAccounts.map((acc) => {
                                    const Icon = acc.icon;
                                    return (
                                        <button
                                            key={acc.email}
                                            type="button"
                                            onClick={() => fillDemo(acc)}
                                            className="group flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-950/50 p-3 text-left transition-all hover:border-indigo-500/50 hover:bg-slate-900 hover:shadow-md"
                                        >
                                            <div className="flex items-center justify-between">
                                                <Icon className="h-4 w-4 text-slate-400 group-hover:text-indigo-400" />
                                                <Badge variant="outline" className={`text-[10px] ${acc.badgeColor}`}>
                                                    {acc.badge}
                                                </Badge>
                                            </div>
                                            <div className="mt-3">
                                                <p className="text-xs font-semibold text-slate-200 group-hover:text-white">
                                                    {acc.label}
                                                </p>
                                                <p className="truncate text-[11px] text-slate-500">
                                                    {acc.email}
                                                </p>
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Footer note */}
                <p className="text-center text-xs text-slate-500">
                    AgencyDesk Multi-Tenant Architecture &bull; Secure JWT Auth & Isolation
                </p>
            </div>
        </div>
    );
}
