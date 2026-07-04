import { OrdersManager } from "@/components/admin/orders-manager";
import { PanelShell } from "@/components/layout/panel-shell";

export default function OrdersPage() {
  return (
    <PanelShell title="مدیریت سفارشات" description="سفارشات، پرداخت‌ها، فاکتورها و استردادها.">
      <OrdersManager />
    </PanelShell>
  );
}
