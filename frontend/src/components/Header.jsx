import React from 'react';
import { RotateCw } from 'lucide-react';

export default function Header({ onRefresh, isRefreshing, lastUpdated }) {
  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-slate-200/80 px-4 py-3 sm:px-6">
      <div className="max-w-xl mx-auto flex items-center justify-between">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <h1 className="text-base sm:text-lg font-bold tracking-tight text-slate-900">
              Money that matters <span className="text-slate-400 font-normal">—</span> <span className="mono text-sky-600 font-bold">EGX</span>
            </h1>
          </div>
          <p className="text-[11px] text-slate-500 font-medium">
            Smart money tracker • Insiders & flows
          </p>
        </div>

        {/* Circular manual Refresh button with minimum 44px tap target */}
        <div className="flex items-center gap-2">
          {lastUpdated && (
            <span className="hidden xs:inline text-[11px] text-slate-400 mono">
              {new Date(lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            aria-label="Refresh Market Feeds"
            title="Refresh Market Feeds"
            className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-full border border-slate-200 bg-white flex items-center justify-center text-slate-600 hover:text-sky-600 hover:border-sky-300 hover:bg-sky-50 active:scale-95 transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-400/40"
          >
            <RotateCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-sky-500' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
}
