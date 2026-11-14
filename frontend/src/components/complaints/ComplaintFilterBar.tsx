import { RotateCcw, Search } from 'lucide-react';
import { titleCase } from '../../utils/format';

export interface FilterValues { search: string; status: string; priority: string; severity: string; channel: string }

interface Props {
  values: FilterValues;
  onChange: (patch: Partial<FilterValues>) => void;
  onReset: () => void;
  statusOptions: string[];
  severityOptions: string[];
  channelOptions: string[];
}

function Select({ label, value, onChange, options, fmt = titleCase }: {
  label: string; value: string; onChange: (v: string) => void; options: string[]; fmt?: (s: string) => string;
}) {
  return (
    <select className="input w-full sm:w-auto sm:min-w-[140px]" value={value} onChange={(e) => onChange(e.target.value)} aria-label={label}>
      <option value="">{label}</option>
      {options.map((o) => <option key={o} value={o}>{fmt(o)}</option>)}
    </select>
  );
}

export function ComplaintFilterBar({ values, onChange, onReset, statusOptions, severityOptions, channelOptions }: Props) {
  const active = Object.values(values).some(Boolean);
  return (
    <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 p-4">
      <div className="relative min-w-[240px] flex-1">
        <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          className="input pl-9"
          placeholder="Search by ID, customer or description"
          value={values.search}
          onChange={(e) => onChange({ search: e.target.value })}
          aria-label="Search complaints"
        />
      </div>
      <Select label="All statuses" value={values.status} onChange={(v) => onChange({ status: v })} options={statusOptions} />
      <Select label="All priorities" value={values.priority} onChange={(v) => onChange({ priority: v })} options={['P1', 'P2', 'P3', 'P4']} fmt={(s) => s} />
      <Select label="All severities" value={values.severity} onChange={(v) => onChange({ severity: v })} options={severityOptions} />
      <Select label="All channels" value={values.channel} onChange={(v) => onChange({ channel: v })} options={channelOptions} />
      {active && <button className="btn-ghost" onClick={onReset}><RotateCcw size={14} /> Clear</button>}
    </div>
  );
}
