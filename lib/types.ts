export interface SBCReward {
  type: string;
  name: string;
  amount: number;
  estimatedValue: number;
}

export interface SBCRequirement {
  minRating?: number;
  chemistry?: number;
  squadSize?: number;
  sameLeague?: boolean;
  sameNation?: boolean;
  sameClub?: boolean;
  uniqueNations?: number;
  uniqueLeagues?: number;
  rareCards?: number;
  bronzeCards?: number;
  silverCards?: number;
  goldCards?: number;
  description?: string;
}

export interface SBC {
  id: string | number;
  name: string;
  description: string;
  category: string;
  imageUrl?: string;
  rewards: SBCReward[];
  requirements: SBCRequirement[];
  estimatedCost: number;
  totalRewardValue: number;
  costBenefitRatio: number;
  repeatable: boolean;
  startDate?: string;
  endDate?: string;
  difficulty: 'Easy' | 'Medium' | 'Hard' | 'Expert';
  source: 'futbin' | 'mock';
}

export interface AIAnalysis {
  topPicks: Array<{
    sbcId: string | number;
    rank: number;
    score: number;
    reasoning: string;
    recommendation: 'Must Do' | 'Highly Recommended' | 'Worth It' | 'Skip';
  }>;
  summary: string;
  marketInsight: string;
  generatedAt: string;
}

export interface FilterState {
  category: string;
  maxCost: number;
  repeatableOnly: boolean;
  difficulty: string;
  sortBy: 'costBenefit' | 'cost' | 'reward' | 'expiry';
  sortDir: 'asc' | 'desc';
}
