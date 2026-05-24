"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { requestOtp, verifyOtp } from "@/lib/auth/api";
import { useAuthStore } from "@/store/auth-store";

export function LoginForm() {
  const router = useRouter();
  const setTokens = useAuthStore((state) => state.setTokens);
  const setUser = useAuthStore((state) => state.setUser);
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    setIsLoading(true);

    try {
      if (step === "phone") {
        const data = await requestOtp(phone);
        setMessage(data.detail);
        setStep("code");
      } else {
        const data = await verifyOtp(phone, code);
        setTokens({ accessToken: data.access, refreshToken: data.refresh });
        setUser(data.user);
        router.replace("/profile");
      }
    } catch {
      setError(step === "phone" ? "ارسال کد ناموفق بود. شماره را بررسی کنید." : "کد واردشده معتبر نیست یا منقضی شده است.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <label className="block">
        <span className="mb-2 block text-sm font-bold text-slate-700 dark:text-slate-200">شماره موبایل</span>
        <input
          className="w-full rounded-2xl border border-brand/15 bg-white px-4 py-3 text-left [direction:ltr] outline-none transition focus:border-brand dark:bg-white/10"
          disabled={step === "code" || isLoading}
          inputMode="tel"
          onChange={(event) => setPhone(event.target.value)}
          placeholder="09123456789"
          required
          value={phone}
        />
      </label>

      {step === "code" ? (
        <label className="block">
          <span className="mb-2 block text-sm font-bold text-slate-700 dark:text-slate-200">کد OTP</span>
          <input
            className="w-full rounded-2xl border border-brand/15 bg-white px-4 py-3 text-center tracking-[0.5em] outline-none transition focus:border-brand dark:bg-white/10"
            inputMode="numeric"
            maxLength={6}
            onChange={(event) => setCode(event.target.value)}
            placeholder="------"
            required
            value={code}
          />
        </label>
      ) : null}

      {message ? <p className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</p> : null}
      {error ? <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}

      <button
        className="w-full rounded-2xl bg-brand px-4 py-3 font-black text-white shadow-xl shadow-brand/20 transition hover:bg-brand/90 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={isLoading}
        type="submit"
      >
        {isLoading ? "لطفاً صبر کنید..." : step === "phone" ? "دریافت کد ورود" : "ورود به پنل"}
      </button>

      {step === "code" ? (
        <button className="w-full text-sm font-bold text-brand" onClick={() => setStep("phone")} type="button">
          ویرایش شماره موبایل
        </button>
      ) : null}
    </form>
  );
}
