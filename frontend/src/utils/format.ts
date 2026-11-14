export function formatDate(v?: string | null, withTime = false): string {
  if (!v) return '—';
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return String(v);
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    ...(withTime ? { hour: '2-digit', minute: '2-digit' } : {}),
  }).format(d);
}

export function timeAgo(v?: string | null): string {
  if (!v) return '';
  const d = new Date(v).getTime();
  if (Number.isNaN(d)) return '';
  const mins = Math.round((Date.now() - d) / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.round(hrs / 24);
  return days < 31 ? `${days}d ago` : formatDate(v);
}

export function titleCase(s?: string | number | null): string {
  if (s === undefined || s === null || s === '') return '—';
  return String(s).replace(/[_-]+/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export function truncate(s: string | undefined | null, n = 90): string {
  if (!s) return '—';
  return s.length > n ? s.slice(0, n).trimEnd() + '…' : s;
}

export function formatNumber(n?: number | null): string {
  return n === undefined || n === null ? '—' : new Intl.NumberFormat('en-IN').format(n);
}

export function formatMinutes(m?: number | null): string {
  if (m === undefined || m === null) return '—';
  if (m < 60) return `${Math.round(m)} min`;
  return `${Math.floor(m / 60)}h ${Math.round(m % 60)}m`;
}

export function formatMoney(v?: number | string | null): string {
  if (v === undefined || v === null || v === '') return '—';
  const n = Number(v);
  return Number.isFinite(n)
    ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(n)
    : String(v);
}
