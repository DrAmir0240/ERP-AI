"use client";

import { FormEvent, useEffect, useState } from "react";

import type { Branch } from "@/lib/auth/types";
import { createBranch, deleteBranch, listBranches, updateBranch } from "@/lib/core/api";

const emptyBranch = { name: "", address: "", phone: "", is_active: true };

export function BranchManager() {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyBranch);
  const [status, setStatus] = useState("");

  async function loadBranches() {
    setBranches(await listBranches());
  }

  useEffect(() => {
    loadBranches().catch(() => setStatus("دریافت شعبه‌ها ناموفق بود."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      if (editingId) {
        await updateBranch(editingId, form);
        setStatus("شعبه ویرایش شد.");
      } else {
        await createBranch(form);
        setStatus("شعبه ایجاد شد.");
      }
      setEditingId(null);
      setForm(emptyBranch);
      await loadBranches();
    } catch {
      setStatus("ذخیره شعبه ناموفق بود.");
    }
  }

  function startEdit(branch: Branch) {
    setEditingId(branch.id);
    setForm({ name: branch.name, address: branch.address, phone: branch.phone, is_active: branch.is_active });
  }

  async function handleDelete(id: number) {
    try {
      await deleteBranch(id);
      setStatus("شعبه حذف شد.");
      await loadBranches();
    } catch {
      setStatus("حذف شعبه ناموفق بود.");
    }
  }

  return (
    <section className="space-y-5">
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-2" onSubmit={handleSubmit}>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="نام شعبه" required value={form.name} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => setForm({ ...form, phone: event.target.value })} placeholder="تلفن" value={form.phone} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none md:col-span-2" onChange={(event) => setForm({ ...form, address: event.target.value })} placeholder="آدرس" value={form.address} />
        <label className="flex items-center gap-2 text-sm text-white/70">
          <input checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} type="checkbox" />
          فعال
        </label>
        <button className="rounded-2xl bg-white px-5 py-3 font-black text-brand" type="submit">
          {editingId ? "ویرایش شعبه" : "ایجاد شعبه"}
        </button>
      </form>
      {status ? <p className="text-sm text-white/70">{status}</p> : null}
      <div className="space-y-3">
        {branches.map((branch) => (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 p-4" key={branch.id}>
            <div>
              <p className="font-black">{branch.name}</p>
              <p className="text-sm text-white/60">{branch.phone || "بدون تلفن"} — {branch.is_active ? "فعال" : "غیرفعال"}</p>
            </div>
            <div className="flex gap-2">
              <button className="rounded-xl border border-white/15 px-3 py-2 text-sm" onClick={() => startEdit(branch)} type="button">ویرایش</button>
              <button className="rounded-xl border border-red-300/40 px-3 py-2 text-sm text-red-100" onClick={() => handleDelete(branch.id)} type="button">حذف</button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
