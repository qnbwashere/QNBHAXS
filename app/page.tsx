'use client';

import { useState, useEffect, useMemo } from 'react';
import Header from '@/components/Header';
import SBCCard from '@/components/SBCCard';
import FilterBar from '@/components/FilterBar';
import { SBC, AIAnalysis, FilterState } from '@/lib/types';
import clsx from 'clsx';

const DEFAULT_FILTERS: FilterState = {
  category: 'all',
  maxCost: 9_999_999,
  repeatableOnly: false,
  difficulty: 'all',
  sortBy: 'costBenefit',
  sortDir: 'desc',
};

function coins(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function Home() {
  const [sbcs, setSbcs] = useState<SBC[]>([]);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [loadingSbcs, setLoadingSbcs] = useState(true);
  const [loadingAI, setLoadingAI] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<string>('');
  const [showOnlyAIPicks, setShowOnlyAIPicks] = useState(false);

  // Fetch SBC data on mount
  useEffect(() => {
    fetch('/api/sbcs')
      .then((r) => r.json())
      .then((d) => {
        setSbcs(d.sbcs ?? []);
        setDataSource(d.source ?? '');
      })
      .catch(() => setSbcs([]))
      .finally(() => setLoadingSbcs(false));
  }, []);

  // Filtered + sorted SBCs
  const filtered = useMemo(() => {
    let list = [...sbcs];

    if (filters.category !== 'all') list = list.filter((s) => s.category === filters.category);
    if (filters.difficulty !== 'all') list = list.filter((s) => s.difficulty === filters.difficulty);
    if (filters.repeatableOnly) list = list.filter((s) => s.repeatable);

    // AI picks filter
    const pickIds = analysis?.topPicks.map((p) => String(p.sbcId)) ?? [];
    if (showOnlyAIPicks && pickIds.length) {
      list = list.filter((s) => pickIds.includes(String(s.id)));
    }

    list.sort((a, b) => {
      const dir = filters.sortDir === 'desc' ? -1 : 1;
      switch (filters.sortBy) {
        case 'costBenefit': return dir * (a.costBenefitRatio - b.costBenefitRatio);
        case 'cost': return dir * (a.estimatedCost - b.estimatedCost);
        case 'reward': return dir * (a.totalRewardValue - b.totalRewardValue);
        case 'expiry': {
          const da = a.endDate ? new Date(a.endDate).getTime() : Infinity;
          const db = b.endDate ? new Date(b.endDate).getTime() : Infinity;
          return dir * (da - db);
        }
      }
    });

    return list;
  }, [sbcs, filters, showOnlyAIPicks, analysis]);

  async function runAIAnalysis() {
    if (sbcs.length === 0) return;
    setLoadingAI(true);
    setAiError(null);
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sbcs }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? 'Analysis failed');
      setAnalysis(data);
    } catch (e) {
      setAiError(String(e));
    } finally {
      setLoadingAI(false);
    }
  }

  const aiPickMap = useMemo(() => {
    const map = new Map<string, AIAnalysis['topPicks'][0]>();
    analysis?.topPicks.forEach((p) => map.set(String(p.sbcId), p));
    return map;
  }, [analysis]);

  const stats = useMemo(() => {
    if (!sbcs.length) return null;
    const profitable = sbcs.filter((s) => s.costBenefitRatio > 1);
    const best = [...sbcs].sort((a, b) => b.costBenefitRatio - a.costBenefitRatio)[0];
    const repeatable = sbcs.filter((s) => s.repeatable);
    return { total: sbcs.length, profitable: profitable.length, best, repeatable: repeatable.length };
  }, [sbcs]);

  return (
    <div className="min-h-screen bg-fc-dark">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">

        {/* Hero / stats bar */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Total SBCs', value: stats.total },
              { label: 'Profitable', value: stats.profitable },
              { label: 'Repeatable', value: stats.repeatable },
              { label: 'Best Ratio', value: `${stats.best?.costBenefitRatio.toFixed(2)}x` },
            ].map((s) => (
              <div key={s.label} className="bg-fc-card border border-fc-border rounded-xl p-4 text-center">
                <p className="text-2xl font-black text-white">{s.value}</p>
                <p className="text-xs text-gray-500 mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* AI Analysis panel */}
        <div className="bg-fc-card border border-fc-border rounded-2xl p-6">
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="flex-1">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span className="text-fc-green">✦</span> AI Optimizer
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                Claude analyzes all SBCs and ranks the top 5 by true cost-benefit value.
                {!analysis && ' Add your ANTHROPIC_API_KEY to Vercel env vars to enable.'}
              </p>
            </div>
            <div className="flex gap-3 flex-wrap">
              {analysis && (
                <button
                  onClick={() => setShowOnlyAIPicks((v) => !v)}
                  className={clsx(
                    'px-4 py-2 rounded-xl text-sm font-medium border transition-all',
                    showOnlyAIPicks
                      ? 'bg-fc-green/20 border-fc-green text-fc-green'
                      : 'border-fc-border text-gray-400 hover:text-white'
                  )}
                >
                  {showOnlyAIPicks ? 'Show All' : 'Show AI Picks'}
                </button>
              )}
              <button
                onClick={runAIAnalysis}
                disabled={loadingAI || loadingSbcs}
                className={clsx(
                  'px-5 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2',
                  loadingAI
                    ? 'bg-fc-border text-gray-500 cursor-not-allowed'
                    : 'bg-fc-green text-fc-dark hover:bg-emerald-400 shadow-lg shadow-fc-green/20'
                )}
              >
                {loadingAI && (
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
                {loadingAI ? 'Analyzing…' : analysis ? 'Re-analyze' : 'Analyze with AI'}
              </button>
            </div>
          </div>

          {aiError && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-sm text-red-400">
              {aiError}
            </div>
          )}

          {analysis && (
            <div className="mt-5 grid sm:grid-cols-2 gap-4">
              <div className="bg-fc-dark rounded-xl p-4 border border-fc-border">
                <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wide">Market Summary</p>
                <p className="text-sm text-gray-300 leading-relaxed">{analysis.summary}</p>
              </div>
              <div className="bg-fc-dark rounded-xl p-4 border border-fc-border">
                <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wide">Tip of the Day</p>
                <p className="text-sm text-gray-300 leading-relaxed">{analysis.marketInsight}</p>
              </div>
            </div>
          )}
        </div>

        {/* Data source note */}
        {dataSource && (
          <p className="text-xs text-gray-600 text-right -mt-4">
            Data source: {dataSource === 'mock' ? 'Sample data (FUTBIN unavailable)' : 'FUTBIN FC26 API'}
          </p>
        )}

        {/* Filters */}
        <FilterBar
          filters={filters}
          onChange={setFilters}
          totalCount={sbcs.length}
          visibleCount={filtered.length}
        />

        {/* SBC Grid */}
        {loadingSbcs ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-64 rounded-2xl bg-fc-card border border-fc-border animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-gray-500">
            <p className="text-4xl mb-3">⚽</p>
            <p>No SBCs match your filters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((sbc) => {
              const pick = aiPickMap.get(String(sbc.id));
              return (
                <SBCCard
                  key={sbc.id}
                  sbc={sbc}
                  aiPick={pick}
                  rank={pick?.rank}
                />
              );
            })}
          </div>
        )}

        {/* Footer */}
        <footer className="border-t border-fc-border pt-6 text-center text-xs text-gray-600 pb-8">
          <p>FC 26 SBC Optimizer · Coin values are estimates based on current market rates</p>
          <p className="mt-1">Not affiliated with EA Sports · For entertainment purposes</p>
        </footer>
      </main>
    </div>
  );
}
