export function KeyValue({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 py-2">
      <dt className="shrink-0 text-sm text-slate-500">{label}</dt>
      <dd className="min-w-0 break-words text-right text-sm font-medium text-slate-800">{children ?? '—'}</dd>
    </div>
  );
}

export function Section({ title, icon, children, aside }: { title: string; icon?: React.ReactNode; children: React.ReactNode; aside?: React.ReactNode }) {
  return (
    <section className="card">
      <header className="flex items-center justify-between gap-2 border-b border-slate-100 px-5 py-3.5">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          {icon && <span className="text-slate-400">{icon}</span>}
          {title}
        </h2>
        {aside}
      </header>
      <div className="px-5 py-4">{children}</div>
    </section>
  );
}
