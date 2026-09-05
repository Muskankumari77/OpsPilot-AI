"use client";

import { createContext, useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { clearToken, getActiveOrgId, setActiveOrgId, setToken } from "@/lib/auth";
import type { CurrentUser, TokenResponse } from "@/types/auth";

interface AuthContextValue {
  user: CurrentUser | null;
  isLoading: boolean;
  activeOrgId: number | null;
  login: (email: string, password: string) => Promise<void>;
  register: (
    fullName: string,
    email: string,
    password: string,
    organizationName: string
  ) => Promise<void>;
  logout: () => void;
  switchOrganization: (orgId: number) => void;
  refreshUser: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeOrgId, setActiveOrgIdState] = useState<number | null>(null);
  const router = useRouter();

  const loadUser = useCallback(async () => {
    try {
      const me = await apiFetch<CurrentUser>("/auth/me");
      setUser(me);

      // If no org is active yet, default to the first membership.
      const existingOrgId = getActiveOrgId();
      if (existingOrgId) {
        setActiveOrgIdState(existingOrgId);
      } else if (me.memberships.length > 0) {
        const firstOrgId = me.memberships[0].organization.id;
        setActiveOrgId(firstOrgId);
        setActiveOrgIdState(firstOrgId);
      }
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await apiFetch<TokenResponse>("/auth/login", {
        method: "POST",
        auth: false,
        body: JSON.stringify({ email, password }),
      });
      setToken(access_token);
      await loadUser();
      router.push("/dashboard");
    },
    [loadUser, router]
  );

  const register = useCallback(
    async (fullName: string, email: string, password: string, organizationName: string) => {
      const { access_token } = await apiFetch<TokenResponse>("/auth/register", {
        method: "POST",
        auth: false,
        body: JSON.stringify({
          full_name: fullName,
          email,
          password,
          organization_name: organizationName,
        }),
      });
      setToken(access_token);
      await loadUser();
      router.push("/dashboard");
    },
    [loadUser, router]
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    setActiveOrgIdState(null);
    router.push("/login");
  }, [router]);

  const switchOrganization = useCallback((orgId: number) => {
    setActiveOrgId(orgId);
    setActiveOrgIdState(orgId);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        activeOrgId,
        login,
        register,
        logout,
        switchOrganization,
        refreshUser: loadUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
