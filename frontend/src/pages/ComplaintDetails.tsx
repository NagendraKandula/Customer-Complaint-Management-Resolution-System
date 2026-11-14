import { Link, useParams } from 'react-router-dom';
import {
  ArrowLeft, ClipboardList, Clock, History, MessageSquare, Repeat, RefreshCw, ShieldAlert, Star, User, UserCog, BadgeCheck, Timer,
} from 'lucide-react';
import { useAsync } from '../hooks/useAsync';
import { getComplaintDetails } from '../services/complaintService';
import { pick } from '../services/normalize';
import { Section, KeyValue } from '../components/common/KeyValue';
import { FlagBadge, PriorityBadge, SeverityBadge, StatusBadge } from '../components/common/Badges';
import { ErrorState, EmptyState } from '../components/common/States';
import { Skeleton } from '../components/common/Skeleton';
import { StatusTimeline } from '../components/complaints/Timeline';
import { formatDate, formatMinutes, formatMoney, titleCase } from '../utils/format';
import type { Dict } from '../types';

const YesNo = ({ v }: { v: unknown }) => (v === undefined || v === null ? <>—</> : <>{v ? 'Yes' : 'No'}</>);

function nameWithFallback(a: Dict, nameKeys: string[], nested: string, idKey: string, label: string) {
  const direct = pick(a, ...nameKeys);
  if (direct) return String(direct);
  const n = a[nested];
  const fromNested = n && typeof n === 'object' ? pick(n, ...nameKeys, 'name') : undefined;
  if (fromNested) return String(fromNested);
  return a[idKey] !== undefined && a[idKey] !== null ? `${label} #${a[idKey]}` : '—';
}

function DetailsSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-10 w-72" />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2"><Skeleton className="h-48" /><Skeleton className="h-64" /></div>
        <div className="space-y-4"><Skeleton className="h-48" /><Skeleton className="h-48" /></div>
      </div>
    </div>
  );
}

export default function ComplaintDetails() {
  const { id = '' } = useParams();
  const { data, error, loading, reload } = useAsync(() => getComplaintDetails(id), [id]);

  const back = (
    <Link to="/complaints" className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-800">
      <ArrowLeft size={16} /> All complaints
    </Link>
  );

  if (loading && !data) return <>{back}<DetailsSkeleton /></>;
  if (error || !data) {
    return <>{back}<div className="card"><ErrorState message={error ?? 'Complaint not found.'} onRetry={reload} /></div></>;
  }

  const { complaint: c, customer, messages, history, assignments, resolutions, slaClocks, slaEvents, surveys } = data;
  const currentAssignment = assignments.find((a) => !a.ended_at) ?? assignments[assignments.length - 1];

  return (
    <>
      {back}

      <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Complaint <span className="font-mono">#{String(c.complaint_id ?? id)}</span></h1>
            <StatusBadge value={c.status} />
            <PriorityBadge value={c.priority} />
            <SeverityBadge value={c.severity} />
            {c.is_safety_related && <FlagBadge color="#dc2626"><span className="inline-flex items-center gap-1"><ShieldAlert size={12} /> Safety related</span></FlagBadge>}
            {c.is_repeat && <FlagBadge color="#7c3aed"><span className="inline-flex items-center gap-1"><Repeat size={12} /> Repeat{c.repeat_of_complaint_id ? ` of #${c.repeat_of_complaint_id}` : ''}</span></FlagBadge>}
          </div>
          <p className="mt-1.5 text-sm text-slate-500">
            Opened {formatDate(c.created_at, true)} · Last updated {formatDate(c.updated_at, true)}
          </p>
        </div>
        <button className="btn-ghost" onClick={reload} disabled={loading}><RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh</button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Main column */}
        <div className="space-y-4 lg:col-span-2">
          <Section title="Complaint description" icon={<ClipboardList size={16} />}>
            <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-slate-700">{c.complaint_text || 'No description provided.'}</p>
          </Section>

          <Section title={`Messages (${messages.length})`} icon={<MessageSquare size={16} />}>
            {messages.length === 0 ? (
              <EmptyState title="No messages" hint="Nothing has been exchanged on this complaint yet." />
            ) : (
              <ul className="space-y-3">
                {messages.map((m, i) => {
                  const fromCustomer = String(m.sender_type ?? '').toLowerCase() === 'customer';
                  return (
                    <li key={m.message_id ?? i} className={`flex ${fromCustomer ? 'justify-start' : 'justify-end'}`}>
                      <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${fromCustomer ? 'rounded-bl-sm bg-slate-100 text-slate-800' : 'rounded-br-sm bg-brand-600 text-white'}`}>
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.message_text}</p>
                        <p className={`mt-1.5 text-[11px] ${fromCustomer ? 'text-slate-500' : 'text-brand-100'}`}>
                          {titleCase(m.sender_type)}{m.channel ? ` · ${titleCase(m.channel)}` : ''} · {formatDate(m.sent_at, true)}
                        </p>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </Section>

          <Section title="Status history" icon={<History size={16} />}>
            {history.length === 0 ? <EmptyState title="No status changes recorded" /> : <StatusTimeline history={history} />}
          </Section>

          <Section title={`Resolution details (${resolutions.length})`} icon={<BadgeCheck size={16} />}>
            {resolutions.length === 0 ? (
              <EmptyState title="Not resolved yet" hint="Resolution cycles will appear here once an agent resolves this complaint." />
            ) : (
              <div className="space-y-3">
                {resolutions.map((r, i) => (
                  <div key={r.resolution_id ?? i} className="rounded-lg border border-slate-200 p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-semibold text-slate-900">Cycle {r.cycle_no ?? i + 1}</span>
                      {r.is_final && <FlagBadge color="#16a34a">Final</FlagBadge>}
                      {r.outcome && <FlagBadge color="#2563eb">{titleCase(r.outcome)}</FlagBadge>}
                    </div>
                    <dl className="mt-2 divide-y divide-slate-100">
                      <KeyValue label="Resolution type">{titleCase(r.resolution_type)}</KeyValue>
                      <KeyValue label="Resolved by">{r.resolved_by ?? '—'}</KeyValue>
                      <KeyValue label="Resolved at">{formatDate(r.resolved_at, true)}</KeyValue>
                      <KeyValue label="Refund amount">{formatMoney(r.refund_amount)}</KeyValue>
                    </dl>
                    {r.resolution_notes && <p className="mt-2 rounded-md bg-slate-50 p-3 text-sm text-slate-600">{r.resolution_notes}</p>}
                  </div>
                ))}
              </div>
            )}
          </Section>
        </div>

        {/* Side column */}
        <div className="space-y-4">
          <Section title="Complaint information" icon={<ClipboardList size={16} />}>
            <dl className="divide-y divide-slate-100">
              <KeyValue label="Channel">{titleCase(c.channel)}</KeyValue>
              <KeyValue label="Category ID">{c.category_id ?? '—'}</KeyValue>
              <KeyValue label="Order ID">{c.order_id ?? '—'}</KeyValue>
              <KeyValue label="Product ID">{c.product_id ?? '—'}</KeyValue>
              <KeyValue label="Sentiment">{titleCase(c.sentiment)}</KeyValue>
              <KeyValue label="Priority score">{c.priority_score ?? '—'}</KeyValue>
              <KeyValue label="Rule fired">{c.class_rule_fired ?? '—'}</KeyValue>
              <KeyValue label="Safety related"><YesNo v={c.is_safety_related} /></KeyValue>
              <KeyValue label="Repeat complaint"><YesNo v={c.is_repeat} /></KeyValue>
              <KeyValue label="Reopen count">{c.reopen_count ?? '—'}</KeyValue>
              <KeyValue label="Closed at">{formatDate(c.closed_at, true)}</KeyValue>
            </dl>
          </Section>

          <Section title="Customer" icon={<User size={16} />}>
            {customer ? (
              <dl className="divide-y divide-slate-100">
                <KeyValue label="Name">{pick(customer, 'full_name', 'name') ?? '—'}</KeyValue>
                <KeyValue label="Customer ID">{customer.customer_id ?? c.customer_id ?? '—'}</KeyValue>
                <KeyValue label="Email">{customer.email ?? '—'}</KeyValue>
                <KeyValue label="Phone">{customer.phone ?? '—'}</KeyValue>
                <KeyValue label="Tier">{titleCase(customer.customer_tier)}</KeyValue>
                <KeyValue label="Vulnerable customer"><YesNo v={customer.is_vulnerable} /></KeyValue>
              </dl>
            ) : (
              <p className="text-sm text-slate-500">Customer #{String(c.customer_id ?? '—')} · no further details in the response.</p>
            )}
          </Section>

          <Section title="Assignment" icon={<UserCog size={16} />}>
            {assignments.length === 0 ? (
              <EmptyState title="Unassigned" hint="No agent or team has been assigned yet." />
            ) : (
              <>
                {currentAssignment && (
                  <dl className="divide-y divide-slate-100">
                    <KeyValue label="Agent">{nameWithFallback(currentAssignment, ['agent_name'], 'agent', 'agent_id', 'Agent')}</KeyValue>
                    <KeyValue label="Team">{nameWithFallback(currentAssignment, ['team_name'], 'team', 'team_id', 'Team')}</KeyValue>
                    <KeyValue label="Assigned">{formatDate(currentAssignment.assigned_at, true)}</KeyValue>
                    <KeyValue label="Reason">{titleCase(currentAssignment.assignment_reason)}</KeyValue>
                    <KeyValue label="State">{currentAssignment.ended_at ? `Ended ${formatDate(currentAssignment.ended_at, true)}` : 'Current'}</KeyValue>
                  </dl>
                )}
                {assignments.length > 1 && (
                  <details className="mt-3 text-sm">
                    <summary className="cursor-pointer font-medium text-brand-700">Assignment history ({assignments.length})</summary>
                    <ul className="mt-2 space-y-2">
                      {assignments.map((a, i) => (
                        <li key={a.assignment_id ?? i} className="rounded-md bg-slate-50 p-2.5 text-xs text-slate-600">
                          <span className="font-semibold text-slate-800">{nameWithFallback(a, ['agent_name'], 'agent', 'agent_id', 'Agent')}</span>
                          {' · '}{nameWithFallback(a, ['team_name'], 'team', 'team_id', 'Team')}
                          <br />{formatDate(a.assigned_at, true)} → {a.ended_at ? formatDate(a.ended_at, true) : 'now'}
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </>
            )}
          </Section>
        </div>
      </div>

      <div className="mt-4">
        <Section title="SLA" icon={<Timer size={16} />}>
          {slaClocks.length === 0 ? (
            <EmptyState title="No SLA clock" hint="This complaint has no SLA record in the response." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {slaClocks.map((s, i) => (
                <div key={s.sla_id ?? i} className="rounded-lg border border-slate-200 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    {s.priority_level && <PriorityBadge value={s.priority_level} />}
                    {s.response_breached ? <FlagBadge color="#dc2626">Response breached</FlagBadge> : <FlagBadge color="#16a34a">Response on track</FlagBadge>}
                    {s.resolution_breached ? <FlagBadge color="#ea580c">Resolution breached</FlagBadge> : <FlagBadge color="#16a34a">Resolution on track</FlagBadge>}
                    {s.is_paused && <FlagBadge color="#64748b">Paused</FlagBadge>}
                  </div>
                  <dl className="mt-2 divide-y divide-slate-100">
                    <KeyValue label="Started">{formatDate(s.started_at, true)}</KeyValue>
                    <KeyValue label="Response deadline">{formatDate(s.response_deadline, true)}</KeyValue>
                    <KeyValue label="First response">{formatDate(s.first_response_at, true)}</KeyValue>
                    <KeyValue label="Resolution deadline">{formatDate(s.resolution_deadline, true)}</KeyValue>
                    <KeyValue label="Resolved">{formatDate(s.resolved_at, true)}</KeyValue>
                    <KeyValue label="Total paused">{formatMinutes(s.total_paused_minutes)}</KeyValue>
                  </dl>
                </div>
              ))}
            </div>
          )}

          {slaEvents.length > 0 && (
            <div className="mt-5">
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-900"><Clock size={15} className="text-slate-400" /> SLA events</h3>
              <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200">
                {slaEvents.map((e, i) => (
                  <li key={e.sla_event_id ?? i} className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5 text-sm">
                    <span className="font-medium text-slate-800">{titleCase(e.event_type)}</span>
                    <span className="text-slate-500">{e.reason ?? ''}</span>
                    <span className="text-xs text-slate-400">{formatDate(e.event_time, true)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Section>
      </div>

      {surveys.length > 0 && (
        <div className="mt-4">
          <Section title="Customer survey" icon={<Star size={16} />}>
            <div className="grid gap-3 md:grid-cols-2">
              {surveys.map((s, i) => (
                <div key={s.survey_id ?? i} className="rounded-lg border border-slate-200 p-4">
                  <p className="text-sm font-semibold text-slate-900">{s.rating !== undefined && s.rating !== null ? `Rating ${s.rating}` : 'Not yet rated'}</p>
                  <p className="mt-1 text-xs text-slate-500">Sent {formatDate(s.sent_at, true)} · Submitted {formatDate(s.submitted_at, true)}</p>
                  {s.feedback && <p className="mt-2 text-sm text-slate-600">{s.feedback}</p>}
                </div>
              ))}
            </div>
          </Section>
        </div>
      )}

      <details className="mt-6 text-sm">
        <summary className="cursor-pointer text-slate-500 hover:text-slate-800">Raw API response</summary>
        <pre className="mt-2 max-h-96 overflow-auto rounded-lg bg-navy-900 p-4 font-mono text-xs text-slate-200">{JSON.stringify(data.raw, null, 2)}</pre>
      </details>
    </>
  );
}
