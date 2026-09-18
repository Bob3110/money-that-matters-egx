import React from 'react';
import { Database } from 'lucide-react';

export default function EmptyState({ title, message, status }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-200 bg-white/70 p-6 text-center space-y-3 my-4">
      <div className="w-10 h-10 mx-auto rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
        <Database className="w-5 h-5" />
      </div>
      <h3 className="text-sm font-semibold text-slate-700">{title || 'No Records Found'}</h3>
      <p className="text-xs text-slate-500 max-w-xs mx-auto leading-relaxed">
        {message || 'Honest public data tracking: waiting for genuine public filings or disclosures from authorized market portals.'}
      </p>
      {status && status.mode && (
        <div className="pt-2">
          <span className="text-[11px] text-slate-400 mono">
            Status: {status.mode.toUpperCase()} • Last Attempt: {status.last_success_at ? new Date(status.last_success_at).toLocaleTimeString() : 'Pending'}
          </span>
        </div>
      )}
    </div>
  );
}
