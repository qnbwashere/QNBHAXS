import { SBC, SBCReward, SBCRequirement } from './types';
import { MOCK_SBCS } from './mockData';

const FUTBIN_BASE = 'https://www.futbin.com/api/26';

// Map FUTBIN pack type IDs to names and estimated coin values
const PACK_VALUES: Record<string, { name: string; value: number }> = {
  small_gold: { name: 'Small Gold Pack', value: 1500 },
  gold: { name: 'Gold Pack', value: 2500 },
  rare_gold: { name: 'Rare Gold Pack', value: 3200 },
  premium_gold: { name: 'Premium Gold Pack', value: 5500 },
  prime_electrum_players: { name: 'Prime Electrum Players Pack', value: 18000 },
  rare_players: { name: 'Rare Players Pack', value: 20000 },
  mega: { name: 'Mega Pack', value: 28000 },
  prime_gold_players: { name: 'Prime Gold Players Pack', value: 65000 },
  totw: { name: 'TOTW Pack', value: 55000 },
  silver: { name: 'Silver Pack', value: 600 },
};

function parseDifficulty(cost: number): SBC['difficulty'] {
  if (cost < 5000) return 'Easy';
  if (cost < 20000) return 'Medium';
  if (cost < 80000) return 'Hard';
  return 'Expert';
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeFutbinSBC(raw: any): SBC {
  const rewardValue = raw.reward_value ?? raw.rewardValue ?? 3000;
  const cost = raw.cost ?? raw.estimated_cost ?? 5000;

  const rewards: SBCReward[] = (raw.rewards ?? []).map((r: any) => ({
    type: r.type ?? 'pack',
    name: r.name ?? r.label ?? 'Unknown Pack',
    amount: r.amount ?? r.count ?? 1,
    estimatedValue: r.value ?? rewardValue,
  }));

  if (rewards.length === 0) {
    rewards.push({ type: 'pack', name: 'Mystery Pack', amount: 1, estimatedValue: rewardValue });
  }

  const requirements: SBCRequirement[] = (raw.challenges ?? raw.requirements ?? []).map(
    (c: any) => ({
      minRating: c.min_rating ?? c.minRating,
      chemistry: c.chemistry ?? c.chem,
      squadSize: c.squad_size ?? 11,
      description: c.description ?? c.name ?? '',
    })
  );

  const totalRewardValue = rewards.reduce((sum, r) => sum + r.estimatedValue * r.amount, 0);

  return {
    id: raw.id,
    name: raw.name ?? raw.title ?? 'Unknown SBC',
    description: raw.description ?? '',
    category: (raw.category ?? raw.type ?? 'general').toLowerCase(),
    imageUrl: raw.image ?? raw.imageUrl ?? raw.img,
    rewards,
    requirements,
    estimatedCost: cost,
    totalRewardValue,
    costBenefitRatio: totalRewardValue > 0 && cost > 0 ? totalRewardValue / cost : 0,
    repeatable: Boolean(raw.repeatable ?? raw.repeat),
    startDate: raw.start_date ?? raw.startDate,
    endDate: raw.end_date ?? raw.endDate,
    difficulty: parseDifficulty(cost),
    source: 'futbin',
  };
}

export async function fetchSBCs(): Promise<SBC[]> {
  try {
    const response = await fetch(`${FUTBIN_BASE}/sbc`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
        Accept: 'application/json, text/plain, */*',
        Referer: 'https://www.futbin.com/',
      },
      next: { revalidate: 300 },
    });

    if (!response.ok) throw new Error(`FUTBIN responded ${response.status}`);

    const data = await response.json();
    const list = Array.isArray(data) ? data : data.sbcs ?? data.data ?? [];

    if (list.length === 0) throw new Error('Empty response from FUTBIN');

    return list.map(normalizeFutbinSBC);
  } catch {
    // Fall back to curated mock data if FUTBIN is unavailable
    return MOCK_SBCS;
  }
}
