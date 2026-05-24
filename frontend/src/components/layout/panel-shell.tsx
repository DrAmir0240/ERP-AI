import Link from "next/link";

import { LogoutButton } from "@/components/auth/logout-button";
import { RoleSwitcher } from "@/components/auth/role-switcher";

export function PanelShell({ title, description, children }: { title: string; description: string; children?: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-brand-dark px-6 py-10 text-white">
      <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-white/10 p-8 shadow-2xl shadow-black/20">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <p className="text-sm font-semibold text-white/60">DrGame ERP</p>
          <nav className="flex flex-wrap items-center gap-3 text-sm font-bold">
            <Link className="text-white/75 transition hover:text-white" href="/admin">مدیر</Link>
            <Link className="text-white/75 transition hover:text-white" href="/employee">کارمند</Link>
            <Link className="text-white/75 transition hover:text-white" href="/customer">مشتری</Link>
            <Link className="text-white/75 transition hover:text-white" href="/profile">پروفایل</Link>
            <LogoutButton />
          </nav>
        </div>
        <h1 className="mt-3 text-3xl font-black">{title}</h1>
        <p className="mt-4 max-w-2xl text-white/70">{description}</p>
        <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
          <div>{children}</div>
          <aside>
            <RoleSwitcher />
          </aside>
        </div>
      </div>
    </main>
  );
}
