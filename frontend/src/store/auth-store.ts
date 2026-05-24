import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { User } from "@/lib/auth/types";

type PersistedAuthState = Pick<AuthState, "accessToken" | "refreshToken" | "user" | "activeRoleId">;

type AuthState = {
  accessToken?: string;
  refreshToken?: string;
  user?: User;
  activeRoleId?: string;
  hasHydrated: boolean;
  setTokens: (tokens: { accessToken: string; refreshToken: string }) => void;
  setUser: (user: User) => void;
  setActiveRole: (roleId: string) => void;
  setHasHydrated: (hasHydrated: boolean) => void;
  clearAuth: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist<AuthState, [], [], PersistedAuthState>(
    (set) => ({
      hasHydrated: false,
      setTokens: ({ accessToken, refreshToken }) => set({ accessToken, refreshToken }),
      setUser: (user) =>
        set((state) => ({
          user,
          activeRoleId: state.activeRoleId ?? (user.roles[0] ? String(user.roles[0].id) : undefined),
        })),
      setActiveRole: (activeRoleId) => set({ activeRoleId }),
      setHasHydrated: (hasHydrated) => set({ hasHydrated }),
      clearAuth: () => set({ accessToken: undefined, refreshToken: undefined, user: undefined, activeRoleId: undefined }),
    }),
    {
      name: "drgame-auth",
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
      partialize: (state): PersistedAuthState => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        activeRoleId: state.activeRoleId,
      }),
    },
  ),
);
