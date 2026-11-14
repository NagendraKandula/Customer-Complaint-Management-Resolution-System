import { getJson } from './api';
import { firstArray, isObj, pick, pickLike, toDistribution, toNum, unwrap } from './normalize';
import type { AgentRow, AgentStats, DistributionItem } from '../types';

export async function getCategories(): Promise<DistributionItem[]> {
  return toDistribution(await getJson('/api/analytics/categories'));
}

export async function getAgents(): Promise<AgentStats> {
  const raw = unwrap(await getJson('/api/analytics/agents'));
  const list = firstArray(raw, ['agents', 'workload', 'agent_workload', 'items', 'rows', 'data']);

  const agents: AgentRow[] = list.map((a) => ({
    name: String(pick(a, 'agent_name', 'name', 'agent') ?? `Agent ${pick(a, 'agent_id') ?? '?'}`),
    total: toNum(pickLike(a, /^(total|assignments?)(_assignments?)?$|total_assign/i)),
    current: toNum(pickLike(a, /current|active|open/i)),
  }));

  const rootTotals = isObj(raw)
    ? {
        total: toNum(pickLike(raw, /total.*assign/i)),
        current: toNum(pickLike(raw, /current.*assign|active.*assign/i)),
      }
    : { total: undefined, current: undefined };

  const sum = (k: 'total' | 'current') => {
    const vals = agents.map((a) => a[k]).filter((v): v is number => v !== undefined);
    return vals.length ? vals.reduce((x, y) => x + y, 0) : undefined;
  };

  return {
    totalAssignments: rootTotals.total ?? sum('total'),
    currentAssignments: rootTotals.current ?? sum('current'),
    agents,
  };
}
