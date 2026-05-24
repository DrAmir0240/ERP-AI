"use client";

import { useEffect } from "react";

import { getCurrentUser } from "@/lib/auth/api";
import { useAuthStore } from "@/store/auth-store";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const accessToken = useAuthStore((state) => state.accessToken);
  const setUser = useAuthStore((state) => state.setUser);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  useEffect(() => {
    if (!accessToken) return;

    getCurrentUser()
      .then(setUser)
      .catch(() => clearAuth());
  }, [accessToken, clearAuth, setUser]);

  return children;
}
