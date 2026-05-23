import { create } from "zustand";

type AuthState = {
  accessToken?: string;
  refreshToken?: string;
  activeRole?: string;
  setTokens: (tokens: { accessToken: string; refreshToken: string }) => void;
  setActiveRole: (role: string) => void;
  clearAuth: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  setTokens: ({ accessToken, refreshToken }) => set({ accessToken, refreshToken }),
  setActiveRole: (activeRole) => set({ activeRole }),
  clearAuth: () => set({ accessToken: undefined, refreshToken: undefined, activeRole: undefined }),
}));
