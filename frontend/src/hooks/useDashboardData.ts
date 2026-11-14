import { useCallback, useEffect, useState } from 'react';
import { errorMessage } from '../services/api';
import * as dash from '../services/dashboardService';
import * as analytics from '../services/analyticsService';
import type { AgentStats, DistributionItem, SlaStats, SummaryStats } from '../types';

export interface Slot<T> { data?: T; error?: string }

export interface DashboardBundle {
  summary: Slot<SummaryStats>;
  status: Slot<DistributionItem[]>;
  priority: Slot<DistributionItem[]>;
  severity: Slot<DistributionItem[]>;
  sla: Slot<SlaStats>;
  categories: Slot<DistributionItem[]>;
  agents: Slot<AgentStats>;
}

async function slot<T>(p: Promise<T>): Promise<Slot<T>> {
  try { return { data: await p }; } catch (e) { return { error: errorMessage(e) }; }
}

/** Loads all dashboard + analytics endpoints in parallel; one failure doesn't block the others. */
export function useDashboardData() {
  const [bundle, setBundle] = useState<DashboardBundle | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const [summary, status, priority, severity, sla, categories, agents] = await Promise.all([
      slot(dash.getSummary()),
      slot(dash.getStatusDistribution()),
      slot(dash.getPriorityDistribution()),
      slot(dash.getSeverityDistribution()),
      slot(dash.getSla()),
      slot(analytics.getCategories()),
      slot(analytics.getAgents()),
    ]);
    setBundle({ summary, status, priority, severity, sla, categories, agents });
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);
  return { bundle, loading, reload: load };
}
