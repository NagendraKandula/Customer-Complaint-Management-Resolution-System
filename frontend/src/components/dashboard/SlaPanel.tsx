import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { SlaStats } from '../../types';
import { formatNumber } from '../../utils/format';

const ROWS: { key: keyof SlaStats; label: string; color: string }[] = [
  { key: 'total', label: 'Total SLA records', color: '#3b6df0' },
  { key: 'responseBreaches', label: 'Response breaches', color: '#dc2626' },
  { key: 'resolutionBreaches', label: 'Resolution breaches', color: '#f97316' },
  { key: 'compliant', label: 'Compliant', color: '#16a34a' },
  { key: 'paused', label: 'Paused', color: '#64748b' },
];

export function SlaPanel({ sla, showChart = false }: { sla: SlaStats; showChart?: boolean }) {
  const chart = ROWS.filter((r) => r.key !== 'total' && sla[r.key] !== undefined).map((r) => ({
    name: r.label, value: sla[r.key] as number, color: r.color,
  }));
  return (
    <div>
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">
        {ROWS.map((r) => (
          <div key={r.key} className="rounded-lg border border-slate-100 bg-slate-50/60 p-3">
            <dt className="flex items-center gap-2 text-xs text-slate-500">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: r.color }} />
              {r.label}
            </dt>
            <dd className="mt-1 text-xl font-bold text-slate-900">{formatNumber(sla[r.key])}</dd>
          </div>
        ))}
      </dl>
      {showChart && chart.length > 0 && (
        <div className="mt-5 h-60">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
              <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
              <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={64}>
                {chart.map((c) => <Cell key={c.name} fill={c.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
