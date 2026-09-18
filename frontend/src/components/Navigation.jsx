import React from 'react';
import { Zap, Newspaper, UserCheck, Building2, Landmark, Star } from 'lucide-react';

export const TABS = [
  { id: 'match', label: 'Match', fullName: 'Money Match (Home)', icon: Zap },
  { id: 'news', label: 'News', fullName: 'EGX Market & Corporate News', icon: Newspaper },
  { id: 'insiders', label: 'Insiders', fullName: 'Corporate Insiders & Treasury', icon: UserCheck },
  { id: 'holders', label: 'Holders', fullName: 'Institutional & Major Holders', icon: Building2 },
  { id: 'macro', label: 'Macro', fullName: 'Macro & Central Bank of Egypt', icon: Landmark },
  { id: 'watchlist', label: 'Saved', fullName: 'Watchlist', icon: Star },
];

export default function Navigation({ activeTab, onSelectTab }) {
  return (
    <nav 
      aria-label="Main Navigation"
      className="fixed bottom-0 left-0 right-0 z-30 bg-white/95 backdrop-blur border-t border-slate-200/80 pb-safe shadow-[0_-4px_12px_rgba(0,0,0,0.03)]"
    >
      <div className="max-w-xl mx-auto flex items-center justify-around px-1 py-1">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`flex-1 flex flex-col items-center justify-center min-h-[48px] min-w-[44px] py-1 px-0.5 rounded-xl transition-colors relative ${
                isActive ? 'text-sky-500 font-semibold' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {/* Exactly ONE accent color: baby blue #38BDF8 / sky-400 */}
              <Icon className={`w-5 h-5 transition-transform ${isActive ? 'scale-110 text-sky-400 stroke-[2.25]' : 'stroke-[1.75]'}`} />
              <span className="text-[10px] mt-0.5 tracking-tight">
                {tab.label}
              </span>
              {isActive && (
                <span className="absolute bottom-1 w-1 h-1 rounded-full bg-sky-400" />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
