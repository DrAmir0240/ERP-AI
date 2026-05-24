import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <div className="rounded-3xl border border-brand/15 bg-white/85 p-8 shadow-2xl shadow-brand/10 backdrop-blur dark:bg-brand-dark/70">
        <h1 className="text-2xl font-black">ورود با شماره موبایل</h1>
        <p className="mb-6 mt-3 text-sm text-slate-600 dark:text-slate-300">شماره موبایل را وارد کنید تا کد یک‌بارمصرف برای ورود ارسال شود.</p>
        <LoginForm />
      </div>
    </main>
  );
}
