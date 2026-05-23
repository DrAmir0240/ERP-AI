import Link from "next/link";

export function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href="/" className="text-xl font-black text-brand">دکترگیم</Link>
        <nav className="flex gap-4 text-sm font-medium">
          <Link href="/login">ورود</Link>
          <Link href="/admin">پنل مدیر</Link>
        </nav>
      </header>
      {children}
    </div>
  );
}
