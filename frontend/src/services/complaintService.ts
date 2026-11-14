import { getJson } from './api';
import { firstArray, isObj, pick, toNum, unwrap } from './normalize';
import type { Complaint, ComplaintDetailsModel, ComplaintFilters, Dict, Paged } from '../types';

export function customerNameOf(c: Dict | null | undefined): string {
  if (!c) return '—';
  const nested = isObj(c.customer) ? c.customer : null;
  return String(
    pick(c, 'customer_name', 'full_name') ?? pick(nested, 'full_name', 'name') ??
      (typeof c.customer === 'string' ? c.customer : undefined) ??
      (c.customer_id !== undefined ? `Customer #${c.customer_id}` : '—'),
  );
}

const eq = (a: unknown, b?: string) => !b || String(a ?? '').toLowerCase() === b.toLowerCase();

function applyClientFilters(items: Complaint[], f: ComplaintFilters): Complaint[] {
  const q = f.search?.trim().toLowerCase();
  return items.filter((c) => {
    if (!eq(c.status, f.status) || !eq(c.priority, f.priority)) return false;
    if (!eq(c.severity, f.severity) || !eq(c.channel, f.channel)) return false;
    if (q) {
      const hay = `${c.complaint_id} ${c.complaint_text ?? ''} ${customerNameOf(c)}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

/**
 * Query params are sent under the common names (page/page_size/limit/offset/skip/search).
 * FastAPI ignores unknown query params, so extras are harmless. If the server returns more
 * rows than requested (i.e. it ignored pagination), filtering and paging happen in the browser.
 */
export async function getComplaints(f: ComplaintFilters): Promise<Paged<Complaint>> {
  const params: Record<string, unknown> = {
    page: f.page,
    page_size: f.pageSize,
    limit: f.pageSize,
    offset: (f.page - 1) * f.pageSize,
    skip: (f.page - 1) * f.pageSize,
    search: f.search || undefined,
    status: f.status || undefined,
    priority: f.priority || undefined,
    severity: f.severity || undefined,
    channel: f.channel || undefined,
  };
  const raw = await getJson('/api/complaints', params);
  const root = unwrap(raw);
  const items = firstArray(root, ['items', 'complaints', 'data', 'results', 'rows']) as Complaint[];
  const serverTotal = isObj(root)
    ? toNum(pick(root, 'total', 'total_count', 'count', 'total_items', 'total_records'))
    : undefined;

  const clientMode = items.length > f.pageSize || serverTotal === undefined;
  if (!clientMode) {
    return { items, total: serverTotal ?? items.length, page: f.page, pageSize: f.pageSize };
  }
  const filtered = applyClientFilters(items, f);
  const start = (f.page - 1) * f.pageSize;
  return {
    items: filtered.slice(start, start + f.pageSize),
    total: filtered.length,
    page: f.page,
    pageSize: f.pageSize,
  };
}

export async function getComplaintDetails(id: string | number): Promise<ComplaintDetailsModel> {
  const raw = await getJson(`/api/complaints/${id}`);
  const root = unwrap(raw);
  const complaint: Complaint = isObj(root?.complaint) ? root.complaint : (root as Complaint);

  const customer: Dict | null = isObj(root?.customer)
    ? root.customer
    : isObj(complaint?.customer)
      ? complaint.customer
      : complaint && (complaint.full_name || complaint.email || complaint.customer_tier)
        ? complaint
        : null;

  const slaClocks = firstArray(root, ['sla_clocks', 'sla_clock', 'sla']);
  const nestedEvents = slaClocks.flatMap((s) => (Array.isArray(s.events) ? s.events : []));
  const slaEvents = firstArray(root, ['sla_events']);

  return {
    complaint,
    customer,
    messages: firstArray(root, ['messages', 'complaint_messages', 'conversation']),
    history: firstArray(root, ['status_history', 'complaint_status_history', 'history', 'timeline']),
    assignments: firstArray(root, ['assignments', 'complaint_assignments', 'assignment']),
    resolutions: firstArray(root, ['resolutions', 'resolution']),
    slaClocks,
    slaEvents: slaEvents.length ? slaEvents : nestedEvents,
    surveys: firstArray(root, ['surveys', 'survey']),
    raw,
  };
}
