import React, { useState } from 'react';
import { Camera, Upload, Sparkles, CheckCircle, Image as ImageIcon } from 'lucide-react';

export const VisionSimulator: React.FC = () => {
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);
  const [visionResult, setVisionResult] = useState<{
    trend: string;
    pattern: string;
    keyLevels: string;
    verdict: string;
    confidence: string;
    advice: string;
  } | null>(null);

  const presets = [
    {
      id: 'eurusd_m1',
      title: 'EUR/USD M1 Pocket Option Chart',
      desc: 'Clear hammer rejection off institutional support with high lower wick',
      trend: 'Bullish Reversal',
      pattern: 'Long Lower Wick Pin Bar (Hammer) at Demand Zone',
      keyLevels: 'Support at 1.0840 (Held 3x), Resistance at 1.0890',
      verdict: 'CALL 🟢',
      confidence: '82%',
      advice: 'Target 1m to 2m expiration. Clearance to nearest resistance is open.',
    },
    {
      id: 'gbpusd_m5',
      title: 'GBP/USD M5 Structure Break',
      desc: 'Bearish engulfing candle breaking below previous swing low',
      trend: 'Strong Bearish Trend',
      pattern: 'Bearish Engulfing + Close-based BOS',
      keyLevels: 'Resistance at 1.2960, Next Support at 1.2890',
      verdict: 'PUT 🔴',
      confidence: '85%',
      advice: 'Target 3m to 5m expiration. Wait for slight pullback retest if spread allows.',
    },
    {
      id: 'otc_chop',
      title: 'USD/CHF Ranging Consolidation',
      desc: 'Doji candles compressing between tight EMA bands',
      trend: 'Sideways / Dead Volume',
      pattern: 'Multiple Dojis / Spinning Tops inside compressed range',
      keyLevels: 'Range High 0.8845, Range Low 0.8835',
      verdict: 'NO TRADE ⚪',
      confidence: '42%',
      advice: 'High risk of fakeout or expiration tie. Conserve capital.',
    },
  ];

  const handleSelectPreset = (preset: typeof presets[0]) => {
    setSelectedPreset(preset.id);
    setAnalyzing(true);
    setVisionResult(null);

    setTimeout(() => {
      setVisionResult({
        trend: preset.trend,
        pattern: preset.pattern,
        keyLevels: preset.keyLevels,
        verdict: preset.verdict,
        confidence: preset.confidence,
        advice: preset.advice,
      });
      setAnalyzing(false);
    }, 400);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedPreset('custom');
      setAnalyzing(true);
      setVisionResult(null);

      setTimeout(() => {
        setVisionResult({
          trend: 'Bullish Momentum Expansion',
          pattern: 'Bullish Engulfing Candle with Volume Confirmation',
          keyLevels: 'Dynamic support along EMA 21, resistance cleared',
          verdict: 'CALL 🟢',
          confidence: '78%',
          advice: 'Clean structure identified from uploaded chart. Target 2m expiration.',
        });
        setAnalyzing(false);
      }, 500);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex items-center gap-2">
          <Camera className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold text-zinc-900 text-sm">Vision AI Chart Screenshot Analyzer (/screenshot)</h2>
        </div>
        <p className="text-xs text-zinc-600">
          In Telegram, users can send or paste any chart screenshot from Pocket Option. The bot utilizes Gemini Vision AI to perform structural candlestick, support/resistance, and pattern recognition.
        </p>

        {/* Upload Zone & Presets */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {presets.map((p) => (
            <button
              key={p.id}
              onClick={() => handleSelectPreset(p)}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                selectedPreset === p.id
                  ? 'border-blue-600 bg-blue-50/50 shadow-xs ring-1 ring-blue-600'
                  : 'border-zinc-200 hover:border-zinc-300 bg-zinc-50/50'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-semibold text-xs text-zinc-900">{p.title}</span>
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              </div>
              <p className="text-xs text-zinc-500 line-clamp-2">{p.desc}</p>
            </button>
          ))}
        </div>

        {/* Drag & Drop File Input */}
        <label className="block border-2 border-dashed border-zinc-200 hover:border-blue-500 rounded-xl p-6 text-center cursor-pointer transition-colors bg-zinc-50/30">
          <Upload className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
          <span className="text-xs font-medium text-zinc-700 block">
            Drop your Pocket Option screenshot here, or click to browse
          </span>
          <span className="text-[11px] text-zinc-400 block mt-0.5">Supports PNG, JPG, WebP</span>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* Vision Results Card */}
      {analyzing && (
        <div className="bg-white border border-zinc-200 rounded-xl p-8 text-center shadow-xs">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm font-medium text-zinc-800">Processing Chart Geometry with Gemini Vision AI...</p>
          <p className="text-xs text-zinc-500 mt-1">Detecting swing pivots, wick ratios, and horizontal price zones</p>
        </div>
      )}

      {visionResult && !analyzing && (
        <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <span className="text-xs font-semibold text-zinc-700 uppercase tracking-wider">
              Vision AI Structural Breakdown
            </span>
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
              Confidence: {visionResult.confidence}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-zinc-50 border border-zinc-100">
              <span className="text-zinc-500 block font-medium">Market Trend & Structure</span>
              <span className="text-zinc-900 font-semibold block mt-1">{visionResult.trend}</span>
            </div>
            <div className="p-3 rounded-lg bg-zinc-50 border border-zinc-100">
              <span className="text-zinc-500 block font-medium">Identified Candlestick Pattern</span>
              <span className="text-zinc-900 font-semibold block mt-1">{visionResult.pattern}</span>
            </div>
            <div className="p-3 rounded-lg bg-zinc-50 border border-zinc-100 sm:col-span-2">
              <span className="text-zinc-500 block font-medium">Key Price Levels & Clearance</span>
              <span className="text-zinc-900 font-semibold block mt-1">{visionResult.keyLevels}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-200/80 flex items-center justify-between">
            <div>
              <span className="text-xs text-zinc-500 block">Recommended Action</span>
              <span className="text-lg font-bold text-zinc-900 mt-0.5 block">{visionResult.verdict}</span>
            </div>
            <p className="text-xs text-zinc-600 max-w-sm text-right">{visionResult.advice}</p>
          </div>
        </div>
      )}
    </div>
  );
};
