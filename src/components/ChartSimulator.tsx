import React, { useState } from 'react';
import { Layers, Info } from 'lucide-react';

interface SimulatedCandle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  label?: string;
  isSweep?: boolean;
}

export const ChartSimulator: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState('EUR/USD');
  const [chartType, setChartType] = useState<'bullish_bos' | 'liquidity_sweep'>('bullish_bos');

  // Realistic sample candle series
  const candles: SimulatedCandle[] = chartType === 'bullish_bos'
    ? [
        { time: '10:00', open: 1.0820, high: 1.0835, low: 1.0815, close: 1.0830, label: 'L' },
        { time: '10:01', open: 1.0830, high: 1.0850, low: 1.0825, close: 1.0845, label: 'H (1.0850)' },
        { time: '10:02', open: 1.0845, high: 1.0848, low: 1.0828, close: 1.0832 },
        { time: '10:03', open: 1.0832, high: 1.0840, low: 1.0825, close: 1.0838, label: 'HL (1.0825)' },
        { time: '10:04', open: 1.0838, high: 1.0852, low: 1.0835, close: 1.0848 }, // Wick only (no BOS)
        { time: '10:05', open: 1.0848, high: 1.0865, low: 1.0845, close: 1.0862, label: 'BOS CLOSE' }, // Confirmed Close BOS
        { time: '10:06', open: 1.0862, high: 1.0870, low: 1.0858, close: 1.0868, label: 'HH (1.0870)' },
      ]
    : [
        { time: '10:00', open: 1.0855, high: 1.0860, low: 1.0840, close: 1.0845 },
        { time: '10:01', open: 1.0845, high: 1.0858, low: 1.0840, close: 1.0852, label: 'EQH #1 (1.0858)' },
        { time: '10:02', open: 1.0852, high: 1.0854, low: 1.0842, close: 1.0846 },
        { time: '10:03', open: 1.0846, high: 1.0858, low: 1.0844, close: 1.0850, label: 'EQH #2 (1.0858)' },
        { time: '10:04', open: 1.0850, high: 1.0868, low: 1.0848, close: 1.0849, label: 'SWEEP REJECTION', isSweep: true },
        { time: '10:05', open: 1.0849, high: 1.0850, low: 1.0832, close: 1.0835, label: 'PUT ENTRY' },
      ];

  const minPrice = Math.min(...candles.map(c => c.low)) - 0.0005;
  const maxPrice = Math.max(...candles.map(c => c.high)) + 0.0005;
  const priceRange = maxPrice - minPrice;

  const svgHeight = 280;
  const svgWidth = 650;
  const candleSpacing = svgWidth / (candles.length + 1);

  const getY = (price: number) => {
    return svgHeight - ((price - minPrice) / priceRange) * (svgHeight - 40) - 20;
  };

  return (
    <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-100 pb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold text-zinc-900 text-sm">Smart Money Concepts (SMC) Chart Visualizer</h2>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setChartType('bullish_bos')}
            className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
              chartType === 'bullish_bos'
                ? 'bg-blue-50 border-blue-600 text-blue-900 font-semibold'
                : 'border-zinc-200 text-zinc-600 hover:bg-zinc-50'
            }`}
          >
            Close-Based BOS Breakdown
          </button>
          <button
            onClick={() => setChartType('liquidity_sweep')}
            className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
              chartType === 'liquidity_sweep'
                ? 'bg-blue-50 border-blue-600 text-blue-900 font-semibold'
                : 'border-zinc-200 text-zinc-600 hover:bg-zinc-50'
            }`}
          >
            EQH Liquidity Sweep & Rejection
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="w-full overflow-x-auto bg-zinc-950 rounded-xl p-4 border border-zinc-800">
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-64 select-none">
          {/* Grid lines */}
          <line x1="0" y1={svgHeight * 0.25} x2={svgWidth} y2={svgHeight * 0.25} stroke="#27272a" strokeDasharray="3 3" />
          <line x1="0" y1={svgHeight * 0.5} x2={svgWidth} y2={svgHeight * 0.5} stroke="#27272a" strokeDasharray="3 3" />
          <line x1="0" y1={svgHeight * 0.75} x2={svgWidth} y2={svgHeight * 0.75} stroke="#27272a" strokeDasharray="3 3" />

          {/* Reference line for Breakout / EQH level */}
          {chartType === 'bullish_bos' && (
            <g>
              <line x1="60" y1={getY(1.0850)} x2={svgWidth - 20} y2={getY(1.0850)} stroke="#f59e0b" strokeWidth="1.5" strokeDasharray="4 4" />
              <text x={svgWidth - 110} y={getY(1.0850) - 6} fill="#f59e0b" fontSize="10" fontFamily="monospace">
                BOS Level: 1.0850
              </text>
            </g>
          )}

          {chartType === 'liquidity_sweep' && (
            <g>
              <line x1="60" y1={getY(1.0858)} x2={svgWidth - 20} y2={getY(1.0858)} stroke="#ef4444" strokeWidth="1.5" strokeDasharray="4 4" />
              <text x={svgWidth - 140} y={getY(1.0858) - 6} fill="#ef4444" fontSize="10" fontFamily="monospace">
                EQH Buy-Side Pool: 1.0858
              </text>
            </g>
          )}

          {/* Render Candlesticks */}
          {candles.map((c, i) => {
            const x = (i + 1) * candleSpacing;
            const isBullish = c.close >= c.open;
            const candleColor = isBullish ? '#10b981' : '#f43f5e';
            const bodyTop = getY(Math.max(c.open, c.close));
            const bodyBottom = getY(Math.min(c.open, c.close));
            const bodyHeight = Math.max(2, bodyBottom - bodyTop);

            return (
              <g key={i}>
                {/* Upper and Lower Wick */}
                <line
                  x1={x}
                  y1={getY(c.high)}
                  x2={x}
                  y2={getY(c.low)}
                  stroke={candleColor}
                  strokeWidth="1.5"
                />
                {/* Real Body */}
                <rect
                  x={x - 10}
                  y={bodyTop}
                  width="20"
                  height={bodyHeight}
                  fill={c.isSweep ? '#f59e0b' : candleColor}
                  stroke={c.isSweep ? '#fbbf24' : candleColor}
                  rx="1"
                />
                {/* Label marker */}
                {c.label && (
                  <text
                    x={x}
                    y={isBullish ? bodyBottom + 16 : bodyTop - 10}
                    textAnchor="middle"
                    fill={c.isSweep ? '#fbbf24' : '#e4e4e7'}
                    fontSize="9"
                    fontWeight="600"
                    fontFamily="monospace"
                  >
                    {c.label}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-3 text-xs text-zinc-600 flex items-start gap-2">
        <Info className="w-4 h-4 text-zinc-400 mt-0.5 shrink-0" />
        <p>
          <span className="font-semibold text-zinc-900">Quantitative Rule in Code:</span> At candle 10:04, price only pierced 1.0850 with an upper wick (high 1.0852) but closed at 1.0848. The bot <span className="font-semibold text-rose-600">refused to trigger BOS</span>. Only at 10:05 when candle body closed above 1.0850 + ATR buffer was BOS confirmed.
        </p>
      </div>
    </div>
  );
};
