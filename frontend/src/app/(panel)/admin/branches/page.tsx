import { BranchManager } from "@/components/admin/branch-manager";
import { PanelShell } from "@/components/layout/panel-shell";

export default function BranchesPage() {
  return (
    <PanelShell title="مدیریت شعبه‌ها" description="CRUD شعبه‌ها از API Core انجام می‌شود.">
      <BranchManager />
    </PanelShell>
  );
}
