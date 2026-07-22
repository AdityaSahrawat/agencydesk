"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, Role } from "@/types";
import * as api from "@/services/api";

interface AuthContextType {
    user: User | null;
    token: string | null;
    agencyId: string | null;
    role: Role | null;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<User>;
    logout: () => void;
    setAgency: (agencyId: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [agencyId, setAgencyId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const initAuth = async () => {
        const storedToken = localStorage.getItem("token");
        const storedAgencyId = localStorage.getItem("agency_id");

        if (!storedToken) {
            setIsLoading(false);
            return;
        }

        setToken(storedToken);
        api.setAuthToken(storedToken);
        if (storedAgencyId) {
            setAgencyId(storedAgencyId);
            api.setAgencyIdHeader(storedAgencyId);
        }

        try {
            const profile = await api.getMe();
            // Profile returns memberships: [{ agency_id, agency_name, role, client_id }]
            const activeMembership = storedAgencyId
                ? profile.memberships?.find((m: any) => m.agency_id === storedAgencyId) || profile.memberships?.[0]
                : profile.memberships?.[0];

            const activeAgencyId = activeMembership?.agency_id || storedAgencyId || "";
            const activeRole: Role = activeMembership?.role || "agency_admin";

            if (activeAgencyId) {
                setAgencyId(activeAgencyId);
                localStorage.setItem("agency_id", activeAgencyId);
                api.setAgencyIdHeader(activeAgencyId);
            }

            setUser({
                id: profile.id,
                email: profile.email,
                name: profile.full_name || profile.email.split("@")[0],
                role: activeRole,
                agencyId: activeAgencyId,
                clientId: activeMembership?.client_id || undefined,
                createdAt: profile.created_at || new Date().toISOString(),
            });
        } catch (err) {
            console.error("Failed to load user profile:", err);
            localStorage.removeItem("token");
            localStorage.removeItem("agency_id");
            setToken(null);
            setUser(null);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        initAuth();
    }, []);

    const login = async (email: string, password: string) => {
        setIsLoading(true);
        try {
            const res = await api.login(email, password);
            const accessToken = res.access_token;
            localStorage.setItem("token", accessToken);
            setToken(accessToken);
            api.setAuthToken(accessToken);

            // Fetch me profile
            const profile = await api.getMe();
            const activeMembership = profile.memberships?.[0];
            const activeAgencyId = activeMembership?.agency_id || "";
            const activeRole: Role = activeMembership?.role || "agency_admin";

            if (activeAgencyId) {
                setAgencyId(activeAgencyId);
                localStorage.setItem("agency_id", activeAgencyId);
                api.setAgencyIdHeader(activeAgencyId);
            }

            const newUser: User = {
                id: profile.id,
                email: profile.email,
                name: profile.full_name || profile.email.split("@")[0],
                role: activeRole,
                agencyId: activeAgencyId,
                clientId: activeMembership?.client_id || undefined,
                createdAt: profile.created_at || new Date().toISOString(),
            };
            setUser(newUser);
            return newUser;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("agency_id");
        setToken(null);
        setUser(null);
        setAgencyId(null);
        api.clearAuth();
    };

    const setAgency = (newAgencyId: string) => {
        setAgencyId(newAgencyId);
        localStorage.setItem("agency_id", newAgencyId);
        api.setAgencyIdHeader(newAgencyId);
        if (user) {
            setUser({ ...user, agencyId: newAgencyId });
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                agencyId,
                role: user?.role || null,
                isLoading,
                login,
                logout,
                setAgency,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
