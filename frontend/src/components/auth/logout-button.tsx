"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { logout } from "@/lib/auth/api";
import { useAuthStore } from "@/store/auth-store";

export function LogoutButton() {
  const router = useRouter();
  const refreshToken = useAuthStore((state) => state.refreshToken);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const [isLoading, setIsLoading] = useState(false);

  async function handleLogout() {
    setIsLoading(true);
    try {
      if (refreshToken) {
        await logout(refreshToken);
      }
    } finally {
      clearAuth();
      router.replace("/login");
    }
  }

  return (
    <button
      className="rounded-2xl border border-white/15 px-4 py-2 text-sm font-bold text-white/80 transition hover:bg-white/10 disabled:opacity-60"
      disabled={isLoading}
      onClick={handleLogout}
      type="button"
    >
      خروج
    </button>
  );
}
