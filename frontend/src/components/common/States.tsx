import { AlertTriangle, Inbox, RefreshCw } from 'lucide-react';

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-12 text-center">
      <div className="mb-3 rounded-full bg-slate-100 p-3 text-slate-400"><Inbox size={22} /></div>
      <p className="text-sm font-semibold text-slate-700">{title}</p>
      {hint && <p className="mt-1 max-w-sm text-sm text-slate-500">{hint}</p>}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-10 text-center">
      <div className="mb-3 rounded-full bg-red-50 p-3 text-red-500"><AlertTriangle size={22} /></div>
      <p className="text-sm font-semibold text-slate-700">Couldn’t load this data</p>
      <p className="mt-1 max-w-md break-words text-sm text-slate-500">{message}</p>
      {onRetry && (
        <button className="btn-ghost mt-4" onClick={onRetry}><RefreshCw size={14} /> Try again</button>
      )}
    </div>
  );
}
