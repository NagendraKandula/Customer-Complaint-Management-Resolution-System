export const PRIORITY_COLORS: Record<string, string> = {
  P1: '#dc2626',
  P2: '#f97316',
  P3: '#eab308',
  P4: '#16a34a',
};

export function priorityColor(p?: string | null): string {
  if (!p) return '#94a3b8';
  const key = String(p).toUpperCase().match(/P[1-4]/)?.[0];
  return key ? PRIORITY_COLORS[key] : '#94a3b8';
}

export function statusColor(s?: string | null): string {
  const v = String(s ?? '').toLowerCase();
  if (v.includes('reopen')) return '#db2777';
  if (v.includes('escalat')) return '#7c3aed';
  if (v.includes('resolved')) return '#16a34a';
  if (v.includes('closed')) return '#6b7280';
  if (v.includes('progress') || v.includes('assigned')) return '#4f46e5';
  if (v.includes('pending') || v.includes('wait') || v.includes('hold')) return '#0891b2';
  if (v.includes('open') || v.includes('new')) return '#2563eb';
  return '#64748b';
}

export function severityColor(s?: string | number | null): string {
  const v = String(s ?? '').toLowerCase();
  if (v.includes('critical') || v === '5') return '#b91c1c';
  if (v.includes('high') || v === '4') return '#ea580c';
  if (v.includes('medium') || v.includes('moderate') || v === '3') return '#ca8a04';
  if (v.includes('low') || v === '2') return '#15803d';
  if (v.includes('minor') || v === '1') return '#0d9488';
  return '#64748b';
}

export const SERIES_PALETTE = [
  '#3b6df0', '#0d9488', '#7c3aed', '#f97316', '#db2777', '#0891b2', '#65a30d', '#b45309', '#475569',
];
