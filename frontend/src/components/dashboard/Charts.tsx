import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import type { DistributionItem } from '../../types';
import { SERIES_PALETTE } from '../../utils/colors';
import { titleCase } from '../../utils/format';

type ColorFn = (name: string, index: number) => string;
const defaultColor: ColorFn = (_n, i) => SERIES_PALETTE[i % SERIES_PALETTE.length];

const tooltipStyle = {
  borderRadius: 8, border: '1px solid #e2e8f0', boxShadow: '0 10px 30px -8px rgba(15,23,42,.25)', fontSize: 12,
};

export function DonutChart({ data, colorFor = defaultColor, height = 260 }: { data: DistributionItem[]; colorFor?: ColorFn; height?: number }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  return (
    <div className="relative" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="82%" paddingAngle={2} stroke="none">
            {data.map((d, i) => <Cell key={d.name} fill={colorFor(d.name, i)} />)}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n: any) => [v, titleCase(n)]} />
          <Legend iconType="circle" iconSize={8} formatter={(v: string) => <span className="text-xs text-slate-600">{titleCase(v)}</span>} />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-x-0 top-[38%] text-center">
        <p className="text-2xl font-bold text-slate-900">{total.toLocaleString('en-IN')}</p>
        <p className="text-xs text-slate-500">Total</p>
      </div>
    </div>
  );
}

export function ColumnChart({ data, colorFor = defaultColor, height = 260 }: { data: DistributionItem[]; colorFor?: ColorFn; height?: number }) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
          <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(v: string) => titleCase(v)} />
          <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
          <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={tooltipStyle} formatter={(v: any) => [v, 'Complaints']} labelFormatter={(l: any) => titleCase(l)} />
          <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={56}>
            {data.map((d, i) => <Cell key={d.name} fill={colorFor(d.name, i)} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function HorizontalBars({ data, colorFor = defaultColor, height }: { data: DistributionItem[]; colorFor?: ColorFn; height?: number }) {
  const h = height ?? Math.max(220, data.length * 38 + 24);
  return (
    <div style={{ height: h }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
          <XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
          <YAxis type="category" dataKey="name" width={130} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#475569' }} tickFormatter={(v: string) => (v.length > 18 ? v.slice(0, 17) + '…' : v)} />
          <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={tooltipStyle} formatter={(v: any) => [v, 'Complaints']} />
          <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={20}>
            {data.map((d, i) => <Cell key={d.name} fill={colorFor(d.name, i)} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function GroupedAgentBars({ data, height }: { data: { name: string; total?: number; current?: number }[]; height?: number }) {
  const h = height ?? Math.max(260, data.length * 44 + 60);
  return (
    <div style={{ height: h }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
          <XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
          <YAxis type="category" dataKey="name" width={130} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#475569' }} />
          <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={tooltipStyle} />
          <Legend iconType="circle" iconSize={8} />
          {data.some((d) => d.total !== undefined) && <Bar dataKey="total" name="Total assignments" fill="#3b6df0" radius={[0, 4, 4, 0]} barSize={12} />}
          {data.some((d) => d.current !== undefined) && <Bar dataKey="current" name="Current assignments" fill="#0d9488" radius={[0, 4, 4, 0]} barSize={12} />}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
