import { ProcurementManager } from "@/components/admin/procurement-manager";
import { PanelShell } from "@/components/layout/panel-shell";

export default function ProcurementPage() {
  return (
    <PanelShell title="مدیریت تدارکات" description="تأمین‌کنندگان، درخواست‌های خرید و سفارشات خرید.">
      <ProcurementManager />
    </PanelShell>
  );
}
