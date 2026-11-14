import { ArrowRight } from 'lucide-react';
import type { Dict } from '../../types';
import { StatusBadge } from '../common/Badges';
import { statusColor } from '../../utils/colors';
import { formatDate } from '../../utils/format';

export function StatusTimeline({ history }: { history: Dict[] }) {
  const sorted = [...history].sort((a, b) => new Date(a.changed_at ?? 0).getTime() - new Date(b.changed_at ?? 0).getTime());
  return (
    <ol className="relative ml-2 border-l border-slate-200">
      {sorted.map((h, i) => (
        <li key={h.history_id ?? i} className="relative pb-6 pl-6 last:pb-0">
          <span
            className="absolute -left-[7px] top-1 h-3 w-3 rounded-full border-2 border-white"
            style={{ backgroundColor: statusColor(h.new_status), boxShadow: '0 0 0 1px #e2e8f0' }}
          />
          <div className="flex flex-wrap items-center gap-2">
            {h.old_status ? <StatusBadge value={h.old_status} /> : <span className="text-xs text-slate-400">Created</span>}
            <ArrowRight size={14} className="text-slate-400" />
            <StatusBadge value={h.new_status} />
          </div>
          <p className="mt-1.5 text-xs text-slate-500">
            {formatDate(h.changed_at, true)}
            {h.changed_by !== undefined && h.changed_by !== null && <> · by {String(h.changed_by)}</>}
          </p>
          {h.reason && <p className="mt-1 text-sm text-slate-600">{h.reason}</p>}
        </li>
      ))}
    </ol>
  );
}
