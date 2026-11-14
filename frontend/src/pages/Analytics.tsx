import { RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { ChartCard } from '../components/dashboard/ChartCard';
import { DonutChart, GroupedAgentBars, HorizontalBars } from '../components/dashboard/Charts';
import { SlaPanel } from '../components/dashboard/SlaPanel';
import { useDashboardData } from '../hooks/useDashboardData';
import { priorityColor, severityColor } from '../utils/colors';
import { formatNumber } from '../utils/format';

export default function Analytics() {
  const { bundle: b, loading, reload } = useDashboardData();
  const cats = b?.categories.data ?? [];
  const catTotal = cats.reduce((s, c) => s + c.value, 0);
  const agents = b?.agents.data;

  return (
    <>
      <PageHeader
        title="Analytics"
        subtitle="Distribution and performance across categories, agents and SLAs."
        actions={<button className="btn-ghost" onClick={reload} disabled={loading}><RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh</button>}
      />

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-5">
        <ChartCard className="xl:col-span-3" title="Category-wise complaints" subtitle="Volume by complaint category" loading={loading} error={b?.categories.error} empty={!cats.length} onRetry={reload}>
          <HorizontalBars data={cats} />
        </ChartCard>
        <ChartCard className="xl:col-span-2" title="Category share" loading={loading} error={b?.categories.error} empty={!cats.length} onRetry={reload}>
          <ul className="divide-y divide-slate-100">
            {[...cats].sort((a, c) => c.value - a.value).map((c) => (
              <li key={c.name} className="flex items-center gap-3 py-2.5">
                <span className="min-w-0 flex-1 truncate text-sm text-slate-700">{c.name}</span>
                <div className="h-1.5 w-24 overflow-hidden rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-brand-500" style={{ width: `${catTotal ? (c.value / catTotal) * 100 : 0}%` }} />
                </div>
                <span className="w-10 text-right text-sm font-semibold text-slate-900">{formatNumber(c.value)}</span>
                <span className="w-12 text-right text-xs text-slate-500">{catTotal ? ((c.value / catTotal) * 100).toFixed(1) : '0'}%</span>
              </li>
            ))}
          </ul>
        </ChartCard>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ChartCard title="Priority distribution" loading={loading} error={b?.priority.error} empty={!b?.priority.data?.length} onRetry={reload}>
          <DonutChart data={b?.priority.data ?? []} colorFor={(n) => priorityColor(n)} />
        </ChartCard>
        <ChartCard title="Severity distribution" loading={loading} error={b?.severity.error} empty={!b?.severity.data?.length} onRetry={reload}>
          <DonutChart data={b?.severity.data ?? []} colorFor={(n) => severityColor(n)} />
        </ChartCard>
      </div>

      <div className="mt-4">
        <ChartCard
          title="Agent assignment analytics"
          subtitle={agents ? `${formatNumber(agents.totalAssignments)} total · ${formatNumber(agents.currentAssignments)} current` : undefined}
          loading={loading}
          error={b?.agents.error}
          empty={!agents || agents.agents.length === 0}
          emptyHint="The agents endpoint returned no per-agent rows."
          onRetry={reload}
        >
          <GroupedAgentBars data={agents?.agents ?? []} />
        </ChartCard>
      </div>

      <div className="mt-4">
        <ChartCard title="SLA performance" loading={loading} error={b?.sla.error} empty={!b?.sla.data} onRetry={reload}>
          <SlaPanel sla={b?.sla.data ?? {}} showChart />
        </ChartCard>
      </div>
    </>
  );
}
