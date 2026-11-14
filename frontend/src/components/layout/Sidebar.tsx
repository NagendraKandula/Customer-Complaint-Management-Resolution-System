import { NavLink } from 'react-router-dom';
import { BarChart3, Code2, FileText, LayoutDashboard, LifeBuoy, X } from 'lucide-react';

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/complaints', label: 'Complaints', icon: FileText },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/inspector', label: 'API inspector', icon: Code2 },
];

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-navy-950/60 lg:hidden" onClick={onClose} />}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-navy-900 text-slate-300 transition-transform lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between px-5">
          <div className="flex items-center gap-2.5">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-brand-500 text-white"><LifeBuoy size={18} /></div>
            <div className="leading-tight">
              <p className="text-[15px] font-bold text-white">Resolve</p>
              <p className="text-[11px] text-slate-400">Complaint management</p>
            </div>
          </div>
          <button className="text-slate-400 lg:hidden" onClick={onClose} aria-label="Close menu"><X size={20} /></button>
        </div>

        <nav className="mt-4 flex-1 space-y-1 px-3">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive ? 'bg-navy-700 text-white' : 'text-slate-400 hover:bg-navy-800 hover:text-slate-100'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="m-3 rounded-lg bg-navy-800 p-3 text-xs text-slate-400">
          Connected to FastAPI backend. Data is read-only.
        </div>
      </aside>
    </>
  );
}
