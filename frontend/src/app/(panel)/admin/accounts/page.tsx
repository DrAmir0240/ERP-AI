import { AccountsManager } from "@/components/admin/accounts-manager";
import { PanelShell } from "@/components/layout/panel-shell";

export default function AccountsPage() {
  return (
    <PanelShell title="مدیریت اکانت‌ها" description="اکانت‌های PS/Xbox/Nintendo، بازی‌ها، لاگ فروش و محاسبه قیمت.">
      <AccountsManager />
    </PanelShell>
  );
}
