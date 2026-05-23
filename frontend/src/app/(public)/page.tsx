import { PublicLayout } from "@/components/layout/public-layout";

export default function HomePage() {
  return (
    <PublicLayout>
      <section className="mx-auto flex min-h-[70vh] max-w-6xl flex-col justify-center px-6 py-20">
        <p className="mb-4 text-sm font-semibold text-brand">فاز ۱.۱</p>
        <h1 className="max-w-3xl text-4xl font-black leading-tight md:text-6xl">
          زیرساخت ERP دکترگیم آماده توسعه ماژول‌های Core است.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-300">
          این اسکلت شامل مسیرهای عمومی، احراز هویت، پنل‌ها، کلاینت API و WebSocket است.
        </p>
      </section>
    </PublicLayout>
  );
}
