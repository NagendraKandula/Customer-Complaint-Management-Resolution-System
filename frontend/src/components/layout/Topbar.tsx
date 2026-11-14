import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Search } from 'lucide-react';
import { checkHealth } from '../../services/api';
import { useToast } from '../common/Toast';

export function Topbar({ onMenu }: { onMenu: () => void }) {
  const [online, setOnline] = useState<boolean | null>(null);
  const [id, setId] = useState('');
  const prev = useRef<boolean | null>(null);
  const navigate = useNavigate();
  const { push } = useToast();

  useEffect(() => {
    let alive = true;
    const ping = async () => {
      let ok = false;
      try { await checkHealth(); ok = true; } catch { ok = false; }
      if (!alive) return;
      setOnline(ok);
      if (prev.current !== null && prev.current !== ok) {
        push(ok ? 'success' : 'error', ok ? 'Backend connection restored.' : 'Lost connection to the backend.');
      }
      prev.current = ok;
    };
    ping();
    const t = setInterval(ping, 30000);
    return () => { alive = false; clearInterval(t); };
  }, [push]);

  const go = (e: React.FormEvent) => {
    e.preventDefault();
    const v = id.trim().replace(/^#/, '');
    if (v) { navigate(`/complaints/${encodeURIComponent(v)}`); setId(''); }
  };

  const dot = online === null ? 'bg-slate-300' : online ? 'bg-emerald-500' : 'bg-red-500';
  const label = online === null ? 'Checking…' : online ? 'Backend online' : 'Backend offline';

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-slate-200 bg-white/90 px-4 backdrop-blur sm:px-6">
      <button className="btn-ghost !px-2 lg:hidden" onClick={onMenu} aria-label="Open menu"><Menu size={18} /></button>

      <form onSubmit={go} className="relative w-full max-w-xs">
        <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          className="input pl-9"
          placeholder="Open complaint by ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
          aria-label="Open complaint by ID"
        />
      </form>

      <div className="ml-auto flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600">
        <span className={`h-2 w-2 rounded-full ${dot}`} />
        {label}
      </div>
    </header>
  );
}
