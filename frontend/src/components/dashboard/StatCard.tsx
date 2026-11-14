import type { LucideIcon } from 'lucide-react';
import { Skeleton } from '../common/Skeleton';
import { formatNumber } from '../../utils/format';

interface Props {
  label: string;
  value?: number;
  icon: LucideIcon;
  color: string;
  loading?: boolean;
  error?: boolean;
  hint?: string;
}

export function StatCard({ label, value, icon: Icon, color, loading, error, hint }: Props) {
  return (
    <div className="card flex items-center gap-4 p-4">
      <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl" style={{ backgroundColor: `${color}1a`, color }}>
        <Icon size={20} />
      </div>
      <div className="min-w-0">
        <p className="truncate text-sm text-slate-500">{label}</p>
        {loading ? (
          <Skeleton className="mt-1.5 h-7 w-16" />
        ) : (
          <p className="text-2xl font-bold tracking-tight text-slate-900" title={error ? 'Failed to load' : undefined}>
            {error ? '—' : formatNumber(value)}
          </p>
        )}
        {hint && !loading && <p className="text-xs text-slate-400">{hint}</p>}
      </div>
    </div>
  );
}
