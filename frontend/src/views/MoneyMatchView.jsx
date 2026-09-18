import React, { useState } from 'react';
import { Search, Zap, ArrowUpRight, ArrowDownRight, ChevronRight, Star } from 'lucide-react';
import SkeletonCard from '../components/SkeletonCard';
import EmptyState from '../components/EmptyState';

export default function MoneyMatchView({ scores, loading, onSelectTicker, onToggleWatchlist, watchlist }) {
  const [search, setSearch] = useState('');
  const [selectedSector, setSelectedSector] = useState('ALL');

  const sectors = React.useMemo(() => {
    const unique = Array.from(new Set(scores.map((s) => s.sector))).filter(Boolean).sort();
    return ['ALL', ...unique];
  }, [scores]);

  const cleanSearch = search.toLowerCase().trim();
  const isGourmetQuery = cleanSearch === 'gour' || cleanSearch.includes('gourmet') || search.includes('جورميه');

  const filtered = scores.filter((item) => {
    const matchesSearch = 
      item.ticker.toLowerCase().includes(cleanSearch) ||
      item.name_en.toLowerCase().includes(cleanSearch) ||
      item.name_ar.includes(search) ||
      (item.ticker === 'BINV.CA' && isGourmetQuery);
    const matchesSector = selectedSector === 'ALL' || item.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  return (
    <div className="space-y-4 pb-20">
      {/* Hero Explainer Card */}
      <div className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-bold tracking-wider uppercase text-sky-700">Hero Algorithm</span>
          <span className="text-[11px] font-semibold text-slate-500 mono bg-slate-100 px-2 py-0.5 rounded-full">
            {scores.length > 0 ? `${scores.length} EGX Equities` : '0 - 100 Scale'}
          </span>
        </div>
        <h2 className="text-sm font-bold text-slate-900 mb-1">Money Match Agreement</h2>
        <p className="text-xs text-slate-600 leading-relaxed">
          Scores how strongly Insiders, Institutional Flows, and Public Disclosures lean in the <strong>same direction</strong> across all Egyptian Exchange listed companies.
          1 source caps at 33, 2 sources at 67, and all 3 agreeing reaches 100.
        </p>
      </div>

      {/* Search & Sector Filters */}
      <div className="space-y-2">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search all ~230+ EGX tickers or companies (e.g. COMI, فوري, EKHO)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all shadow-2xs"
          />
        </div>

        {/* Smart Ticker Hint for Gourmet */}
        {isGourmetQuery && (
          <div className="p-3 rounded-xl bg-sky-50/80 border border-sky-200 text-sky-950 text-xs flex items-start gap-2.5 animate-in fade-in duration-150">
            <span className="text-sm shrink-0">💡</span>
            <div className="space-y-0.5">
              <p className="font-semibold text-sky-900">Looking for Gourmet Egypt?</p>
              <p className="text-[11px] text-sky-800 leading-relaxed">
                Gourmet is <strong>not independently listed</strong> as a standalone stock (there is no official ticker <code className="mono font-bold bg-sky-100 px-1 py-0.2 rounded">GOUR</code> on EGX). It is a 68% subsidiary of <strong>B Investments Holding (<code className="mono font-bold bg-sky-100 px-1 py-0.2 rounded">BINV.CA</code>)</strong> shown below.
              </p>
            </div>
          </div>
        )}

        {/* Horizontal scrollable sector pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
          {sectors.map((sec) => (
            <button
              key={sec}
              onClick={() => setSelectedSector(sec)}
              className={`px-3 py-1.5 rounded-full text-[11px] font-medium whitespace-nowrap transition-all min-h-[32px] ${
                selectedSector === sec
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {sec}
            </button>
          ))}
        </div>
      </div>

      {/* Tickers Leaderboard */}
      {loading ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState title="No matching tickers found" message="Try searching for a different EGX ticker code or clear sector filters." />
      ) : (
        <div className="space-y-2.5">
          {filtered.map((item) => {
            const isWatchlisted = watchlist.includes(item.ticker);
            const isStrong = item.strong_match;
            return (
              <div
                key={item.ticker}
                onClick={() => onSelectTicker(item)}
                className="rounded-2xl border border-slate-200/80 bg-white p-3.5 shadow-sm hover:border-sky-300 hover:shadow-md transition-all active:scale-[0.99] cursor-pointer flex items-center justify-between gap-3 min-h-[64px]"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {/* Score Pill */}
                  <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col items-center justify-center shrink-0">
                    <span className="mono text-base font-extrabold text-slate-900 leading-none">{item.score}</span>
                    <span className="mono text-[9px] text-slate-400 uppercase mt-0.5">SCORE</span>
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="mono font-bold text-sm text-slate-900 tracking-tight">{item.ticker}</span>
                      {isStrong && (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                          <Zap className="w-2.5 h-2.5 fill-amber-400 text-amber-500" /> ⚡ Match
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-700 font-medium truncate" dir="auto">{item.name_ar}</p>
                    <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                      <span>{item.sector}</span>
                      <span>•</span>
                      <span className="mono text-slate-500">{item.active_sources_count}/3 signals</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {item.direction === 'bullish' ? (
                    <span className="inline-flex items-center gap-0.5 px-2 py-1 rounded-lg text-[10px] font-bold mono bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <ArrowUpRight className="w-3 h-3 text-emerald-600" /> BUY
                    </span>
                  ) : item.direction === 'bearish' ? (
                    <span className="inline-flex items-center gap-0.5 px-2 py-1 rounded-lg text-[10px] font-bold mono bg-rose-50 text-rose-700 border border-rose-200">
                      <ArrowDownRight className="w-3 h-3 text-rose-600" /> SELL
                    </span>
                  ) : (
                    <span className="px-2 py-1 rounded-lg text-[10px] font-medium mono bg-slate-100 text-slate-500">
                      NEUT
                    </span>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleWatchlist(item.ticker);
                    }}
                    className={`w-9 h-9 min-w-[36px] min-h-[36px] rounded-lg flex items-center justify-center text-sm border transition-colors ${
                      isWatchlisted ? 'bg-amber-50 border-amber-200 text-amber-500' : 'bg-white border-slate-200 text-slate-300 hover:text-slate-500'
                    }`}
                  >
                    ★
                  </button>
                  <ChevronRight className="w-4 h-4 text-slate-300" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
