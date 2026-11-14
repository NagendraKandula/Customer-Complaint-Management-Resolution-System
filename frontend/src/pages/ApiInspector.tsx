import { useState } from 'react';
import { Copy, Play } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { useToast } from '../components/common/Toast';
import { API_BASE_URL, errorMessage, getJson } from '../services/api';

const ENDPOINTS = [
  '/api/health',
  '/api/dashboard/summary',
  '/api/dashboard/status',
  '/api/dashboard/priority',
  '/api/dashboard/severity',
  '/api/dashboard/sla',
  '/api/analytics/categories',
  '/api/analytics/agents',
  '/api/complaints',
  '/api/complaints/{complaint_id}',
];

export default function ApiInspector() {
  const [endpoint, setEndpoint] = useState(ENDPOINTS[1]);
  const [complaintId, setComplaintId] = useState('');
  const [output, setOutput] = useState('');
  const [meta, setMeta] = useState('');
  const [busy, setBusy] = useState(false);
  const { push } = useToast();

  const run = async () => {
    const url = endpoint.replace('{complaint_id}', encodeURIComponent(complaintId || '1'));
    setBusy(true);
    const t0 = performance.now();
    try {
      const data = await getJson(url);
      setOutput(JSON.stringify(data, null, 2));
      setMeta(`200 OK · ${Math.round(performance.now() - t0)} ms`);
    } catch (e) {
      setOutput('');
      setMeta('Request failed');
      push('error', errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <PageHeader title="API inspector" subtitle={`See the exact JSON each endpoint returns. Base URL: ${API_BASE_URL || '(Vite proxy → http://127.0.0.1:8000)'}`} />
      <div className="card p-4">
        <div className="flex flex-wrap items-center gap-3">
          <select className="input w-full sm:w-80" value={endpoint} onChange={(e) => setEndpoint(e.target.value)} aria-label="Endpoint">
            {ENDPOINTS.map((e) => <option key={e}>{e}</option>)}
          </select>
          {endpoint.includes('{complaint_id}') && (
            <input className="input w-40" placeholder="Complaint ID" value={complaintId} onChange={(e) => setComplaintId(e.target.value)} />
          )}
          <button className="btn-primary" onClick={run} disabled={busy}><Play size={14} /> {busy ? 'Fetching…' : 'Fetch'}</button>
          {output && (
            <button className="btn-ghost" onClick={() => { navigator.clipboard.writeText(output); push('success', 'JSON copied.'); }}>
              <Copy size={14} /> Copy
            </button>
          )}
          <span className="text-xs text-slate-500">{meta}</span>
        </div>
        <pre className="mt-4 max-h-[60vh] min-h-40 overflow-auto rounded-lg bg-navy-900 p-4 font-mono text-xs leading-relaxed text-slate-200">
          {output || 'Choose an endpoint and press Fetch.'}
        </pre>
      </div>
    </>
  );
}
