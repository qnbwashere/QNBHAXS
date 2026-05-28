'use client';

import { FilterState } from '@/lib/types';
import clsx from 'clsx';

interface Props {
  filters: FilterState;
  onChange: (f: FilterState) => void;
  totalCount: number;
  visibleCount: number;
}

const CATEGORIES = ['all', 'foundation', 'upgrades', 'leagues', 'nations', 'hybrid', 'promo', 'icons'];
const DIFFICULTIES = ['all', 'Easy', 'Medium', 'Hard', 'Expert'];
const SORTS: { value: FilterState['sortBy']; label: string }[] = [
  { value: 'costBenefit', label: 'Best Value' },
  { value: 'cost', label: 'Cheapest' },
  { value: 'reward', label: 'Best Reward' },
  { value: 'expiry', label: 'Expiring Soon' },
];

export default function FilterBar({ filters, onChange, totalCount, visibleCount }: Props) {
  function set(partial: Partial<FilterState>) {
    onChange({ ...filters, ...partial });
  }

  return (
    <div className="space-y-3">
      {/* Category chips */}
      <div className="flex gap-2 flex-wrap">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => set({ category: cat })}
            className={clsx(
              'px-3 py-1 rounded-full text-xs font-medium capitalize transition-all border',
              filters.category === cat
                ? 'bg-fc-green text-fc-dark border-fc-green'
                : 'text-gray-400 border-fc-border hover:border-gray-500 hover:text-white'
            )}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Controls row */}
      <div className="flex flex-wrap gap-3 items-center">
        {/* Sort */}
        <select
          value={filters.sortBy}
          onChange={(e) => set({ sortBy: e.target.value as FilterState['sortBy'] })}
          className="bg-fc-card border border-fc-border text-sm text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-fc-green"
        >
          {SORTS.map((s) => (
            <option key={s.value} value={s.value}>
              Sort: {s.label}
            </option>
          ))}
        </select>

        {/* Difficulty */}
        <select
          value={filters.difficulty}
          onChange={(e) => set({ difficulty: e.target.value })}
          className="bg-fc-card border border-fc-border text-sm text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-fc-green"
        >
          {DIFFICULTIES.map((d) => (
            <option key={d} value={d}>
              Difficulty: {d === 'all' ? 'Any' : d}
            </option>
          ))}
        </select>

        {/* Repeatable toggle */}
        <button
          onClick={() => set({ repeatableOnly: !filters.repeatableOnly })}
          className={clsx(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition-all',
            filters.repeatableOnly
              ? 'bg-fc-green/20 border-fc-green text-fc-green'
              : 'border-fc-border text-gray-400 hover:text-white'
          )}
        >
          <span
            className={clsx(
              'w-4 h-4 rounded border-2 flex items-center justify-center text-xs',
              filters.repeatableOnly ? 'border-fc-green bg-fc-green text-fc-dark' : 'border-gray-500'
            )}
          >
            {filters.repeatableOnly && '✓'}
          </span>
          Repeatable only
        </button>

        <span className="ml-auto text-xs text-gray-500">
          {visibleCount} / {totalCount} SBCs
        </span>
      </div>
    </div>
  );
}
