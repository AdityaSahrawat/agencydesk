"use client";

import { useAuth } from "@/providers/auth-provider";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { ROLE_LABELS, ROLE_COLORS } from "@/lib/constants";
import { Role } from "@/types";

export default function SettingsPage() {
    const { user, logout } = useAuth();

    return (
        <div>
            <Navbar title="Settings" subtitle="Manage your account and agency" />
            <div className="mx-auto max-w-2xl space-y-6 p-6">
                {/* Profile */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Profile</CardTitle>
                        <CardDescription>Update your personal information</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center gap-4">
                            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-xl font-medium text-primary">
                                {user?.name?.charAt(0)}
                            </div>
                            <div>
                                <p className="font-medium">{user?.name}</p>
                                <p className="text-sm text-muted-foreground">{user?.email}</p>
                                {user && user.role && <Badge className={ROLE_COLORS[user.role as Role]} variant="secondary">{ROLE_LABELS[user.role as Role]}</Badge>}
                            </div>
                        </div>
                        <Separator />
                        <div className="space-y-2">
                            <Label htmlFor="name">Full Name</Label>
                            <Input id="name" defaultValue={user?.name} />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input id="email" type="email" defaultValue={user?.email} disabled />
                        </div>
                        <Button onClick={() => toast.success("Profile saved (demo)")} size="sm">Save Changes</Button>
                    </CardContent>
                </Card>

                {/* Password */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Password</CardTitle>
                        <CardDescription>Change your password</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="current">Current Password</Label>
                            <Input id="current" type="password" placeholder="••••••••" />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="new">New Password</Label>
                            <Input id="new" type="password" placeholder="••••••••" />
                        </div>
                        <Button onClick={() => toast.success("Password changed (demo)")} size="sm">Update Password</Button>
                    </CardContent>
                </Card>

                {/* Danger Zone */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base text-destructive">Session</CardTitle>
                        <CardDescription>Sign out of your account</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button variant="outline" size="sm" onClick={logout}>
                            Sign Out
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
