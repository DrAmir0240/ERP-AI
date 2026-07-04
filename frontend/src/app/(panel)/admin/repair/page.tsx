import { RepairManager } from "@/components/admin/repair-manager";
import { PanelShell } from "@/components/layout/panel-shell";

export default function RepairPage() {
  return (
    <PanelShell title="مدیریت تعمیرات" description="تعمیرات، تکنسین‌ها و تنظیمات قیمت‌گذاری.">
      <RepairManager />
    </PanelShell>
  );
}
