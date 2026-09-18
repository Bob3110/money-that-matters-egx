import React, { useState } from 'react';
import { ExternalLink, ArrowUpRight, ArrowDownRight, ShieldCheck, Filter } from 'lucide-react';
import SkeletonCard from '../components/SkeletonCard';
import EmptyState from '../components/EmptyState';
import FeedBadge from '../components/FeedBadge';

export default function InsidersView({ insiders, status, loading }) {
  const [buysOnly, setBuysOnly] = useState(false);

  const filtered = buysOnly
    ? insiders.filter((i) => i.transaction_type.includes('Buy') || i.transaction_type.includes('Treasury'))
    : insiders;

  return (
    <div className="space-y-4 pb-20">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Corporate Insiders & Treasury Shares</h2>
          <p className="text-xs text-slate-500">Board members, executives, and treasury buyback filings</p>
        </div>
        <FeedBadge status={status} />
      </div>

      {/* Filter Toggle */}
      <div className="flex items-center justify-between bg-white p-3 rounded-2xl border border-slate-200/80 shadow-2xs">
        <span className="text-xs font-medium text-slate-700">Filter Buys & Buybacks Only</span>
        <button
          onClick={() => setBuysOnly(!buysOnly)}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all min-h-[36px] ${
            buysOnly
              ? 'bg-emerald-600 text-white shadow-xs'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          {buysOnly ? '✓ Buys Only' : 'Show All Trades'}
        </button>
      </div>

      {loading ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No insider transactions found"
          message="Public disclosures are reported on legal/market delays via EGX Form disclosures."
          status={status}
        />
      ) : (
        <div className="space-y-3">
          {filtered.map((item, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm hover:border-sky-300 transition-all space-y-2.5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="mono text-base font-bold text-slate-900">{item.ticker}</span>
                  <h3 className="text-xs font-medium text-slate-600" dir="auto">{item.company_name}</h3>
                </div>
                <span className={`px-2.5 py-1 rounded-lg text-xs font-bold mono ${
                  item.transaction_type.includes('Buy')
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-rose-50 text-rose-700 border border-rose-200'
                }`}>
                  {item.transaction_type}
                </span>
              </div>

              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-500">Insider Role:</span>
                <span className="font-semibold text-slate-800">{item.insider_title}</span>
              </div>

              {/* Partial Real Data Honesty Rule */}
              {item.omission_reason && (
                <div className="text-[11px] text-slate-500 bg-amber-50/70 border border-amber-200/60 p-2 rounded-xl">
                  <strong>Filing Notice:</strong> {item.omission_reason}
                </div>
              )}

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-100">
                <span className="mono">Filing Date: {new Date(item.filing_date).toLocaleDateString()}</span>
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sky-600 hover:underline font-medium min-h-[36px]"
                  >
                    Original Disclosure <ExternalLink className="w-3 h-3" />
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
