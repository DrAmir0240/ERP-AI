"use client";

import { useAuthStore } from "@/store/auth-store";

export function RoleSwitcher() {
  const user = useAuthStore((state) => state.user);
  const activeRoleId = useAuthStore((state) => state.activeRoleId);
  const setActiveRole = useAuthStore((state) => state.setActiveRole);

  const roles = user?.roles ?? [];
  const activeRole = roles.find((item) => String(item.id) === activeRoleId);
  const selectedRoleId = activeRole ? String(activeRole.id) : String(roles[0]?.id ?? "");

  if (!roles.length) {
    return <p className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/60">نقشی برای این کاربر ثبت نشده است.</p>;
  }

  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-white/70">نقش فعال</span>
      <select
        className="w-full rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 text-white outline-none transition focus:border-white/40"
        value={selectedRoleId}
        onChange={(event) => setActiveRole(event.target.value)}
      >
        {roles.map((item) => (
          <option key={item.id} value={String(item.id)}>
            {item.role.display_name}
            {item.branch ? ` — ${item.branch.name}` : " — سراسری"}
          </option>
        ))}
      </select>
    </label>
  );
}
