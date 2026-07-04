"use client";

import { useEffect, useState } from "react";

import {
  cancelOrder,
  createPayment,
  getOrder,
  listOrders,
  listPayments,
  listRefunds,
  updateOrderStatus,
} from "@/lib/orders/api";
import type { Order, OrderListItem, OrderStatus, Payment, PaymentMethod, Refund } from "@/lib/orders/types";

type Tab = "orders" | "refunds";

const statusOptions: Array<{ value: OrderStatus; label: string }> = [
  { value: "pending", label: "در انتظار" },
  { value: "confirmed", label: "تأیید شده" },
  { value: "processing", label: "در حال پردازش" },
  { value: "ready", label: "آماده" },
  { value: "dispatched", label: "ارسال شده" },
  { value: "delivered", label: "تحویل شده" },
  { value: "completed", label: "تکمیل شده" },
  { value: "cancelled", label: "لغو شده" },
];

const paymentMethods: Array<{ value: PaymentMethod; label: string }> = [
  { value: "cash", label: "نقدی" },
  { value: "pos", label: "کارتخوان" },
  { value: "online", label: "آنلاین" },
  { value: "wallet", label: "کیف پول" },
];

export function OrdersManager() {
  const [activeTab, setActiveTab] = useState<Tab>("orders");
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [refunds, setRefunds] = useState<Refund[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [orderPayments, setOrderPayments] = useState<Payment[]>([]);
  const [status, setStatus] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  const [paymentForm, setPaymentForm] = useState({ method: "cash" as PaymentMethod, amount: "", reference_code: "" });
  const [showPaymentForm, setShowPaymentForm] = useState(false);

  async function loadOrders() {
    const params: Record<string, string> = {};
    if (statusFilter) params.status = statusFilter;
    const data = await listOrders(params);
    setOrders(data);
  }

  async function loadRefunds() {
    const data = await listRefunds();
    setRefunds(data);
  }

  useEffect(() => {
    loadOrders().catch(() => setStatus("دریافت سفارشات ناموفق بود."));
  }, [statusFilter]);

  async function handleSelectOrder(id: number) {
    try {
      const order = await getOrder(id);
      setSelectedOrder(order);
      const payments = await listPayments(id);
      setOrderPayments(payments);
    } catch {
      setStatus("دریافت جزئیات سفارش ناموفق بود.");
    }
  }

  async function handleStatusChange(orderId: number, newStatus: OrderStatus) {
    try {
      await updateOrderStatus(orderId, newStatus);
      setStatus("وضعیت به‌روزرسانی شد.");
      await loadOrders();
      if (selectedOrder?.id === orderId) {
        const updated = await getOrder(orderId);
        setSelectedOrder(updated);
      }
    } catch {
      setStatus("تغییر وضعیت ناموفق بود.");
    }
  }

  async function handleCancel(orderId: number) {
    try {
      await cancelOrder(orderId, "لغو توسط مدیر");
      setStatus("سفارش لغو شد.");
      await loadOrders();
      setSelectedOrder(null);
    } catch {
      setStatus("لغو سفارش ناموفق بود.");
    }
  }

  async function handleAddPayment(orderId: number) {
    try {
      await createPayment(orderId, {
        method: paymentForm.method,
        amount: Number(paymentForm.amount),
        reference_code: paymentForm.reference_code,
      });
      setStatus("پرداخت ثبت شد.");
      setPaymentForm({ method: "cash", amount: "", reference_code: "" });
      setShowPaymentForm(false);
      const payments = await listPayments(orderId);
      setOrderPayments(payments);
      const updated = await getOrder(orderId);
      setSelectedOrder(updated);
      await loadOrders();
    } catch {
      setStatus("ثبت پرداخت ناموفق بود.");
    }
  }

  const tabs: Array<{ key: Tab; label: string }> = [
    { key: "orders", label: "سفارشات" },
    { key: "refunds", label: "استردادها" },
  ];

  return (
    <div className="space-y-4">
      {status && <p className="rounded-2xl bg-white/10 p-3 text-sm">{status}</p>}

      <div className="flex gap-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => {
              setActiveTab(t.key);
              if (t.key === "refunds") loadRefunds();
            }}
            className={`rounded-2xl px-4 py-2 text-sm font-bold transition ${activeTab === t.key ? "bg-[#3c02cf] text-white" : "bg-white/5 text-white/60 hover:bg-white/10"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "orders" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm">
              <option value="">همه وضعیت‌ها</option>
              {statusOptions.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>

          {selectedOrder ? (
            <div className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-5">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-black">{selectedOrder.order_number}</h3>
                <button onClick={() => setSelectedOrder(null)} className="text-sm text-white/60 hover:text-white">بازگشت</button>
              </div>
              <div className="grid gap-3 md:grid-cols-3 text-sm">
                <div><span className="text-white/60">نوع:</span> {selectedOrder.order_type_display}</div>
                <div><span className="text-white/60">مشتری:</span> {selectedOrder.customer_name || selectedOrder.customer_phone}</div>
                <div><span className="text-white/60">شعبه:</span> {selectedOrder.branch_name}</div>
                <div><span className="text-white/60">وضعیت:</span> {selectedOrder.status_display}</div>
                <div><span className="text-white/60">جمع:</span> {Number(selectedOrder.total).toLocaleString()} تومان</div>
                <div><span className="text-white/60">پرداخت:</span> {selectedOrder.payment_status_display}</div>
              </div>

              {selectedOrder.items.length > 0 && (
                <div>
                  <p className="mb-2 text-sm font-bold">آیتم‌ها</p>
                  <table className="w-full text-sm">
                    <thead><tr className="text-white/60"><th className="py-1 text-right">نوع</th><th className="py-1 text-right">محصول</th><th className="py-1 text-right">تعداد</th><th className="py-1 text-right">قیمت واحد</th><th className="py-1 text-right">جمع</th></tr></thead>
                    <tbody>
                      {selectedOrder.items.map((item) => (
                        <tr key={item.id} className="border-t border-white/5">
                          <td className="py-1">{item.item_type}</td>
                          <td className="py-1">{item.product_name || item.stock_item_barcode || item.account_name || "-"}</td>
                          <td className="py-1">{item.quantity}</td>
                          <td className="py-1">{Number(item.unit_price).toLocaleString()}</td>
                          <td className="py-1">{Number(item.total_price).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                <select
                  onChange={(e) => { if (e.target.value) handleStatusChange(selectedOrder.id, e.target.value as OrderStatus); e.target.value = ""; }}
                  className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
                >
                  <option value="">تغییر وضعیت...</option>
                  {statusOptions.filter((s) => s.value !== selectedOrder.status).map((s) => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
                {selectedOrder.status !== "cancelled" && selectedOrder.status !== "completed" && (
                  <button onClick={() => handleCancel(selectedOrder.id)} className="rounded-2xl bg-red-600/80 px-4 py-2 text-sm font-bold hover:bg-red-600">لغو سفارش</button>
                )}
                <button onClick={() => setShowPaymentForm(!showPaymentForm)} className="rounded-2xl bg-[#3c02cf] px-4 py-2 text-sm font-bold hover:bg-[#3c02cf]/80">ثبت پرداخت</button>
              </div>

              {showPaymentForm && (
                <div className="flex flex-wrap gap-2 items-end">
                  <select value={paymentForm.method} onChange={(e) => setPaymentForm({ ...paymentForm, method: e.target.value as PaymentMethod })} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm">
                    {paymentMethods.map((m) => (<option key={m.value} value={m.value}>{m.label}</option>))}
                  </select>
                  <input type="number" placeholder="مبلغ" value={paymentForm.amount} onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm" />
                  <input type="text" placeholder="کد مرجع" value={paymentForm.reference_code} onChange={(e) => setPaymentForm({ ...paymentForm, reference_code: e.target.value })} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm" />
                  <button onClick={() => handleAddPayment(selectedOrder.id)} className="rounded-2xl bg-green-600/80 px-4 py-2 text-sm font-bold hover:bg-green-600">ثبت</button>
                </div>
              )}

              {orderPayments.length > 0 && (
                <div>
                  <p className="mb-2 text-sm font-bold">پرداخت‌ها</p>
                  <table className="w-full text-sm">
                    <thead><tr className="text-white/60"><th className="py-1 text-right">روش</th><th className="py-1 text-right">مبلغ</th><th className="py-1 text-right">وضعیت</th><th className="py-1 text-right">تاریخ</th></tr></thead>
                    <tbody>
                      {orderPayments.map((p) => (
                        <tr key={p.id} className="border-t border-white/5">
                          <td className="py-1">{p.method}</td>
                          <td className="py-1">{Number(p.amount).toLocaleString()}</td>
                          <td className="py-1">{p.status}</td>
                          <td className="py-1">{new Date(p.paid_at).toLocaleDateString("fa-IR")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-white/60"><th className="py-2 text-right">شماره</th><th className="py-2 text-right">نوع</th><th className="py-2 text-right">مشتری</th><th className="py-2 text-right">شعبه</th><th className="py-2 text-right">وضعیت</th><th className="py-2 text-right">جمع</th><th className="py-2 text-right">پرداخت</th><th className="py-2 text-right">تاریخ</th></tr></thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id} onClick={() => handleSelectOrder(o.id)} className="cursor-pointer border-t border-white/5 hover:bg-white/5">
                    <td className="py-2">{o.order_number}</td>
                    <td className="py-2">{o.order_type_display}</td>
                    <td className="py-2">{o.customer_name || o.customer_phone}</td>
                    <td className="py-2">{o.branch_name}</td>
                    <td className="py-2">{o.status_display}</td>
                    <td className="py-2">{Number(o.total).toLocaleString()}</td>
                    <td className="py-2">{o.payment_status_display}</td>
                    <td className="py-2">{new Date(o.created_at).toLocaleDateString("fa-IR")}</td>
                  </tr>
                ))}
                {orders.length === 0 && <tr><td colSpan={8} className="py-4 text-center text-white/40">سفارشی یافت نشد.</td></tr>}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === "refunds" && (
        <table className="w-full text-sm">
          <thead><tr className="text-white/60"><th className="py-2 text-right">سفارش</th><th className="py-2 text-right">مبلغ</th><th className="py-2 text-right">دلیل</th><th className="py-2 text-right">وضعیت</th><th className="py-2 text-right">تاریخ</th></tr></thead>
          <tbody>
            {refunds.map((r) => (
              <tr key={r.id} className="border-t border-white/5">
                <td className="py-2">{r.order_number}</td>
                <td className="py-2">{Number(r.amount).toLocaleString()}</td>
                <td className="py-2 max-w-[200px] truncate">{r.reason}</td>
                <td className="py-2">{r.status}</td>
                <td className="py-2">{new Date(r.created_at).toLocaleDateString("fa-IR")}</td>
              </tr>
            ))}
            {refunds.length === 0 && <tr><td colSpan={5} className="py-4 text-center text-white/40">استردادی یافت نشد.</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  );
}
