import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { EmptyState, ErrorState } from '../components/common/States';
import { TableSkeleton } from '../components/common/Skeleton';
import { useToast } from '../components/common/Toast';
import { ComplaintFilterBar, type FilterValues } from '../components/complaints/ComplaintFilterBar';
import { ComplaintTable } from '../components/complaints/ComplaintTable';
import { Pagination } from '../components/complaints/Pagination';
import { useAsync } from '../hooks/useAsync';
import { getComplaints } from '../services/complaintService';
import { getSeverityDistribution, getStatusDistribution } from '../services/dashboardService';

const PAGE_SIZE = 15;

export default function Complaints() {
  const [params, setParams] = useSearchParams();
  const { push } = useToast();

  const page = Math.max(1, Number(params.get('page')) || 1);
  const values: FilterValues = {
    search: params.get('q') ?? '',
    status: params.get('status') ?? '',
    priority: params.get('priority') ?? '',
    severity: params.get('severity') ?? '',
    channel: params.get('channel') ?? '',
  };

  const [searchInput, setSearchInput] = useState(values.search);
  const [channels, setChannels] = useState<string[]>([]);

  const update = (patch: Record<string, string | number | undefined>) =>
    setParams((prev) => {
      const next = new URLSearchParams(prev);
      for (const [k, v] of Object.entries(patch)) {
        if (v === undefined || v === '' || (k === 'page' && v === 1)) next.delete(k);
        else next.set(k, String(v));
      }
      return next;
    }, { replace: true });

  // Debounce the search box
  useEffect(() => {
    if (searchInput === values.search) return;
    const t = setTimeout(() => update({ q: searchInput, page: 1 }), 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  const { data, error, loading, reload } = useAsync(
    () => getComplaints({ page, pageSize: PAGE_SIZE, search: values.search, status: values.status, priority: values.priority, severity: values.severity, channel: values.channel }),
    [page, values.search, values.status, values.priority, values.severity, values.channel],
  );

  // Filter option lists come from the dashboard endpoints (status, severity) and from channels seen so far.
  const statusOpts = useAsync(() => getStatusDistribution(), []);
  const severityOpts = useAsync(() => getSeverityDistribution(), []);

  useEffect(() => {
    if (!data) return;
    setChannels((prev) => {
      const set = new Set(prev);
      data.items.forEach((c) => c.channel && set.add(String(c.channel)));
      return [...set].sort();
    });
  }, [data]);

  useEffect(() => { if (error) push('error', 'Could not load complaints.'); }, [error, push]);

  const statusOptions = useMemo(() => (statusOpts.data ?? []).map((d) => d.name), [statusOpts.data]);
  const severityOptions = useMemo(() => (severityOpts.data ?? []).map((d) => d.name), [severityOpts.data]);

  const onChange = (patch: Partial<FilterValues>) => {
    if ('search' in patch) { setSearchInput(patch.search ?? ''); return; }
    update({ ...patch, page: 1 });
  };
  const reset = () => { setSearchInput(''); setParams({}, { replace: true }); };

  return (
    <>
      <PageHeader
        title="Complaints"
        subtitle="Search, filter and open any complaint to see its full history."
        actions={<button className="btn-ghost" onClick={reload} disabled={loading}><RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh</button>}
      />
      <div className="card overflow-hidden">
        <ComplaintFilterBar
          values={{ ...values, search: searchInput }}
          onChange={onChange}
          onReset={reset}
          statusOptions={statusOptions}
          severityOptions={severityOptions}
          channelOptions={channels}
        />
        {loading && !data ? (
          <TableSkeleton />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : !data || data.items.length === 0 ? (
          <EmptyState title="No complaints match" hint="Try removing a filter or searching for a different term." />
        ) : (
          <div className={loading ? 'opacity-60 transition-opacity' : ''}>
            <ComplaintTable items={data.items} />
            <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onPage={(p) => { update({ page: p }); window.scrollTo({ top: 0 }); }} />
          </div>
        )}
      </div>
    </>
  );
}
