import { priorityColor, severityColor, statusColor } from '../../utils/colors';
import { titleCase } from '../../utils/format';

function Pill({ color, children, dot = true }: { color: string; children: React.ReactNode; dot?: boolean }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-semibold"
      style={{ backgroundColor: `${color}1a`, color }}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />}
      {children}
    </span>
  );
}

export function PriorityBadge({ value }: { value?: string | null }) {
  if (!value) return <span className="text-slate-400">—</span>;
  return <Pill color={priorityColor(value)}>{String(value).toUpperCase()}</Pill>;
}

export function StatusBadge({ value }: { value?: string | null }) {
  if (!value) return <span className="text-slate-400">—</span>;
  return <Pill color={statusColor(value)}>{titleCase(value)}</Pill>;
}

export function SeverityBadge({ value }: { value?: string | number | null }) {
  if (value === undefined || value === null || value === '') return <span className="text-slate-400">—</span>;
  return <Pill color={severityColor(value)} dot={false}>{titleCase(value)}</Pill>;
}

export function FlagBadge({ color, children }: { color: string; children: React.ReactNode }) {
  return <Pill color={color} dot={false}>{children}</Pill>;
}
