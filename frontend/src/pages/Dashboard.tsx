import { useEffect, useRef } from 'react';
import { Activity, CheckCircle2, FileText, FolderOpen, RefreshCw, RotateCcw, Users, Archive } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { useToast } from '../components/common/Toast';
import { StatCard } from '../components/dashboard/StatCard';
import { ChartCard } from '../components/dashboard/ChartCard';
import { ColumnChart, DonutChart, HorizontalBars, GroupedAgentBars } from '../components/dashboard/Charts';
import { SlaPanel } from '../components/dashboard/SlaPanel';
import { useDashboardData } from '../hooks/useDashboardData';
import { priorityColor, severityColor, statusColor } from '../utils/colors';
import { formatNumber } from '../utils/format';

export default function Dashboard() {
  const { bundle: b, loading, reload } = useDashboardData();
  const { push } = useToast();
  const warned = useRef(false);

  useEffect(() => {
    if (!b || warned.current) return;
    const failed = Object.entries(b).filter(([, s]) => s.error).map(([k]) => k);
    if (failed.length) {
      warned.current = true;
      push('error', `Could not load: ${failed.join(', ')}.`);
    }
  }, [b, push]);

  const s = b?.summary;
  const stat = (key: 'total' | 'open' | 'resolved' | 'closed' | 'reopened') => s?.data?.[key];

  const agentsHaveData = !!b?.agents.data && b.agents.data.agents.length > 0;

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="Live overview of complaint volume, SLA health and team workload."
        actions={<button className="btn-ghost" onClick={reload} disabled={loading}><RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh</button>}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Total complaints" value={stat('total')} icon={FileText} color="#3b6df0" loading={loading} error={!!s?.error} />
        <StatCard label="Open" value={stat('open')} icon={FolderOpen} color="#2563eb" loading={loading} error={!!s?.error} />
        <StatCard label="Resolved" value={stat('resolved')} icon={CheckCircle2} color="#16a34a" loading={loading} error={!!s?.error} />
        <StatCard label="Closed" value={stat('closed')} icon={Archive} color="#6b7280" loading={loading} error={!!s?.error} />
        <StatCard label="Reopened" value={stat('reopened')} icon={RotateCcw} color="#db2777" loading={loading} error={!!s?.error} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ChartCard title="Complaints by status" loading={loading} error={b?.status.error} empty={!b?.status.data?.length} onRetry={reload}>
          <DonutChart data={b?.status.data ?? []} colorFor={(n) => statusColor(n)} />
        </ChartCard>
        <ChartCard title="Complaints by priority" subtitle="P1 is most urgent" loading={loading} error={b?.priority.error} empty={!b?.priority.data?.length} onRetry={reload}>
          <ColumnChart data={b?.priority.data ?? []} colorFor={(n) => priorityColor(n)} />
        </ChartCard>
        <ChartCard title="Complaints by severity" loading={loading} error={b?.severity.error} empty={!b?.severity.data?.length} onRetry={reload}>
          <ColumnChart data={b?.severity.data ?? []} colorFor={(n) => severityColor(n)} />
        </ChartCard>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <ChartCard title="Category analytics" subtitle="Complaints per category" loading={loading} error={b?.categories.error} empty={!b?.categories.data?.length} onRetry={reload}>
          <HorizontalBars data={b?.categories.data ?? []} />
        </ChartCard>

        <ChartCard title="Agent analytics" subtitle="Assignments across the support team" loading={loading} error={b?.agents.error} empty={!b?.agents.data || (b.agents.data.totalAssignments === undefined && b.agents.data.currentAssignments === undefined && !agentsHaveData)} onRetry={reload}>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-slate-100 bg-slate-50/60 p-3">
              <p className="flex items-center gap-2 text-xs text-slate-500"><Users size={14} /> Total assignments</p>
              <p className="mt-1 text-xl font-bold text-slate-900">{formatNumber(b?.agents.data?.totalAssignments)}</p>
            </div>
            <div className="rounded-lg border border-slate-100 bg-slate-50/60 p-3">
              <p className="flex items-center gap-2 text-xs text-slate-500"><Activity size={14} /> Current assignments</p>
              <p className="mt-1 text-xl font-bold text-slate-900">{formatNumber(b?.agents.data?.currentAssignments)}</p>
            </div>
          </div>
          {agentsHaveData && (
            <div className="mt-4">
              <p className="mb-1 text-xs font-medium text-slate-500">Agent workload</p>
              <GroupedAgentBars data={b!.agents.data!.agents} height={Math.min(340, Math.max(200, b!.agents.data!.agents.length * 40 + 60))} />
            </div>
          )}
        </ChartCard>
      </div>

      <div className="mt-4">
        <ChartCard title="SLA monitoring" subtitle="Response and resolution performance" loading={loading} error={b?.sla.error} empty={!b?.sla.data} onRetry={reload}>
          <SlaPanel sla={b?.sla.data ?? {}} />
        </ChartCard>
      </div>
    </>
  );
}
