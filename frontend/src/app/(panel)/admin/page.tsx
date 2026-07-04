import Link from "next/link";

import { PanelShell } from "@/components/layout/panel-shell";

export default function AdminPage() {
  return (
    <PanelShell title="پنل مدیر" description="دسترسی سریع به مدیریت Core، شعبه‌ها، نقش‌ها، انبار، اکانت‌ها و لاگ‌های ممیزی.">
      <div className="grid gap-4 md:grid-cols-3">
        <Link className="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:bg-white/10" href="/admin/branches">
          <p className="text-lg font-black">شعبه‌ها</p>
          <p className="mt-2 text-sm text-white/60">لیست، ایجاد، ویرایش و حذف شعبه‌ها.</p>
        </Link>
        <Link className="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:bg-white/10" href="/admin/roles">
          <p className="text-lg font-black">نقش‌ها</p>
          <p className="mt-2 text-sm text-white/60">مدیریت ماتریس دسترسی نقش‌ها.</p>
        </Link>
        <Link className="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:bg-white/10" href="/admin/accounts">
          <p className="text-lg font-black">اکانت‌ها</p>
          <p className="mt-2 text-sm text-white/60">مدیریت اکانت‌های PS/Xbox/Nintendo، بازی‌ها و لاگ فروش.</p>
        </Link>
        <Link className="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:bg-white/10" href="/admin/orders">
          <p className="text-lg font-black">سفارشات</p>
          <p className="mt-2 text-sm text-white/60">مدیریت سفارشات، پرداخت‌ها، فاکتورها و استردادها.</p>
        </Link>
        <Link className="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:bg-white/10" href="/admin/repair">
          <p className="text-lg font-black">تعمیرات</p>
          <p className="mt-2 text-sm text-white/60">مدیریت تعمیرات، تکنسین‌ها و قیمت‌گذاری.</p>
        </Link>
        <Link className="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:bg-white/10" href="/admin/procurement">
          <p className="text-lg font-black">تدارکات</p>
          <p className="mt-2 text-sm text-white/60">تأمین‌کنندگان، درخواست‌ها و سفارشات خرید.</p>
        </Link>
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
          <p className="text-lg font-black">Audit Log</p>
          <p className="mt-2 text-sm text-white/60">API ممیزی آماده مصرف در UI گزارش‌ها است.</p>
        </div>
      </div>
    </PanelShell>
  );
}
