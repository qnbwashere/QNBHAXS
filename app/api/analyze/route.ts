import { NextRequest, NextResponse } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';
import { SBC, AIAnalysis } from '@/lib/types';

export const runtime = 'nodejs';

const client = new Anthropic();

function buildSBCContext(sbcs: SBC[]): string {
  return sbcs
    .map(
      (s) =>
        `ID: ${s.id} | Name: "${s.name}" | Category: ${s.category} | ` +
        `Cost: ${s.estimatedCost.toLocaleString()} coins | ` +
        `Reward Value: ${s.totalRewardValue.toLocaleString()} coins | ` +
        `Ratio: ${s.costBenefitRatio.toFixed(2)}x | ` +
        `Repeatable: ${s.repeatable} | Difficulty: ${s.difficulty} | ` +
        `Expires: ${s.endDate ?? 'No expiry'} | ` +
        `Rewards: ${s.rewards.map((r) => `${r.amount}x ${r.name}`).join(', ')}`
    )
    .join('\n');
}

export async function POST(request: NextRequest) {
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json({ error: 'AI analysis unavailable — ANTHROPIC_API_KEY not set.' }, { status: 503 });
  }

  let sbcs: SBC[];
  try {
    const body = await request.json();
    sbcs = body.sbcs;
    if (!Array.isArray(sbcs) || sbcs.length === 0) throw new Error('No SBCs provided');
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
  }

  const prompt = `You are an expert FC26 (EA Sports FC 26) Ultimate Team economist and SBC analyst.
Analyze the following Squad Building Challenges and rank the TOP 5 by cost-benefit value.

Consider these factors:
1. Coin profit/loss margin (reward value minus completion cost)
2. Repeatable SBCs offer sustained profit — weight them higher
3. Expiry urgency — recommend time-sensitive SBCs before they disappear
4. Difficulty relative to reward (Easy SBCs with good value are ideal)
5. Reliable value: some packs are consistently worth more than their listed estimate

SBC DATA:
${buildSBCContext(sbcs)}

Respond ONLY with valid JSON matching this exact schema (no markdown, no code fences):
{
  "topPicks": [
    {
      "sbcId": "<id from the data>",
      "rank": 1,
      "score": 95,
      "recommendation": "Must Do",
      "reasoning": "2-3 sentence explanation focusing on value and why to do it now"
    }
  ],
  "summary": "2-3 sentence overall market summary for today",
  "marketInsight": "1 sentence tip about current FC26 market conditions",
  "generatedAt": "${new Date().toISOString()}"
}

recommendation must be one of: "Must Do", "Highly Recommended", "Worth It", "Skip"
score is 0-100.
Return exactly 5 picks ranked 1-5.`;

  try {
    const message = await client.messages.create({
      model: 'claude-opus-4-7',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }],
    });

    const raw = (message.content[0] as { type: string; text: string }).text.trim();

    // Strip any accidental markdown fences
    const clean = raw.replace(/^```json?\s*/i, '').replace(/\s*```$/, '');
    const analysis: AIAnalysis = JSON.parse(clean);

    return NextResponse.json(analysis);
  } catch (err) {
    return NextResponse.json({ error: `AI analysis failed: ${String(err)}` }, { status: 500 });
  }
}
