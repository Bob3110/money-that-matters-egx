import React from 'react';
import { Landmark, ExternalLink, TrendingUp, TrendingDown, Percent } from 'lucide-react';
import SkeletonCard from '../components/SkeletonCard';
import EmptyState from '../components/EmptyState';
import FeedBadge from '../components/FeedBadge';

export default function MacroView({ macro, status, loading }) {
  return (
    <div className="space-y-4 pb-20">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Macro & Central Bank of Egypt (CBE)</h2>
          <p className="text-xs text-slate-500">Interest rate decisions, inflation reports, and treasury yields</p>
        </div>
        <FeedBadge status={status} />
      </div>

      {/* Snapshot Reference Box */}
      <div className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Key Egyptian Macro Metrics</h3>
        <div className="grid grid-cols-2 gap-2 text-center">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] text-slate-500 block">CBE Overnight Deposit</span>
            <span className="mono text-lg font-bold text-slate-900">27.25%</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] text-slate-500 block">CBE Overnight Lending</span>
            <span className="mono text-lg font-bold text-slate-900">28.25%</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : macro.length === 0 ? (
        <EmptyState
          title="No macro filings in current batch"
          message="Tracking official MPC releases, CAPMAS inflation prints, and Ministry of Finance auction results."
          status={status}
        />
      ) : (
        <div className="space-y-3">
          {macro.map((item, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm hover:border-sky-300 transition-all space-y-2"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">{item.indicator || 'CBE Policy'}</span>
                <span className="text-[10px] text-slate-400 mono">{item.source}</span>
              </div>

              <h3 className="text-sm font-bold text-slate-900 leading-snug" dir="auto">
                {item.headline}
              </h3>

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-100">
                <span className="mono">{new Date(item.published_at).toLocaleDateString()}</span>
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sky-600 hover:underline min-h-[36px]"
                  >
                    Report Link <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
