"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuthStore } from "@/store/auth-store";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const accessToken = useAuthStore((state) => state.accessToken);
  const hasHydrated = useAuthStore((state) => state.hasHydrated);

  useEffect(() => {
    if (hasHydrated && !accessToken) {
      router.replace("/login");
    }
  }, [accessToken, hasHydrated, router]);

  if (!hasHydrated) {
    return <main className="flex min-h-screen items-center justify-center text-sm text-slate-500">در حال آماده‌سازی نشست...</main>;
  }

  if (!accessToken) {
    return null;
  }

  return children;
}
