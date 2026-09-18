import React from 'react';
import { Star, ChevronRight, Zap, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import EmptyState from '../components/EmptyState';

export default function WatchlistView({ scores, watchlist, onSelectTicker, onToggleWatchlist }) {
  const watchlistedItems = scores.filter((s) => watchlist.includes(s.ticker));

  return (
    <div className="space-y-4 pb-20">
      <div>
        <h2 className="text-sm font-bold text-slate-900">Custom Saved Watchlist</h2>
        <p className="text-xs text-slate-500">Persisted locally in your browser for fast monitoring</p>
      </div>

      {watchlistedItems.length === 0 ? (
        <EmptyState
          title="Your Watchlist is empty"
          message="Tap the star icon (★) on any EGX stock in the Money Match leaderboard to pin it here."
        />
      ) : (
        <div className="space-y-2.5">
          {watchlistedItems.map((item) => (
            <div
              key={item.ticker}
              onClick={() => onSelectTicker(item)}
              className="rounded-2xl border border-slate-200/80 bg-white p-3.5 shadow-sm hover:border-sky-300 transition-all cursor-pointer flex items-center justify-between gap-3 min-h-[64px]"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col items-center justify-center shrink-0">
                  <span className="mono text-base font-extrabold text-slate-900">{item.score}</span>
                  <span className="mono text-[9px] text-slate-400">SCORE</span>
                </div>

                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="mono font-bold text-sm text-slate-900">{item.ticker}</span>
                    {item.strong_match && (
                      <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                        <Zap className="w-2.5 h-2.5 fill-amber-400 text-amber-500" /> Match
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-700 font-medium truncate" dir="auto">{item.name_ar}</p>
                  <span className="text-[11px] text-slate-400">{item.sector}</span>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleWatchlist(item.ticker);
                  }}
                  className="w-9 h-9 min-w-[36px] min-h-[36px] rounded-lg flex items-center justify-center text-sm border bg-amber-50 border-amber-200 text-amber-500"
                >
                  ★
                </button>
                <ChevronRight className="w-4 h-4 text-slate-300" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
