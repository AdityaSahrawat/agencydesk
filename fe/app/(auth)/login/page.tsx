"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ChevronsLeftRight, Loader2, AlertCircle } from "lucide-react";
import { toast } from "sonner";

const demoAccounts = [
    { label: "Agency Admin", email: "admin@technova.com", password: "demo" },
    { label: "Agency Member", email: "rahul@technova.com", password: "demo" },
    { label: "Client User", email: "john@nike.com", password: "demo" },
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
            await login(email, password);
            toast.success("Welcome back!");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Login failed");
        } finally {
            setLoading(false);
        }
    };

    const fillDemo = (acc: { email: string; password: string }) => {
        setEmail(acc.email);
        setPassword(acc.password);
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4">
            <div className="w-full max-w-md">
                <div className="mb-6 flex items-center justify-center gap-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                        <ChevronsLeftRight className="h-5 w-5" />
                    </div>
                    <span className="text-2xl font-semibold tracking-tight">AgencyDesk</span>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>Sign in</CardTitle>
                        <CardDescription>Enter your credentials to access your workspace</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {error && (
                                <div className="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                                    <AlertCircle className="h-4 w-4" />
                                    {error}
                                </div>
                            )}
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="you@company.com"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                            <Button type="submit" className="w-full" disabled={loading}>
                                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Sign in
                            </Button>
                        </form>

                        <div className="mt-6 border-t border-border pt-4">
                            <p className="mb-2 text-xs font-medium text-muted-foreground">Demo accounts (click to fill):</p>
                            <div className="space-y-1.5">
                                {demoAccounts.map((acc) => (
                                    <button
                                        key={acc.email}
                                        onClick={() => fillDemo(acc)}
                                        className="flex w-full items-center justify-between rounded-md border border-border px-3 py-2 text-left text-xs hover:bg-accent"
                                    >
                                        <span className="font-medium">{acc.label}</span>
                                        <span className="text-muted-foreground">{acc.email}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
