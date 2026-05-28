'use client';

export default function Header() {
  return (
    <header className="border-b border-fc-border bg-fc-card/60 backdrop-blur-sm sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-fc-green to-fc-accent flex items-center justify-center text-xl font-black text-white shadow-lg shadow-fc-green/20">
            S
          </div>
          <div>
            <h1 className="text-xl font-bold text-white leading-none">SBC Optimizer</h1>
            <p className="text-xs text-gray-400 mt-0.5">FC 26 · AI-Powered Value Analysis</p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 text-xs text-gray-500 bg-fc-dark rounded-full px-3 py-1.5 border border-fc-border">
          <span className="w-2 h-2 rounded-full bg-fc-green animate-pulse" />
          Live market data
        </div>
      </div>
    </header>
  );
}
