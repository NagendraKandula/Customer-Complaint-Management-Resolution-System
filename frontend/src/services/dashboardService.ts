import { getJson } from './api';
import { isObj, pickLike, toDistribution, toNum, unwrap } from './normalize';
import type { DistributionItem, SlaStats, SummaryStats } from '../types';

export async function getSummary(): Promise<SummaryStats> {
  const raw = unwrap(await getJson('/api/dashboard/summary'));
  let src: any = raw;
  // Fall back to a name/count list if the endpoint returns one
  if (!isObj(raw)) {
    const dist = toDistribution(raw);
    src = Object.fromEntries(dist.map((d) => [d.name.toLowerCase(), d.value]));
  }
  return {
    total: toNum(pickLike(src, /^total/i)),
    open: toNum(pickLike(src, /^open/i)),
    resolved: toNum(pickLike(src, /^resolved/i)),
    closed: toNum(pickLike(src, /^closed/i)),
    reopened: toNum(pickLike(src, /reopen/i)),
  };
}

export async function getStatusDistribution(): Promise<DistributionItem[]> {
  return toDistribution(await getJson('/api/dashboard/status'));
}

export async function getPriorityDistribution(): Promise<DistributionItem[]> {
  const items = toDistribution(await getJson('/api/dashboard/priority'));
  // Always show P1-P4 in order; a missing bucket means zero complaints in that group.
  const byKey = new Map(items.map((i) => [i.name.toUpperCase(), i]));
  const ordered = ['P1', 'P2', 'P3', 'P4'].map((p) => byKey.get(p) ?? { name: p, value: 0 });
  const extras = items.filter((i) => !/^P[1-4]$/i.test(i.name));
  return [...ordered, ...extras];
}

export async function getSeverityDistribution(): Promise<DistributionItem[]> {
  return toDistribution(await getJson('/api/dashboard/severity'));
}

export async function getSla(): Promise<SlaStats> {
  const raw = unwrap(await getJson('/api/dashboard/sla'));
  return {
    total: toNum(pickLike(raw, /^total/i)),
    responseBreaches: toNum(pickLike(raw, /response.*breach/i)),
    resolutionBreaches: toNum(pickLike(raw, /resolution.*breach/i)),
    compliant: toNum(pickLike(raw, /compliant|within_sla|met/i)),
    paused: toNum(pickLike(raw, /paus/i)),
  };
}
