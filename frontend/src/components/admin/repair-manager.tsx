"use client";

import { useEffect, useState } from "react";

import {
  acceptRepair,
  changeRepairStatus,
  completeRepair,
  customerDecision,
  getRepairSettings,
  listRepairOrders,
  setRepairPrice,
  updateRepairSettings,
} from "@/lib/repair/api";
import type { RepairOrder, RepairSettings, RepairStatus } from "@/lib/repair/types";

type Tab = "repairs" | "settings";

const repairStatusOptions: Array<{ value: RepairStatus; label: string }> = [
  { value: "pending", label: "در انتظار" },
  { value: "received", label: "دریافت شده" },
  { value: "under_review", label: "در بررسی" },
  { value: "price_set", label: "قیمت‌گذاری شده" },
  { value: "approved", label: "تأیید مشتری" },
  { value: "rejected", label: "رد مشتری" },
  { value: "in_repair", label: "در حال تعمیر" },
  { value: "repaired", label: "تعمیر شده" },
  { value: "dispatched", label: "ارسال شده" },
  { value: "completed", label: "تکمیل شده" },
  { value: "cancelled", label: "لغو شده" },
];

export function RepairManager() {
  const [activeTab, setActiveTab] = useState<Tab>("repairs");
  const [repairs, setRepairs] = useState<RepairOrder[]>([]);
  const [settings, setSettings] = useState<RepairSettings | null>(null);
  const [status, setStatus] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [markupInput, setMarkupInput] = useState("");
  const [priceInput, setPriceInput] = useState<Record<number, string>>({});

  async function loadRepairs() {
    const params: Record<string, string> = {};
    if (statusFilter) params.status = statusFilter;
    const data = await listRepairOrders(params);
    setRepairs(data);
  }

  async function loadSettings() {
    const data = await getRepairSettings();
    setSettings(data);
    setMarkupInput(data.markup_percent);
  }

  useEffect(() => {
    loadRepairs().catch(() => setStatus("دریافت تعمیرات ناموفق بود."));
  }, [statusFilter]);

  async function handleAccept(id: number) {
    try {
      await acceptRepair(id);
      setStatus("تعمیر پذیرش شد.");
      await loadRepairs();
    } catch {
      setStatus("پذیرش ناموفق بود.");
    }
  }

  async function handleSetPrice(id: number) {
    const price = Number(priceInput[id]);
    if (!price) return;
    try {
      await setRepairPrice(id, price);
      setStatus("قیمت ثبت شد.");
      setPriceInput((prev) => ({ ...prev, [id]: "" }));
      await loadRepairs();
    } catch {
      setStatus("ثبت قیمت ناموفق بود.");
    }
  }

  async function handleCustomerDecision(id: number, approved: boolean) {
    try {
      await customerDecision(id, approved);
      setStatus(approved ? "مشتری تأیید کرد." : "مشتری رد کرد.");
      await loadRepairs();
    } catch {
      setStatus("ثبت تصمیم ناموفق بود.");
    }
  }

  async function handleComplete(id: number) {
    try {
      await completeRepair(id);
      setStatus("تعمیر تکمیل شد.");
      await loadRepairs();
    } catch {
      setStatus("تکمیل ناموفق بود.");
    }
  }

  async function handleStatusChange(id: number, newStatus: RepairStatus) {
    try {
      await changeRepairStatus(id, newStatus);
      setStatus("وضعیت به‌روزرسانی شد.");
      await loadRepairs();
    } catch {
      setStatus("تغییر وضعیت ناموفق بود.");
    }
  }

  async function handleSaveSettings() {
    try {
      await updateRepairSettings(Number(markupInput));
      setStatus("تنظیمات ذخیره شد.");
      await loadSettings();
    } catch {
      setStatus("ذخیره تنظیمات ناموفق بود.");
    }
  }

  const tabs: Array<{ key: Tab; label: string }> = [
    { key: "repairs", label: "تعمیرات" },
    { key: "settings", label: "تنظیمات" },
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
              if (t.key === "settings") loadSettings();
            }}
            className={`rounded-2xl px-4 py-2 text-sm font-bold transition ${activeTab === t.key ? "bg-[#3c02cf] text-white" : "bg-white/5 text-white/60 hover:bg-white/10"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "repairs" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm">
              <option value="">همه وضعیت‌ها</option>
              {repairStatusOptions.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>

          <div className="space-y-3">
            {repairs.map((r) => (
              <div key={r.id} className="rounded-3xl border border-white/10 bg-white/5 p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold">{r.device_model} ({r.device_type})</h4>
                  <span className="text-sm text-white/60">{r.status}</span>
                </div>
                <p className="text-sm text-white/80">{r.issue_description}</p>
                <div className="grid gap-2 md:grid-cols-3 text-sm">
                  <div><span className="text-white/60">تکنسین:</span> {r.technician_phone || "تعیین نشده"}</div>
                  <div><span className="text-white/60">قیمت نهایی:</span> {Number(r.final_price).toLocaleString()} تومان</div>
                  <div><span className="text-white/60">تأیید مشتری:</span> {r.customer_approved === null ? "در انتظار" : r.customer_approved ? "تأیید" : "رد"}</div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {r.status === "pending" && (
                    <button onClick={() => handleAccept(r.id)} className="rounded-2xl bg-blue-600/80 px-3 py-1.5 text-xs font-bold hover:bg-blue-600">پذیرش</button>
                  )}
                  {r.status === "under_review" && (
                    <div className="flex gap-1 items-center">
                      <input type="number" placeholder="قیمت تکنسین" value={priceInput[r.id] || ""} onChange={(e) => setPriceInput((prev) => ({ ...prev, [r.id]: e.target.value }))} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs w-32" />
                      <button onClick={() => handleSetPrice(r.id)} className="rounded-2xl bg-green-600/80 px-3 py-1.5 text-xs font-bold hover:bg-green-600">ثبت قیمت</button>
                    </div>
                  )}
                  {r.status === "price_set" && (
                    <>
                      <button onClick={() => handleCustomerDecision(r.id, true)} className="rounded-2xl bg-green-600/80 px-3 py-1.5 text-xs font-bold hover:bg-green-600">تأیید مشتری</button>
                      <button onClick={() => handleCustomerDecision(r.id, false)} className="rounded-2xl bg-red-600/80 px-3 py-1.5 text-xs font-bold hover:bg-red-600">رد مشتری</button>
                    </>
                  )}
                  {r.status === "in_repair" && (
                    <button onClick={() => handleComplete(r.id)} className="rounded-2xl bg-green-600/80 px-3 py-1.5 text-xs font-bold hover:bg-green-600">تکمیل تعمیر</button>
                  )}
                  <select
                    onChange={(e) => { if (e.target.value) handleStatusChange(r.id, e.target.value as RepairStatus); e.target.value = ""; }}
                    className="rounded-2xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs"
                  >
                    <option value="">تغییر وضعیت...</option>
                    {repairStatusOptions.filter((s) => s.value !== r.status).map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
            {repairs.length === 0 && <p className="py-4 text-center text-white/40">تعمیری یافت نشد.</p>}
          </div>
        </div>
      )}

      {activeTab === "settings" && settings && (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 space-y-4">
          <h3 className="text-lg font-black">تنظیمات تعمیرات</h3>
          <div className="flex items-end gap-3">
            <div>
              <label className="mb-1 block text-sm text-white/60">درصد سود (%)</label>
              <input type="number" value={markupInput} onChange={(e) => setMarkupInput(e.target.value)} className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm w-32" />
            </div>
            <button onClick={handleSaveSettings} className="rounded-2xl bg-[#3c02cf] px-4 py-2 text-sm font-bold hover:bg-[#3c02cf]/80">ذخیره</button>
          </div>
          <p className="text-sm text-white/60">آخرین به‌روزرسانی: {new Date(settings.updated_at).toLocaleDateString("fa-IR")}</p>
        </div>
      )}
    </div>
  );
}
