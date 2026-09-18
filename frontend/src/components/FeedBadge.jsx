import React from 'react';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export default function FeedBadge({ status }) {
  if (!status) return null;
  const mode = status.mode || 'empty';

  if (mode === 'live') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/80">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        Live
      </span>
    );
  }

  if (mode === 'stale') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
        <Clock className="w-3 h-3 text-amber-500" />
        Stale (&gt;24h)
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
      <AlertCircle className="w-3 h-3 text-slate-400" />
      Awaiting sync
    </span>
  );
}
