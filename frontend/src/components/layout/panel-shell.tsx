export function PanelShell({ title, description }: { title: string; description: string }) {
  return (
    <main className="min-h-screen bg-brand-dark px-6 py-10 text-white">
      <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-white/10 p-8 shadow-2xl shadow-black/20">
        <p className="text-sm font-semibold text-white/60">DrGame ERP</p>
        <h1 className="mt-3 text-3xl font-black">{title}</h1>
        <p className="mt-4 max-w-2xl text-white/70">{description}</p>
      </div>
    </main>
  );
}
