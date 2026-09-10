import React, { useState } from 'react';
import { DemoTrade } from '../types';
import { BookOpen, PlusCircle, CheckCircle, XCircle, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

export const TradeJournal: React.FC = () => {
  const [trades, setTrades] = useState<DemoTrade[]>([
    {
      id: 'trade-1',
      asset: 'EUR/USD',
      direction: 'CALL',
      entryPrice: 1.0845,
      stake: 10,
      expiration: '1m',
      outcome: 'WIN',
      pnl: 8.5,
      timestamp: '10:15 AM',
    },
    {
      id: 'trade-2',
      asset: 'GBP/USD',
      direction: 'PUT',
      entryPrice: 1.2940,
      stake: 10,
      expiration: '2m',
      outcome: 'WIN',
      pnl: 8.5,
      timestamp: '10:28 AM',
    },
    {
      id: 'trade-3',
      asset: 'USD/JPY',
      direction: 'CALL',
      entryPrice: 154.10,
      stake: 10,
      expiration: '1m',
      outcome: 'LOSS',
      pnl: -10.0,
      timestamp: '10:45 AM',
    },
    {
      id: 'trade-4',
      asset: 'AUD/CAD',
      direction: 'PUT',
      entryPrice: 0.8920,
      stake: 10,
      expiration: '3m',
      outcome: 'WIN',
      pnl: 8.5,
      timestamp: '11:02 AM',
    },
  ]);

  const [asset, setAsset] = useState('EUR/USD');
  const [direction, setDirection] = useState<'CALL' | 'PUT'>('CALL');
  const [stake, setStake] = useState(10);
  const [outcome, setOutcome] = useState<'WIN' | 'LOSS'>('WIN');

  const totalTrades = trades.length;
  const wins = trades.filter((t) => t.outcome === 'WIN').length;
  const losses = trades.filter((t) => t.outcome === 'LOSS').length;
  const winRate = totalTrades > 0 ? Math.round((wins / totalTrades) * 100) : 0;
  const netPnl = trades.reduce((acc, t) => acc + (t.pnl || 0), 0);

  const handleAddTrade = (e: React.FormEvent) => {
    e.preventDefault();
    const payoutRate = 0.85; // Standard 85% broker payout
    const pnl = outcome === 'WIN' ? stake * payoutRate : -stake;

    const newTrade: DemoTrade = {
      id: `trade-${Date.now()}`,
      asset,
      direction,
      entryPrice: 1.0850,
      stake,
      expiration: '1m',
      outcome,
      pnl: Number(pnl.toFixed(2)),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setTrades([newTrade, ...trades]);
  };

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-zinc-200 rounded-xl p-4 shadow-xs">
          <span className="text-xs text-zinc-500 font-medium">Win Rate</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-zinc-900">{winRate}%</span>
            <span className="text-xs text-zinc-400">({wins}W / {losses}L)</span>
          </div>
        </div>

        <div className="bg-white border border-zinc-200 rounded-xl p-4 shadow-xs">
          <span className="text-xs text-zinc-500 font-medium">Net Demo PnL</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span
              className={`text-2xl font-bold font-mono ${
                netPnl >= 0 ? 'text-emerald-600' : 'text-rose-600'
              }`}
            >
              {netPnl >= 0 ? `+$${netPnl.toFixed(2)}` : `-$${Math.abs(netPnl).toFixed(2)}`}
            </span>
          </div>
        </div>

        <div className="bg-white border border-zinc-200 rounded-xl p-4 shadow-xs">
          <span className="text-xs text-zinc-500 font-medium">Total Logged</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-bold font-mono text-zinc-900">{totalTrades}</span>
            <span className="text-xs text-zinc-400">trades</span>
          </div>
        </div>

        <div className="bg-white border border-zinc-200 rounded-xl p-4 shadow-xs">
          <span className="text-xs text-zinc-500 font-medium">Discipline Score</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-bold font-mono text-blue-600">92%</span>
            <span className="text-xs text-zinc-400">gated compliance</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Log Trade Form */}
        <form onSubmit={handleAddTrade} className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2">
            <PlusCircle className="w-4 h-4 text-blue-600" />
            <h2 className="font-semibold text-zinc-900 text-sm">Log Paper / Demo Trade</h2>
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-600 mb-1">Asset</label>
            <select
              value={asset}
              onChange={(e) => setAsset(e.target.value)}
              className="w-full text-xs p-2 rounded-lg border border-zinc-200 bg-white"
            >
              <option value="EUR/USD">EUR/USD</option>
              <option value="GBP/USD">GBP/USD</option>
              <option value="USD/JPY">USD/JPY</option>
              <option value="AUD/CAD">AUD/CAD</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs font-medium text-zinc-600 mb-1">Direction</label>
              <div className="grid grid-cols-2 gap-1">
                <button
                  type="button"
                  onClick={() => setDirection('CALL')}
                  className={`py-1.5 text-xs font-semibold rounded-md border text-center transition-colors ${
                    direction === 'CALL'
                      ? 'bg-emerald-600 text-white border-emerald-600'
                      : 'border-zinc-200 text-zinc-700'
                  }`}
                >
                  CALL 🟢
                </button>
                <button
                  type="button"
                  onClick={() => setDirection('PUT')}
                  className={`py-1.5 text-xs font-semibold rounded-md border text-center transition-colors ${
                    direction === 'PUT'
                      ? 'bg-rose-600 text-white border-rose-600'
                      : 'border-zinc-200 text-zinc-700'
                  }`}
                >
                  PUT 🔴
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-600 mb-1">Result</label>
              <div className="grid grid-cols-2 gap-1">
                <button
                  type="button"
                  onClick={() => setOutcome('WIN')}
                  className={`py-1.5 text-xs font-semibold rounded-md border text-center transition-colors ${
                    outcome === 'WIN'
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-500'
                      : 'border-zinc-200 text-zinc-700'
                  }`}
                >
                  WIN
                </button>
                <button
                  type="button"
                  onClick={() => setOutcome('LOSS')}
                  className={`py-1.5 text-xs font-semibold rounded-md border text-center transition-colors ${
                    outcome === 'LOSS'
                      ? 'bg-rose-50 text-rose-800 border-rose-500'
                      : 'border-zinc-200 text-zinc-700'
                  }`}
                >
                  LOSS
                </button>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-600 mb-1">Stake Amount ($)</label>
            <input
              type="number"
              min="1"
              max="1000"
              value={stake}
              onChange={(e) => setStake(Number(e.target.value))}
              className="w-full text-xs p-2 rounded-lg border border-zinc-200"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 px-4 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-white font-medium text-xs transition-colors"
          >
            Save to Journal
          </button>
        </form>

        {/* Trade History Table */}
        <div className="lg:col-span-2 bg-white border border-zinc-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3 mb-4">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              <h2 className="font-semibold text-zinc-900 text-sm">Empirical Trading Log</h2>
            </div>
            <span className="text-xs text-zinc-400">{trades.length} entries</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-zinc-100 text-zinc-400 font-medium">
                  <th className="pb-2">Time</th>
                  <th className="pb-2">Asset</th>
                  <th className="pb-2">Direction</th>
                  <th className="pb-2">Stake</th>
                  <th className="pb-2">Result</th>
                  <th className="pb-2 text-right">PnL</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-50">
                {trades.map((t) => (
                  <tr key={t.id} className="hover:bg-zinc-50/50">
                    <td className="py-2.5 text-zinc-500">{t.timestamp}</td>
                    <td className="py-2.5 font-semibold text-zinc-800">{t.asset}</td>
                    <td className="py-2.5">
                      <span
                        className={`inline-flex items-center gap-1 font-semibold px-2 py-0.5 rounded text-[11px] ${
                          t.direction === 'CALL'
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-rose-50 text-rose-700'
                        }`}
                      >
                        {t.direction}
                      </span>
                    </td>
                    <td className="py-2.5 text-zinc-600">${t.stake}</td>
                    <td className="py-2.5">
                      <span
                        className={`inline-flex items-center gap-1 font-semibold text-[11px] ${
                          t.outcome === 'WIN' ? 'text-emerald-600' : 'text-rose-600'
                        }`}
                      >
                        {t.outcome === 'WIN' ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                        {t.outcome}
                      </span>
                    </td>
                    <td
                      className={`py-2.5 text-right font-mono font-semibold ${
                        (t.pnl || 0) >= 0 ? 'text-emerald-600' : 'text-rose-600'
                      }`}
                    >
                      {(t.pnl || 0) >= 0 ? `+$${t.pnl}` : `-$${Math.abs(t.pnl || 0)}`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
