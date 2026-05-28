'use client';

import { SBC, AIAnalysis } from '@/lib/types';
import clsx from 'clsx';

interface Props {
  sbc: SBC;
  aiPick?: AIAnalysis['topPicks'][0];
  rank?: number;
}

const DIFFICULTY_COLORS: Record<string, string> = {
  Easy: 'text-emerald-400 bg-emerald-400/10',
  Medium: 'text-yellow-400 bg-yellow-400/10',
  Hard: 'text-orange-400 bg-orange-400/10',
  Expert: 'text-red-400 bg-red-400/10',
};

const REC_COLORS: Record<string, string> = {
  'Must Do': 'bg-fc-green text-fc-dark',
  'Highly Recommended': 'bg-emerald-500 text-white',
  'Worth It': 'bg-yellow-500 text-fc-dark',
  Skip: 'bg-red-500/20 text-red-400 border border-red-500/30',
};

function coins(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function ratioColor(r: number) {
  if (r >= 2.0) return 'text-fc-green';
  if (r >= 1.3) return 'text-emerald-400';
  if (r >= 1.0) return 'text-yellow-400';
  return 'text-red-400';
}

function daysLeft(dateStr?: string) {
  if (!dateStr) return null;
  const diff = new Date(dateStr).getTime() - Date.now();
  const days = Math.ceil(diff / 86_400_000);
  if (days < 0) return null;
  return days;
}

export default function SBCCard({ sbc, aiPick, rank }: Props) {
  const profit = sbc.totalRewardValue - sbc.estimatedCost;
  const days = daysLeft(sbc.endDate);
  const isUrgent = days !== null && days <= 3;

  return (
    <div
      className={clsx(
        'relative rounded-2xl border bg-fc-card p-5 flex flex-col gap-4 transition-all hover:border-gray-600 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/30',
        aiPick ? 'border-fc-green/40 shadow-md shadow-fc-green/10' : 'border-fc-border',
        isUrgent && 'border-orange-500/40'
      )}
    >
      {/* Rank badge */}
      {rank && (
        <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-fc-green text-fc-dark text-sm font-black flex items-center justify-center shadow-lg">
          #{rank}
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white text-sm leading-snug truncate">{sbc.name}</h3>
          <p className="text-xs text-gray-500 mt-0.5 capitalize">{sbc.category}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={clsx('text-xs font-medium px-2 py-0.5 rounded-full', DIFFICULTY_COLORS[sbc.difficulty])}>
            {sbc.difficulty}
          </span>
          {sbc.repeatable && (
            <span className="text-xs text-fc-green bg-fc-green/10 px-2 py-0.5 rounded-full">Repeatable</span>
          )}
        </div>
      </div>

      {/* Cost / Value row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Cost</p>
          <p className="text-sm font-bold text-white">{coins(sbc.estimatedCost)}</p>
        </div>
        <div className="text-center border-x border-fc-border">
          <p className="text-xs text-gray-500 mb-1">Reward</p>
          <p className="text-sm font-bold text-white">{coins(sbc.totalRewardValue)}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Ratio</p>
          <p className={clsx('text-sm font-bold', ratioColor(sbc.costBenefitRatio))}>
            {sbc.costBenefitRatio.toFixed(2)}x
          </p>
        </div>
      </div>

      {/* Profit bar */}
      <div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-500">Net {profit >= 0 ? 'profit' : 'loss'}</span>
          <span className={profit >= 0 ? 'text-fc-green' : 'text-red-400'}>
            {profit >= 0 ? '+' : ''}{coins(profit)}
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-fc-border overflow-hidden">
          <div
            className={clsx('h-full rounded-full transition-all', profit >= 0 ? 'bg-fc-green' : 'bg-red-500')}
            style={{ width: `${Math.min(100, Math.abs(sbc.costBenefitRatio) * 50)}%` }}
          />
        </div>
      </div>

      {/* Rewards */}
      <div className="flex flex-wrap gap-1.5">
        {sbc.rewards.map((r, i) => (
          <span key={i} className="text-xs bg-fc-dark text-gray-300 px-2 py-0.5 rounded-full border border-fc-border">
            {r.amount > 1 ? `${r.amount}x ` : ''}{r.name}
          </span>
        ))}
      </div>

      {/* Requirements preview */}
      {sbc.requirements[0]?.description && (
        <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">{sbc.requirements[0].description}</p>
      )}

      {/* Expiry */}
      {days !== null && (
        <div className={clsx('flex items-center gap-1.5 text-xs', isUrgent ? 'text-orange-400' : 'text-gray-500')}>
          <span className={clsx('w-1.5 h-1.5 rounded-full', isUrgent ? 'bg-orange-400' : 'bg-gray-600')} />
          {days === 0 ? 'Expires today!' : `${days}d left`}
        </div>
      )}

      {/* AI recommendation */}
      {aiPick && (
        <div className="mt-1 pt-4 border-t border-fc-border">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-gray-400">AI says:</span>
            <span className={clsx('text-xs font-semibold px-2 py-0.5 rounded-full', REC_COLORS[aiPick.recommendation])}>
              {aiPick.recommendation}
            </span>
            <span className="ml-auto text-xs text-gray-500">Score: {aiPick.score}/100</span>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">{aiPick.reasoning}</p>
        </div>
      )}
    </div>
  );
}
