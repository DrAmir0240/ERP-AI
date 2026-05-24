"use client";

import { FormEvent, useEffect, useState } from "react";

import { updateCurrentUser } from "@/lib/auth/api";
import { useAuthStore } from "@/store/auth-store";

export function ProfileForm() {
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setFullName(user?.full_name ?? "");
  }, [user?.full_name]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("");
    setIsLoading(true);
    try {
      const data = await updateCurrentUser({ full_name: fullName });
      setUser(data);
      setStatus("پروفایل ذخیره شد.");
    } catch {
      setStatus("ذخیره پروفایل ناموفق بود.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form className="rounded-3xl border border-white/10 bg-white/5 p-5" onSubmit={handleSubmit}>
      <p className="text-sm text-white/60">شماره موبایل</p>
      <p className="mt-1 text-lg font-black ltr:text-left">{user?.phone ?? "-"}</p>
      <label className="mt-5 block">
        <span className="mb-2 block text-sm font-semibold text-white/70">نام کامل</span>
        <input
          className="w-full rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 text-white outline-none transition focus:border-white/40"
          onChange={(event) => setFullName(event.target.value)}
          placeholder="نام و نام خانوادگی"
          value={fullName}
        />
      </label>
      {status ? <p className="mt-4 text-sm text-white/70">{status}</p> : null}
      <button className="mt-5 rounded-2xl bg-white px-5 py-3 font-black text-brand transition hover:bg-white/90 disabled:opacity-60" disabled={isLoading} type="submit">
        ذخیره پروفایل
      </button>
    </form>
  );
}
