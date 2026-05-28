import { NextResponse } from 'next/server';
import { fetchSBCs } from '@/lib/futbin';

export const runtime = 'nodejs';
export const revalidate = 300;

export async function GET() {
  try {
    const sbcs = await fetchSBCs();
    return NextResponse.json({ sbcs, source: sbcs[0]?.source ?? 'mock', count: sbcs.length });
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
