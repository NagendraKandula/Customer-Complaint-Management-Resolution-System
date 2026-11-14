import type { Dict, DistributionItem } from '../types';

export const isObj = (v: unknown): v is Dict =>
  v !== null && typeof v === 'object' && !Array.isArray(v);

/** First present (non-null) value among the given keys. */
export function pick(obj: unknown, ...keys: string[]): any {
  if (!isObj(obj)) return undefined;
  for (const k of keys) if (obj[k] !== undefined && obj[k] !== null) return obj[k];
  return undefined;
}

/** First present value whose key matches the regex. */
export function pickLike(obj: unknown, re: RegExp): any {
  if (!isObj(obj)) return undefined;
  for (const k of Object.keys(obj)) {
    if (re.test(k) && obj[k] !== null && obj[k] !== undefined) return obj[k];
  }
  return undefined;
}

export function toNum(v: unknown): number | undefined {
  if (v === null || v === undefined || v === '') return undefined;
  const n = typeof v === 'number' ? v : parseFloat(String(v));
  return Number.isFinite(n) ? n : undefined;
}

const WRAPPER_KEYS = ['data', 'result', 'results', 'payload'];

/** Strip a {data: ...} style envelope when it is the only meaningful key. */
export function unwrap(raw: any): any {
  if (isObj(raw)) {
    for (const k of WRAPPER_KEYS) {
      if (k in raw && (isObj(raw[k]) || Array.isArray(raw[k]))) {
        const others = Object.keys(raw).filter(
          (x) => x !== k && !['status', 'success', 'message', 'detail'].includes(x),
        );
        if (others.length === 0) return unwrap(raw[k]);
      }
    }
  }
  return raw;
}

/** Find an array under one of the keys (or the root itself). A single object is wrapped. */
export function firstArray(raw: any, keys: string[]): Dict[] {
  const root = unwrap(raw);
  if (Array.isArray(root)) return root as Dict[];
  if (!isObj(root)) return [];
  for (const k of keys) if (Array.isArray(root[k])) return root[k] as Dict[];
  for (const k of keys) if (isObj(root[k])) return [root[k]];
  return [];
}

const LABEL_KEYS = [
  'status', 'priority', 'severity', 'category', 'category_name', 'channel', 'agent_name',
  'team_name', 'name', 'label', 'key', 'sentiment',
];
const VALUE_KEYS = [
  'count', 'total', 'total_count', 'complaint_count', 'complaints', 'total_complaints', 'value', 'n',
];
const LIST_KEYS = [
  'items', 'data', 'rows', 'results', 'distribution', 'breakdown', 'categories',
  'statuses', 'priorities', 'severities',
];

/**
 * Convert common shapes into [{name, value}]:
 *   { open: 4, closed: 9 }  |  [{ status: 'open', count: 4 }]  |  { data: [...] }
 */
export function toDistribution(raw: any): DistributionItem[] {
  const root = unwrap(raw);

  if (Array.isArray(root)) {
    const out: DistributionItem[] = [];
    for (const item of root) {
      if (!isObj(item)) continue;
      let label: any = pick(item, ...LABEL_KEYS);
      let value: any = pick(item, ...VALUE_KEYS);
      if (label === undefined) {
        const s = Object.entries(item).find(([, v]) => typeof v === 'string');
        if (s) label = s[1];
        else if (item.category_id !== undefined) label = `Category ${item.category_id}`;
      }
      if (value === undefined) {
        const n = Object.entries(item).find(([k, v]) => typeof v === 'number' && !/id$/i.test(k));
        if (n) value = n[1];
      }
      const num = toNum(value);
      if (label !== undefined && num !== undefined) out.push({ name: String(label), value: num });
    }
    return out;
  }

  if (isObj(root)) {
    for (const k of LIST_KEYS) {
      if (Array.isArray(root[k]) || isObj(root[k])) {
        const nested = toDistribution(root[k]);
        if (nested.length) return nested;
      }
    }
    return Object.entries(root)
      .map(([k, v]) => ({ name: k, value: toNum(v) }))
      .filter((e): e is DistributionItem => e.value !== undefined);
  }
  return [];
}
