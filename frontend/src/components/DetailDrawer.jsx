import React from 'react';
import { X, ExternalLink, ShieldAlert, Zap, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export default function DetailDrawer({ tickerData, detailData, onClose, onToggleWatchlist, isWatchlisted }) {
  if (!tickerData) return null;

  const score = tickerData.score;
  const isStrong = tickerData.strong_match;
  const signals = tickerData.signals || {};

  const renderLeanBadge = (lean, stale) => {
    if (stale) {
      return <span className="px-2 py-0.5 rounded text-[10px] mono bg-amber-50 text-amber-700 border border-amber-200">STALE (EXCLUDED)</span>;
    }
    if (lean > 0) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] mono bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
          <ArrowUpRight className="w-3 h-3 text-emerald-600" /> BULLISH (+1)
        </span>
      );
    }
    if (lean < 0) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] mono bg-rose-50 text-rose-700 border border-rose-200 font-semibold">
          <ArrowDownRight className="w-3 h-3 text-rose-600" /> BEARISH (-1)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] mono bg-slate-100 text-slate-600 border border-slate-200">
        <Minus className="w-3 h-3 text-slate-400" /> NEUTRAL (0)
      </span>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-slate-900/40 backdrop-blur-sm p-0 sm:p-4 animate-in fade-in duration-200">
      <div 
        className="w-full max-w-lg bg-white rounded-t-3xl sm:rounded-2xl max-h-[88vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-100 flex items-start justify-between bg-slate-50/70">
          <div>
            <div className="flex items-center gap-2">
              <span className="mono text-lg font-bold tracking-tight text-slate-900">{tickerData.ticker}</span>
              {isStrong && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                  <Zap className="w-3 h-3 fill-amber-400 text-amber-500" /> Strong Match
                </span>
              )}
            </div>
            <h2 className="text-sm text-slate-600 font-medium line-clamp-1" dir="auto">{tickerData.name_ar}</h2>
            <p className="text-xs text-slate-400 line-clamp-1">{tickerData.name_en}</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onToggleWatchlist(tickerData.ticker)}
              className={`p-2 rounded-full border min-w-[44px] min-h-[44px] flex items-center justify-center transition-colors ${
                isWatchlisted ? 'bg-amber-50 border-amber-200 text-amber-500' : 'bg-white border-slate-200 text-slate-400 hover:text-slate-700'
              }`}
            >
              ★
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-full border border-slate-200 bg-white hover:bg-slate-100 text-slate-500 min-w-[44px] min-h-[44px] flex items-center justify-center"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Score Breakdown Banner */}
        <div className="p-4 border-b border-slate-100 bg-white flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 block">Money Match Agreement</span>
            <div className="flex items-baseline gap-1">
              <span className="mono text-3xl font-extrabold text-slate-900">{score}</span>
              <span className="mono text-xs text-slate-400">/ 100</span>
            </div>
          </div>
          <div className="text-right">
            <span className="text-[11px] text-slate-500 block">Active Signal Agreement</span>
            <span className="mono text-xs font-semibold text-slate-700">
              {tickerData.active_sources_count} of 3 Sources ({tickerData.direction.toUpperCase()})
            </span>
          </div>
        </div>

        {/* Signals 3-Column Visualizer */}
        <div className="grid grid-cols-3 gap-2 p-4 bg-slate-50/50 border-b border-slate-100 text-center">
          <div className="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
            <span className="text-[11px] text-slate-500 font-medium block mb-1">EGX News</span>
            {renderLeanBadge(signals.news?.lean ?? 0, signals.news?.stale)}
          </div>
          <div className="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
            <span className="text-[11px] text-slate-500 font-medium block mb-1">Insiders</span>
            {renderLeanBadge(signals.insiders?.lean ?? 0, signals.insiders?.stale)}
          </div>
          <div className="p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
            <span className="text-[11px] text-slate-500 font-medium block mb-1">Institutions</span>
            {renderLeanBadge(signals.institutional?.lean ?? 0, signals.institutional?.stale)}
          </div>
        </div>

        {/* Scrollable Content: Underlying Records Driving the Score */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Underlying Market News</h3>
            {detailData?.underlying?.news?.length ? (
              <div className="space-y-2">
                {detailData.underlying.news.map((item, idx) => (
                  <a
                    key={idx}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-3 rounded-xl border border-slate-200 bg-white hover:border-sky-300 transition-all text-xs"
                  >
                    <p className="font-medium text-slate-900 leading-snug" dir="auto">{item.headline}</p>
                    <div className="flex items-center justify-between mt-2 text-[10px] text-slate-400">
                      <span>{item.outlet} • {new Date(item.published_at).toLocaleDateString()}</span>
                      <ExternalLink className="w-3 h-3 text-slate-400" />
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No direct ticker-specific headline in recent allow-listed cycle.</p>
            )}
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Recent Insider Disclosures</h3>
            {detailData?.underlying?.insiders?.length ? (
              <div className="space-y-2">
                {detailData.underlying.insiders.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-xl border border-slate-200 bg-white text-xs space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-800">{item.insider_title}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        item.transaction_type.includes('Buy') ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                      }`}>
                        {item.transaction_type}
                      </span>
                    </div>
                    {item.omission_reason && (
                      <p className="text-[11px] text-slate-400 italic">
                        {item.omission_reason}
                      </p>
                    )}
                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
                      <span className="mono">{new Date(item.filing_date).toLocaleDateString()}</span>
                      {item.source_url && (
                        <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline inline-flex items-center gap-0.5">
                          Filing Notice <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No formal insider or treasury buyback filings recorded in recent public batches.</p>
            )}
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Institutional Position Lean</h3>
            {detailData?.underlying?.institutional?.length ? (
              <div className="space-y-2">
                {detailData.underlying.institutional.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-xl border border-slate-200 bg-white text-xs space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-800">{item.investor_entity}</span>
                      <span className="mono font-bold text-slate-700">{item.transaction_type}</span>
                    </div>
                    {item.omission_reason && (
                      <p className="text-[11px] text-slate-400 italic">
                        {item.omission_reason}
                      </p>
                    )}
                    <span className="text-[10px] text-slate-400 mono block">
                      Disclosure: {new Date(item.disclosure_date).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">Neutral market-wide institutional balance.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
