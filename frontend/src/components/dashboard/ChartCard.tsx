import { EmptyState, ErrorState } from '../common/States';
import { Skeleton } from '../common/Skeleton';

interface Props {
  title: string;
  subtitle?: string;
  loading?: boolean;
  error?: string;
  empty?: boolean;
  emptyHint?: string;
  onRetry?: () => void;
  className?: string;
  children: React.ReactNode;
}

export function ChartCard({ title, subtitle, loading, error, empty, emptyHint, onRetry, className = '', children }: Props) {
  return (
    <section className={`card flex flex-col ${className}`}>
      <header className="border-b border-slate-100 px-5 py-3.5">
        <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </header>
      <div className="flex-1 p-4">
        {loading ? (
          <div className="space-y-3"><Skeleton className="h-4 w-1/3" /><Skeleton className="h-48 w-full" /></div>
        ) : error ? (
          <ErrorState message={error} onRetry={onRetry} />
        ) : empty ? (
          <EmptyState title="No data yet" hint={emptyHint ?? 'There is nothing to chart for this view.'} />
        ) : (
          children
        )}
      </div>
    </section>
  );
}
