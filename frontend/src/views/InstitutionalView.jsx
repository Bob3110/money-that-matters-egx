import React from 'react';
import { Building2, ExternalLink, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import SkeletonCard from '../components/SkeletonCard';
import EmptyState from '../components/EmptyState';
import FeedBadge from '../components/FeedBadge';

export default function InstitutionalView({ institutional, status, loading }) {
  return (
    <div className="space-y-4 pb-20">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Institutional & Major Holders</h2>
          <p className="text-xs text-slate-500">Substantial stakes (&gt;5%) & daily institutional capital flow breakdowns</p>
        </div>
        <FeedBadge status={status} />
      </div>

      {loading ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : institutional.length === 0 ? (
        <EmptyState
          title="No institutional records in cache"
          message="Waiting for EGX end-of-day bulletins and FRA substantial shareholder notices."
          status={status}
        />
      ) : (
        <div className="space-y-3">
          {institutional.map((item, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm hover:border-sky-300 transition-all space-y-2.5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="mono text-sm font-bold text-slate-900 block">{item.ticker}</span>
                  <span className="text-xs font-semibold text-slate-700">{item.investor_entity}</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-bold mono ${
                  item.transaction_type.includes('Buy')
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-rose-50 text-rose-700 border border-rose-200'
                }`}>
                  {item.transaction_type}
                </span>
              </div>

              {item.omission_reason && (
                <p className="text-[11px] text-slate-500 bg-slate-50 p-2 rounded-xl border border-slate-100">
                  {item.omission_reason}
                </p>
              )}

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-100">
                <span className="mono">Date: {new Date(item.disclosure_date).toLocaleDateString()}</span>
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sky-600 hover:underline min-h-[36px]"
                  >
                    View Notice <ExternalLink className="w-3 h-3" />
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
