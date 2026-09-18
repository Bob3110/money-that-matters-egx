import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import DetailDrawer from './components/DetailDrawer';

import MoneyMatchView from './views/MoneyMatchView';
import NewsView from './views/NewsView';
import InsidersView from './views/InsidersView';
import InstitutionalView from './views/InstitutionalView';
import MacroView from './views/MacroView';
import WatchlistView from './views/WatchlistView';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('match');
  const [scores, setScores] = useState([]);
  const [news, setNews] = useState([]);
  const [insiders, setInsiders] = useState([]);
  const [institutional, setInstitutional] = useState([]);
  const [macro, setMacro] = useState([]);
  const [feedStatuses, setFeedStatuses] = useState({});
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [selectedTicker, setSelectedTicker] = useState(null);
  const [tickerDetail, setTickerDetail] = useState(null);

  // LocalStorage for Watchlist
  const [watchlist, setWatchlist] = useState(() => {
    try {
      const saved = localStorage.getItem('egx_watchlist');
      return saved ? JSON.parse(saved) : ['COMI.CA', 'FWRY.CA', 'TMGH.CA'];
    } catch {
      return ['COMI.CA', 'FWRY.CA', 'TMGH.CA'];
    }
  });

  const toggleWatchlist = (ticker) => {
    setWatchlist((prev) => {
      const next = prev.includes(ticker)
        ? prev.filter((t) => t !== ticker)
        : [...prev, ticker];
      localStorage.setItem('egx_watchlist', JSON.stringify(next));
      return next;
    });
  };

  const loadAllData = async () => {
    try {
      const [scoresRes, newsRes, insidersRes, instRes, macroRes, statusRes] = await Promise.all([
        fetch(`${API_BASE}/money-match`).then((r) => r.json()),
        fetch(`${API_BASE}/news`).then((r) => r.json()),
        fetch(`${API_BASE}/insiders`).then((r) => r.json()),
        fetch(`${API_BASE}/institutional`).then((r) => r.json()),
        fetch(`${API_BASE}/macro`).then((r) => r.json()),
        fetch(`${API_BASE}/feed-status`).then((r) => r.json()),
      ]);

      setScores(scoresRes.data || []);
      setNews(newsRes.data || []);
      setInsiders(insidersRes.data || []);
      setInstitutional(instRes.data || []);
      setMacro(macroRes.data || []);
      setFeedStatuses(statusRes || {});
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    try {
      await fetch(`${API_BASE}/refresh`, { method: 'POST' });
      // Reload after slight delay to allow scrapers to process
      setTimeout(() => {
        loadAllData();
      }, 2000);
    } catch (e) {
      console.error('Refresh trigger error:', e);
      setIsRefreshing(false);
    }
  };

  const handleSelectTicker = async (item) => {
    setSelectedTicker(item);
    try {
      const res = await fetch(`${API_BASE}/money-match/${item.ticker}`).then((r) => r.json());
      setTickerDetail(res);
    } catch (e) {
      console.error('Detail fetch error:', e);
      setTickerDetail(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header
        onRefresh={handleManualRefresh}
        isRefreshing={isRefreshing}
        lastUpdated={lastUpdated}
      />

      <main className="flex-1 max-w-xl w-full mx-auto px-4 py-4 sm:px-6">
        {activeTab === 'match' && (
          <MoneyMatchView
            scores={scores}
            loading={loading}
            onSelectTicker={handleSelectTicker}
            onToggleWatchlist={toggleWatchlist}
            watchlist={watchlist}
          />
        )}

        {activeTab === 'news' && (
          <NewsView
            news={news}
            status={feedStatuses.news}
            loading={loading}
          />
        )}

        {activeTab === 'insiders' && (
          <InsidersView
            insiders={insiders}
            status={feedStatuses.insiders}
            loading={loading}
          />
        )}

        {activeTab === 'holders' && (
          <InstitutionalView
            institutional={institutional}
            status={feedStatuses.institutional}
            loading={loading}
          />
        )}

        {activeTab === 'macro' && (
          <MacroView
            macro={macro}
            status={feedStatuses.macro}
            loading={loading}
          />
        )}

        {activeTab === 'watchlist' && (
          <WatchlistView
            scores={scores}
            watchlist={watchlist}
            onSelectTicker={handleSelectTicker}
            onToggleWatchlist={toggleWatchlist}
          />
        )}
      </main>

      <Footer />

      <Navigation activeTab={activeTab} onSelectTab={setActiveTab} />

      {selectedTicker && (
        <DetailDrawer
          tickerData={selectedTicker}
          detailData={tickerDetail}
          onClose={() => {
            setSelectedTicker(null);
            setTickerDetail(null);
          }}
          onToggleWatchlist={toggleWatchlist}
          isWatchlisted={watchlist.includes(selectedTicker.ticker)}
        />
      )}
    </div>
  );
}
