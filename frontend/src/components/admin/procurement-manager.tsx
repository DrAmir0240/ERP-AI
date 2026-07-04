"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  createPurchaseRequest,
  createSupplier,
  deleteSupplier,
  listPurchaseOrders,
  listPurchaseRequests,
  listSuppliers,
  updatePurchaseRequestStatus,
  updateSupplier,
} from "@/lib/procurement/api";
import type { PurchaseOrder, PurchaseRequest, PurchaseRequestStatus, SupplierListItem } from "@/lib/procurement/types";

type Tab = "suppliers" | "requests" | "purchase-orders";

const requestStatusOptions: Array<{ value: PurchaseRequestStatus; label: string }> = [
  { value: "draft", label: "پیش‌نویس" },
  { value: "submitted", label: "ارسال شده" },
  { value: "approved", label: "تأیید شده" },
  { value: "rejected", label: "رد شده" },
  { value: "purchased", label: "خریداری شده" },
];

const emptySupplierForm = { company_name: "", contact_person: "", phone: "", email: "", address: "", notes: "", is_active: true };

export function ProcurementManager() {
  const [activeTab, setActiveTab] = useState<Tab>("suppliers");
  const [suppliers, setSuppliers] = useState<SupplierListItem[]>([]);
  const [requests, setRequests] = useState<PurchaseRequest[]>([]);
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [status, setStatus] = useState("");

  const [supplierForm, setSupplierForm] = useState(emptySupplierForm);
  const [editingSupplierId, setEditingSupplierId] = useState<number | null>(null);

  const [requestStatusFilter, setRequestStatusFilter] = useState<string>("");

  async function loadSuppliers() {
    const data = await listSuppliers();
    setSuppliers(data);
  }

  async function loadRequests() {
    const params: Record<string, string> = {};
    if (requestStatusFilter) params.status = requestStatusFilter;
    const data = await listPurchaseRequests(params);
    setRequests(data);
  }

  async function loadPurchaseOrders() {
    const data = await listPurchaseOrders();
    setPurchaseOrders(data);
  }

  useEffect(() => {
    loadSuppliers().catch(() => setStatus("دریافت تأمین‌کنندگان ناموفق بود."));
  }, []);

  async function handleSupplierSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      if (editingSupplierId) {
        await updateSupplier(editingSupplierId, supplierForm);
        setStatus("تأمین‌کننده ویرایش شد.");
      } else {
        await createSupplier(supplierForm);
        setStatus("تأمین‌کننده ایجاد شد.");
      }
      setSupplierForm(emptySupplierForm);
      setEditingSupplierId(null);
      await loadSuppliers();
    } catch {
      setStatus("ذخیره تأمین‌کننده ناموفق بود.");
    }
  }

  function startSupplierEdit(s: SupplierListItem) {
    setSupplierForm({
      company_name: s.company_name,
      contact_person: s.contact_person,
      phone: s.phone,
      email: "",
      address: "",
      notes: "",
      is_active: s.is_active,
    });
    setEditingSupplierId(s.id);
  }

  async function handleDeleteSupplier(id: number) {
    try {
      await deleteSupplier(id);
      setStatus("تأمین‌کننده حذف شد.");
      await loadSuppliers();
    } catch {
      setStatus("حذف ناموفق بود.");
    }
  }

  async function handleRequestStatusChange(id: number, newStatus: PurchaseRequestStatus) {
    try {
      await updatePurchaseRequestStatus(id, newStatus);
      setStatus("وضعیت درخواست به‌روزرسانی شد.");
      await loadRequests();
    } catch {
      setStatus("تغییر وضعیت ناموفق بود.");
    }
  }

  const tabs: Array<{ key: Tab; label: string }> = [
    { key: "suppliers", label: "تأمین‌کنندگان" },
    { key: "requests", label: "درخواست خرید" },
    { key: "purchase-orders", label: "سفارشات خرید" },
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
              if (t.key === "requests") loadRequests();
              if (t.key === "purchase-orders") loadPurchaseOrders();
            }}
            className={`rounded-2xl px-4 py-2 text-sm font-bold transition ${activeTab === t.key ? "bg-[#3c02cf] text-white" : "bg-white/5 text-white/60 hover:bg-white/10"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "suppliers" && (
        <div className="space-y-4">
          <form onSubmit={handleSupplierSubmit} className="rounded-3xl border border-white/10 bg-white/5 p-5 space-y-3">
            <h3 className="text-sm font-bold">{editingSupplierId ? "ویرایش تأمین‌کننده" : "تأمین‌کننده جدید"}</h3>
            <div className="grid gap-3 md:grid-cols-2">
              <input type="text" placeholder="نام شرکت" value={supplierForm.company_name} onChange={(e) => setSupplierForm({ ...supplierForm, company_name: e.target.value })} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm" required />
              <input type="text" placeholder="شخص رابط" value={supplierForm.contact_person} onChange={(e) => setSupplierForm({ ...supplierForm, contact_person: e.target.value })} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm" />
              <input type="text" placeholder="تلفن" value={supplierForm.phone} onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm" />
              <input type="email" placeholder="ایمیل" value={supplierForm.email} onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm" />
            </div>
            <textarea placeholder="آدرس" value={supplierForm.address} onChange={(e) => setSupplierForm({ ...supplierForm, address: e.target.value })} className="w-full rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm" rows={2} />
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={supplierForm.is_active} onChange={(e) => setSupplierForm({ ...supplierForm, is_active: e.target.checked })} />
                فعال
              </label>
              <button type="submit" className="rounded-2xl bg-[#3c02cf] px-4 py-2 text-sm font-bold hover:bg-[#3c02cf]/80">{editingSupplierId ? "ویرایش" : "ایجاد"}</button>
              {editingSupplierId && (
                <button type="button" onClick={() => { setSupplierForm(emptySupplierForm); setEditingSupplierId(null); }} className="text-sm text-white/60 hover:text-white">انصراف</button>
              )}
            </div>
          </form>

          <table className="w-full text-sm">
            <thead><tr className="text-white/60"><th className="py-2 text-right">نام شرکت</th><th className="py-2 text-right">رابط</th><th className="py-2 text-right">تلفن</th><th className="py-2 text-right">موجودی</th><th className="py-2 text-right">سفارشات</th><th className="py-2 text-right">عملیات</th></tr></thead>
            <tbody>
              {suppliers.map((s) => (
                <tr key={s.id} className="border-t border-white/5">
                  <td className="py-2">{s.company_name}</td>
                  <td className="py-2">{s.contact_person}</td>
                  <td className="py-2">{s.phone}</td>
                  <td className="py-2">{Number(s.balance).toLocaleString()}</td>
                  <td className="py-2">{s.order_count}</td>
                  <td className="py-2 space-x-2">
                    <button onClick={() => startSupplierEdit(s)} className="text-blue-400 hover:text-blue-300">ویرایش</button>
                    <button onClick={() => handleDeleteSupplier(s.id)} className="text-red-400 hover:text-red-300">حذف</button>
                  </td>
                </tr>
              ))}
              {suppliers.length === 0 && <tr><td colSpan={6} className="py-4 text-center text-white/40">تأمین‌کننده‌ای یافت نشد.</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "requests" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <select value={requestStatusFilter} onChange={(e) => { setRequestStatusFilter(e.target.value); }} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm">
              <option value="">همه وضعیت‌ها</option>
              {requestStatusOptions.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
            <button onClick={() => loadRequests()} className="rounded-2xl bg-white/10 px-3 py-2 text-sm hover:bg-white/20">بارگذاری</button>
          </div>

          <div className="space-y-3">
            {requests.map((r) => (
              <div key={r.id} className="rounded-3xl border border-white/10 bg-white/5 p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold">{r.request_number}</h4>
                  <span className="text-sm text-white/60">{r.status_display}</span>
                </div>
                <div className="grid gap-2 md:grid-cols-3 text-sm">
                  <div><span className="text-white/60">شعبه:</span> {r.branch_name}</div>
                  <div><span className="text-white/60">درخواست‌دهنده:</span> {r.requested_by_phone}</div>
                  <div><span className="text-white/60">تاریخ:</span> {new Date(r.created_at).toLocaleDateString("fa-IR")}</div>
                </div>
                {r.reason && <p className="text-sm text-white/80">{r.reason}</p>}
                <div className="flex flex-wrap gap-2">
                  <select
                    onChange={(e) => { if (e.target.value) handleRequestStatusChange(r.id, e.target.value as PurchaseRequestStatus); e.target.value = ""; }}
                    className="rounded-2xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs"
                  >
                    <option value="">تغییر وضعیت...</option>
                    {requestStatusOptions.filter((s) => s.value !== r.status).map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
            {requests.length === 0 && <p className="py-4 text-center text-white/40">درخواست خریدی یافت نشد.</p>}
          </div>
        </div>
      )}

      {activeTab === "purchase-orders" && (
        <table className="w-full text-sm">
          <thead><tr className="text-white/60"><th className="py-2 text-right">شماره</th><th className="py-2 text-right">تأمین‌کننده</th><th className="py-2 text-right">شعبه</th><th className="py-2 text-right">مبلغ</th><th className="py-2 text-right">روش پرداخت</th><th className="py-2 text-right">تاریخ</th></tr></thead>
          <tbody>
            {purchaseOrders.map((po) => (
              <tr key={po.id} className="border-t border-white/5">
                <td className="py-2">{po.purchase_number}</td>
                <td className="py-2">{po.supplier_name}</td>
                <td className="py-2">{po.branch_name}</td>
                <td className="py-2">{Number(po.total_amount).toLocaleString()}</td>
                <td className="py-2">{po.payment_method_display}</td>
                <td className="py-2">{new Date(po.purchased_at).toLocaleDateString("fa-IR")}</td>
              </tr>
            ))}
            {purchaseOrders.length === 0 && <tr><td colSpan={6} className="py-4 text-center text-white/40">سفارش خریدی یافت نشد.</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  );
}
