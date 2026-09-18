import React, { useState } from 'react';
import { ExternalLink, Filter, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import SkeletonCard from '../components/SkeletonCard';
import EmptyState from '../components/EmptyState';
import FeedBadge from '../components/FeedBadge';

export default function NewsView({ news, status, loading }) {
  const [leanFilter, setLeanFilter] = useState('ALL');

  const filtered = news.filter((item) => {
    if (leanFilter === 'BULLISH') return item.lean > 0;
    if (leanFilter === 'BEARISH') return item.lean < 0;
    if (leanFilter === 'NEUTRAL') return item.lean === 0;
    return true;
  });

  return (
    <div className="space-y-4 pb-20">
      {/* Header Info */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900">EGX Market & Corporate News</h2>
          <p className="text-xs text-slate-500">Strictly allow-listed Egyptian & international financial outlets</p>
        </div>
        <FeedBadge status={status} />
      </div>

      {/* Lean Filter Pills */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {[
          { id: 'ALL', label: 'All News' },
          { id: 'BULLISH', label: 'Bullish (+)' },
          { id: 'BEARISH', label: 'Bearish (-)' },
          { id: 'NEUTRAL', label: 'Neutral' },
        ].map((btn) => (
          <button
            key={btn.id}
            onClick={() => setLeanFilter(btn.id)}
            className={`px-3 py-1.5 rounded-full text-[11px] font-medium whitespace-nowrap transition-all min-h-[36px] ${
              leanFilter === btn.id
                ? 'bg-slate-900 text-white'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState title="No news records in current cache" status={status} />
      ) : (
        <div className="space-y-3">
          {filtered.map((item, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm hover:border-sky-300 transition-all space-y-2"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-600">{item.outlet}</span>
                {item.lean > 0 ? (
                  <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-bold mono bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <ArrowUpRight className="w-3 h-3 text-emerald-600" /> Bullish
                  </span>
                ) : item.lean < 0 ? (
                  <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-bold mono bg-rose-50 text-rose-700 border border-rose-200">
                    <ArrowDownRight className="w-3 h-3 text-rose-600" /> Bearish
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-medium mono bg-slate-100 text-slate-600">
                    <Minus className="w-3 h-3 text-slate-400" /> Neutral
                  </span>
                )}
              </div>

              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group block"
              >
                <h3 className="text-sm font-bold text-slate-900 group-hover:text-sky-600 transition-colors leading-snug" dir="auto">
                  {item.headline}
                </h3>
              </a>

              {item.summary && (
                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed" dir="auto">
                  {item.summary}
                </p>
              )}

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-100">
                <div className="flex items-center gap-2">
                  {item.ticker && (
                    <span className="mono font-bold text-sky-700 bg-sky-50 px-1.5 py-0.5 rounded">
                      {item.ticker}
                    </span>
                  )}
                  <span className="mono">{new Date(item.published_at).toLocaleDateString()}</span>
                </div>

                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sky-600 hover:underline min-h-[32px] font-medium"
                >
                  Read Source <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
