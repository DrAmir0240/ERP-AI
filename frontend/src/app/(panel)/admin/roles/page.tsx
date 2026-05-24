import { RolePermissionManager } from "@/components/admin/role-permission-manager";
import { PanelShell } from "@/components/layout/panel-shell";

export default function RolesPage() {
  return (
    <PanelShell title="مدیریت نقش‌ها" description="ماتریس دسترسی نقش‌ها بر اساس ماژول‌های Core قابل ویرایش است.">
      <RolePermissionManager />
    </PanelShell>
  );
}
