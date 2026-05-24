"use client";

import { useEffect, useState } from "react";

import type { Role } from "@/lib/auth/types";
import { listRoles, updateRolePermissions } from "@/lib/core/api";

export function RolePermissionManager() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [status, setStatus] = useState("");

  const selectedRole = roles.find((role) => role.id === selectedRoleId) ?? roles[0];

  async function loadRoles() {
    const data = await listRoles();
    setRoles(data);
    setSelectedRoleId((current) => current ?? data[0]?.id ?? null);
  }

  useEffect(() => {
    loadRoles().catch(() => setStatus("دریافت نقش‌ها ناموفق بود."));
  }, []);

  async function togglePermission(permissionId: number, field: "can_read" | "can_write") {
    if (!selectedRole) return;
    const permissions = selectedRole.permissions.map((permission) => ({
      module_id: permission.module.id,
      can_read: permission.id === permissionId && field === "can_read" ? !permission.can_read : permission.can_read,
      can_write: permission.id === permissionId && field === "can_write" ? !permission.can_write : permission.can_write,
    }));
    try {
      await updateRolePermissions(selectedRole.id, permissions);
      setStatus("ماتریس دسترسی ذخیره شد.");
      await loadRoles();
    } catch {
      setStatus("ذخیره ماتریس دسترسی ناموفق بود.");
    }
  }

  if (!roles.length) {
    return <p className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/60">نقشی برای نمایش وجود ندارد.</p>;
  }

  return (
    <section className="space-y-5">
      <label className="block">
        <span className="mb-2 block text-sm font-semibold text-white/70">انتخاب نقش</span>
        <select className="w-full rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => setSelectedRoleId(Number(event.target.value))} value={selectedRole?.id ?? ""}>
          {roles.map((role) => (
            <option key={role.id} value={role.id}>{role.display_name}</option>
          ))}
        </select>
      </label>
      {status ? <p className="text-sm text-white/70">{status}</p> : null}
      <div className="overflow-hidden rounded-3xl border border-white/10">
        {selectedRole?.permissions.map((permission) => (
          <div className="grid grid-cols-[1fr_auto_auto] items-center gap-3 border-b border-white/10 bg-white/5 p-4 last:border-b-0" key={permission.id}>
            <span className="font-bold">{permission.module.display_name}</span>
            <label className="flex items-center gap-2 text-sm text-white/70">
              <input checked={permission.can_read} onChange={() => togglePermission(permission.id, "can_read")} type="checkbox" />
              خواندن
            </label>
            <label className="flex items-center gap-2 text-sm text-white/70">
              <input checked={permission.can_write} onChange={() => togglePermission(permission.id, "can_write")} type="checkbox" />
              نوشتن
            </label>
          </div>
        ))}
      </div>
    </section>
  );
}
