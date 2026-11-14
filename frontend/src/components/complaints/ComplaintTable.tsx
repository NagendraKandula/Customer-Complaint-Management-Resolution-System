import { useNavigate } from 'react-router-dom';
import { Repeat, ShieldAlert } from 'lucide-react';
import type { Complaint } from '../../types';
import { PriorityBadge, SeverityBadge, StatusBadge } from '../common/Badges';
import { customerNameOf } from '../../services/complaintService';
import { formatDate, titleCase, truncate } from '../../utils/format';

export function ComplaintTable({ items }: { items: Complaint[] }) {
  const navigate = useNavigate();
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[960px] text-left text-sm">
        <thead className="bg-slate-50 text-xs font-semibold text-slate-500">
          <tr>
            {['ID', 'Customer', 'Description', 'Priority', 'Severity', 'Status', 'Channel', 'Created'].map((h) => (
              <th key={h} className="px-4 py-3 font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((c) => {
            const open = () => navigate(`/complaints/${encodeURIComponent(String(c.complaint_id))}`);
            return (
              <tr
                key={String(c.complaint_id)}
                tabIndex={0}
                onClick={open}
                onKeyDown={(e) => { if (e.key === 'Enter') open(); }}
                className="cursor-pointer transition-colors hover:bg-brand-50/50 focus-visible:bg-brand-50/60"
              >
                <td className="px-4 py-3 font-mono text-xs font-medium text-brand-700">#{String(c.complaint_id)}</td>
                <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-800">{customerNameOf(c)}</td>
                <td className="max-w-md px-4 py-3 text-slate-600">
                  <span className="flex items-center gap-2">
                    <span>{truncate(c.complaint_text, 90)}</span>
                    {c.is_safety_related && <ShieldAlert size={14} className="shrink-0 text-red-500" aria-label="Safety related" />}
                    {c.is_repeat && <Repeat size={14} className="shrink-0 text-purple-500" aria-label="Repeat complaint" />}
                  </span>
                </td>
                <td className="px-4 py-3"><PriorityBadge value={c.priority} /></td>
                <td className="px-4 py-3"><SeverityBadge value={c.severity} /></td>
                <td className="px-4 py-3"><StatusBadge value={c.status} /></td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">{titleCase(c.channel)}</td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-500">{formatDate(c.created_at)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
