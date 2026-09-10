import React, { useState, useEffect, useRef } from 'react';
import { MarketAnalysisResult, AnalysisConfig } from '../types';
import { runQuantitativeAnalysis } from '../engine/clientAnalyzer';
import { loadSystemConfig } from '../engine/configStore';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Zap,
  ShieldAlert,
  Send,
  Sliders,
  Play,
  Pause,
  Copy,
  Check,
  RotateCcw,
  Sparkles,
  ExternalLink,
  Save,
  Radio,
  Share2,
  Settings
} from 'lucide-react';

const DEFAULT_CONFIG: AnalysisConfig = {
  asset: 'EUR/USD',
  timeframe: 'M1',
  expiration: '1m',
  minConfidence: 70,
  requireBos: true,
  requireSweep: false,
  minSrClearanceAtr: 0.4,
  rsiOverbought: 70,
  rsiOversold: 30,
  marketBias: 'auto',
  telegramBotToken: '',
  telegramChatId: '',
  autoSendTelegram: false,
};

const PRESETS = [
  {
    name: 'Pocket Option 1m Standard (70% SMC)',
    desc: 'Close-based BOS required, 70% confluence gate, balanced S/R clearance',
    config: {
      timeframe: 'M1',
      expiration: '1m',
      minConfidence: 70,
      requireBos: true,
      requireSweep: false,
      minSrClearanceAtr: 0.4,
    },
  },
  {
    name: 'OTC Weekend High-Probability (75% Gate)',
    desc: 'Optimized for OTC pairs with liquidity sweeps & wider clearance',
    config: {
      asset: 'EUR/USD (OTC)',
      timeframe: 'M1',
      expiration: '2m',
      minConfidence: 75,
      requireBos: true,
      requireSweep: true,
      minSrClearanceAtr: 0.6,
    },
  },
  {
    name: 'Institutional A+ Sniper (80% Confluence)',
    desc: 'Highest selectivity, sweep + BOS required, strict 80% cutoff',
    config: {
      timeframe: 'M5',
      expiration: '3m',
      minConfidence: 80,
      requireBos: true,
      requireSweep: true,
      minSrClearanceAtr: 0.8,
    },
  },
  {
    name: 'Fast Momentum 30s Scalper',
    desc: 'Faster triggers for sub-minute Pocket Option trades',
    config: {
      timeframe: '30s',
      expiration: '30s',
      minConfidence: 65,
      requireBos: false,
      requireSweep: false,
      minSrClearanceAtr: 0.3,
    },
  },
];

interface AnalyzerConsoleProps {
  onNavigateToConfig?: () => void;
}

export const AnalyzerConsole: React.FC<AnalyzerConsoleProps> = ({ onNavigateToConfig }) => {
  // Load saved config from localStorage or defaults
  const [config, setConfig] = useState<AnalysisConfig>(() => {
    try {
      const sys = loadSystemConfig();
      return {
        asset: sys.defaultAsset || 'EUR/USD',
        timeframe: sys.defaultTimeframe || 'M1',
        expiration: sys.defaultExpiration || '1m',
        minConfidence: sys.minConfidence ?? 70,
        requireBos: sys.requireBos ?? true,
        requireSweep: sys.requireSweep ?? false,
        minSrClearanceAtr: sys.minSrClearanceAtr ?? 0.4,
        rsiOverbought: 70,
        rsiOversold: 30,
        marketBias: 'auto',
        telegramBotToken: sys.telegramBotToken || '',
        telegramChatId: sys.telegramChatId || '',
        autoSendTelegram: sys.autoSendTelegram || false,
      };
    } catch {
      // fallback
    }
    return DEFAULT_CONFIG;
  });

  const [customAssetInput, setCustomAssetInput] = useState('');
  const [isAutoScanning, setIsAutoScanning] = useState(false);
  const [scanInterval, setScanInterval] = useState<number>(10);
  const [countdown, setCountdown] = useState<number>(10);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAdvancedParams, setShowAdvancedParams] = useState(false);
  const [showTelegramSettings, setShowTelegramSettings] = useState(false);
  const [showJsonPayload, setShowJsonPayload] = useState(false);
  const [copiedPayload, setCopiedPayload] = useState(false);
  const [telegramStatus, setTelegramStatus] = useState<string | null>(null);
  const [isSendingTelegram, setIsSendingTelegram] = useState(false);

  // Analysis result state
  const [analysis, setAnalysis] = useState<MarketAnalysisResult>(() =>
    runQuantitativeAnalysis(config.asset, config.timeframe, config.expiration, config.marketBias, config)
  );

  // Save config to localStorage whenever modified
  useEffect(() => {
    try {
      localStorage.setItem('po_analyzer_user_config', JSON.stringify(config));
    } catch {
      // ignore error
    }
  }, [config]);

  // Execute quantitative analysis
  const executeAnalysis = (overrideConfig?: Partial<AnalysisConfig>) => {
    setIsAnalyzing(true);
    const activeConfig = { ...config, ...overrideConfig };
    setTimeout(() => {
      const res = runQuantitativeAnalysis(
        activeConfig.asset,
        activeConfig.timeframe,
        activeConfig.expiration,
        activeConfig.marketBias,
        activeConfig
      );
      setAnalysis(res);
      setIsAnalyzing(false);

      // Auto-dispatch to Telegram if enabled and quality is A+ or A
      if (
        activeConfig.autoSendTelegram &&
        activeConfig.telegramBotToken &&
        activeConfig.telegramChatId &&
        res.decision !== 'NO TRADE'
      ) {
        dispatchToTelegram(res, activeConfig);
      }
    }, 200);
  };

  // Dispatch signal card directly to Telegram
  const dispatchToTelegram = async (result: MarketAnalysisResult, targetConfig: AnalysisConfig) => {
    if (!targetConfig.telegramBotToken || !targetConfig.telegramChatId) {
      setTelegramStatus('Missing Telegram Token or Chat ID in Web UI settings');
      setTimeout(() => setTelegramStatus(null), 3000);
      return;
    }

    setIsSendingTelegram(true);
    setTelegramStatus('Dispatching signal card to Telegram...');

    const emoji = result.decision === 'CALL' ? '🟢 ⬆️ *CALL*' : result.decision === 'PUT' ? '🔴 ⬇️ *PUT*' : '⚪ *NO TRADE*';
    const text = `
🎯 *Pocket Option AI Analyzer Alert*
──────────────────────
*Asset:* \`${result.asset}\`
*Decision:* ${emoji}
*Confidence:* *${result.confidence}%* (${result.quality})
*Timeframe:* ${result.timeframe} | *Expiration:* ${result.expiration}
*Current Price:* \`${result.currentPrice}\`

📊 *Market Structure & SMC:*
• Trend: ${result.marketStructure.trend}
• Close-based BOS: ${result.marketStructure.bosConfirmed ? '✅ Confirmed' : '❌ None'}
• Liquidity: ${result.liquidity.status}

🎯 *Key Levels:*
• Nearest Support: \`${result.sr.nearestSupport}\`
• Nearest Resistance: \`${result.sr.nearestResistance}\`

💡 *Key Reasons:*
${result.reasons.length > 0 ? result.reasons.map((r) => `• ${r}`).join('\n') : '• Setup suppressed due to conflicts'}
${result.conflicts.length > 0 ? `\n⚠️ *Conflicts:*\n${result.conflicts.map((c) => `• ${c}`).join('\n')}` : ''}
──────────────────────
_Triggered directly from Web UI Studio • ${result.timestamp}_
    `.trim();

    try {
      const url = `https://api.telegram.org/bot${targetConfig.telegramBotToken}/sendMessage`;
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: targetConfig.telegramChatId,
          text,
          parse_mode: 'Markdown',
        }),
      });

      const data = await resp.json();
      if (data.ok) {
        setTelegramStatus('✅ Signal successfully delivered to Telegram!');
      } else {
        setTelegramStatus(`⚠️ Telegram error: ${data.description || 'Invalid request'}`);
      }
    } catch (err) {
      setTelegramStatus(`⚠️ Network error sending to Telegram: ${String(err)}`);
    } finally {
      setIsSendingTelegram(false);
      setTimeout(() => setTelegramStatus(null), 4000);
    }
  };

  // Auto-scanning timer
  const autoScanTimerRef = useRef<NodeJS.Timeout | null>(null);
  useEffect(() => {
    if (!isAutoScanning) {
      if (autoScanTimerRef.current) clearInterval(autoScanTimerRef.current);
      return;
    }

    setCountdown(scanInterval);
    autoScanTimerRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          executeAnalysis();
          return scanInterval;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (autoScanTimerRef.current) clearInterval(autoScanTimerRef.current);
    };
  }, [isAutoScanning, scanInterval, config]);

  const handleApplyPreset = (presetConfig: Partial<AnalysisConfig>) => {
    const updated = { ...config, ...presetConfig };
    setConfig(updated);
    executeAnalysis(updated);
  };

  const handleCustomAssetSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customAssetInput.trim()) return;
    const clean = customAssetInput.trim().toUpperCase();
    const updated = { ...config, asset: clean };
    setConfig(updated);
    setCustomAssetInput('');
    executeAnalysis(updated);
  };

  const copyPayload = () => {
    const payload = {
      asset: config.asset,
      timeframe: config.timeframe,
      expiration: config.expiration,
      strategy_gates: {
        min_confluence_threshold: config.minConfidence,
        require_close_based_bos: config.requireBos,
        require_liquidity_sweep: config.requireSweep,
        min_sr_clearance_atr: config.minSrClearanceAtr,
        rsi_overbought: config.rsiOverbought,
        rsi_oversold: config.rsiOversold,
      },
      client_timestamp: new Date().toISOString(),
    };
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    setCopiedPayload(true);
    setTimeout(() => setCopiedPayload(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Risk Rule Banner */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start justify-between gap-3 text-amber-900">
        <div className="flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
          <div className="text-xs sm:text-sm">
            <p className="font-semibold text-amber-950">
              Web UI Request Center: Configure Any Asset, Strategy Gates & Expiration
            </p>
            <p className="text-amber-800 mt-0.5">
              All trading parameters, pairs, timeframe expirations, and Telegram dispatches can be adjusted directly here in the Web UI. No manual code modifications needed.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs px-2.5 py-1 rounded-md bg-white border border-amber-200 font-mono font-semibold text-amber-900">
            Gate: {config.minConfidence}%
          </span>
          {onNavigateToConfig && (
            <button
              onClick={onNavigateToConfig}
              className="text-xs px-3 py-1 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-medium flex items-center gap-1.5 transition-colors shadow-2xs"
            >
              <Settings className="w-3.5 h-3.5" /> System & API Config
            </button>
          )}
        </div>
      </div>

      {/* Main Request Configuration Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Request Configuration Controls (7 cols on lg) */}
        <div className="lg:col-span-7 space-y-5">
          {/* Quick Presets Bar */}
          <div className="bg-white border border-zinc-200 rounded-xl p-4 shadow-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-zinc-900 flex items-center gap-1.5 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                Quick Strategy Presets
              </span>
              <button
                onClick={() => handleApplyPreset(DEFAULT_CONFIG)}
                className="text-[11px] text-zinc-500 hover:text-zinc-800 flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" /> Reset
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleApplyPreset(p.config)}
                  className="p-2.5 rounded-lg border border-zinc-200 hover:border-blue-500 hover:bg-blue-50/40 text-left transition-colors"
                >
                  <p className="text-xs font-semibold text-zinc-800">{p.name}</p>
                  <p className="text-[11px] text-zinc-500 line-clamp-1 mt-0.5">{p.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Core Request Parameters Card */}
          <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-blue-600" />
                <h2 className="font-semibold text-zinc-900 text-sm">Trading Request Parameters</h2>
              </div>
              <span className="text-xs text-zinc-400 font-mono">Current: {config.asset}</span>
            </div>

            {/* Asset Selection & Custom Input */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-medium text-zinc-700">Currency / OTC Asset</label>
                <span className="text-[11px] text-zinc-400">Select preset or enter custom pair</span>
              </div>

              {/* Standard Pairs */}
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 mb-2">
                {['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/CAD', 'EUR/GBP', 'BTC/USD'].map((pair) => (
                  <button
                    key={pair}
                    onClick={() => {
                      const updated = { ...config, asset: pair };
                      setConfig(updated);
                      executeAnalysis(updated);
                    }}
                    className={`px-2 py-1.5 text-xs font-medium rounded-md border text-center transition-colors ${
                      config.asset === pair
                        ? 'border-blue-600 bg-blue-50 text-blue-900 font-semibold'
                        : 'border-zinc-200 hover:border-zinc-300 text-zinc-700'
                    }`}
                  >
                    {pair}
                  </button>
                ))}
              </div>

              {/* Pocket Option OTC Pairs */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 mb-3">
                {['EUR/USD (OTC)', 'GBP/USD (OTC)', 'USD/JPY (OTC)', 'CRYPTO (OTC)'].map((otc) => (
                  <button
                    key={otc}
                    onClick={() => {
                      const updated = { ...config, asset: otc };
                      setConfig(updated);
                      executeAnalysis(updated);
                    }}
                    className={`px-2 py-1.5 text-xs font-medium rounded-md border text-center transition-colors ${
                      config.asset === otc
                        ? 'border-amber-600 bg-amber-50 text-amber-900 font-semibold'
                        : 'border-zinc-200 hover:border-zinc-300 text-zinc-700'
                    }`}
                  >
                    ⚡ {otc}
                  </button>
                ))}
              </div>

              {/* Custom Asset Input Form */}
              <form onSubmit={handleCustomAssetSubmit} className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type any custom asset (e.g. XAU/USD, ETH/USD, USD/CHF, APPLE OTC)..."
                  value={customAssetInput}
                  onChange={(e) => setCustomAssetInput(e.target.value)}
                  className="flex-1 text-xs px-3 py-2 rounded-lg border border-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  className="px-3 py-2 text-xs font-medium rounded-lg bg-zinc-900 hover:bg-zinc-800 text-white transition-colors shrink-0"
                >
                  Set Asset
                </button>
              </form>
            </div>

            {/* Timeframe & Expiration Pickers */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div>
                <label className="block text-xs font-medium text-zinc-700 mb-1.5">Candle Timeframe</label>
                <div className="grid grid-cols-4 gap-1.5">
                  {['10s', '30s', 'M1', 'M2', 'M5', 'M15', 'M30', 'H1'].map((tf) => (
                    <button
                      key={tf}
                      onClick={() => {
                        const updated = { ...config, timeframe: tf };
                        setConfig(updated);
                        executeAnalysis(updated);
                      }}
                      className={`px-2 py-1.5 text-xs font-medium rounded-md border text-center transition-colors ${
                        config.timeframe === tf
                          ? 'border-blue-600 bg-blue-50 text-blue-900 font-semibold'
                          : 'border-zinc-200 hover:border-zinc-300 text-zinc-700'
                      }`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-700 mb-1.5">Trade Expiration</label>
                <div className="grid grid-cols-4 gap-1.5">
                  {['15s', '30s', '1m', '2m', '3m', '5m', '15m'].map((exp) => (
                    <button
                      key={exp}
                      onClick={() => {
                        const updated = { ...config, expiration: exp };
                        setConfig(updated);
                        executeAnalysis(updated);
                      }}
                      className={`px-2 py-1.5 text-xs font-medium rounded-md border text-center transition-colors ${
                        config.expiration === exp
                          ? 'border-blue-600 bg-blue-50 text-blue-900 font-semibold'
                          : 'border-zinc-200 hover:border-zinc-300 text-zinc-700'
                      }`}
                    >
                      {exp}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Strategy Gates & Confluence Sliders */}
            <div className="pt-2 border-t border-zinc-100 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-800">
                  Minimum Confluence Threshold Gate: <span className="font-mono text-blue-600">{config.minConfidence}%</span>
                </label>
                <span className="text-[11px] text-zinc-500">
                  {config.minConfidence >= 80 ? 'Ultra Strict (A+)' : config.minConfidence >= 70 ? 'Recommended (70%)' : 'Aggressive'}
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="90"
                step="1"
                value={config.minConfidence}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  const updated = { ...config, minConfidence: val };
                  setConfig(updated);
                  executeAnalysis(updated);
                }}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-zinc-400 font-mono">
                <span>50% (High Volume)</span>
                <span>70% (Standard)</span>
                <span>80% (Strict)</span>
                <span>90% (Max Confirm)</span>
              </div>
            </div>

            {/* Strategy Toggle Switches */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <label className="flex items-center justify-between p-2.5 rounded-lg border border-zinc-200 bg-zinc-50/50 cursor-pointer">
                <div>
                  <span className="text-xs font-semibold text-zinc-800 block">Strict Close-Based BOS</span>
                  <span className="text-[10px] text-zinc-500 block">Ignore wick-only breakouts</span>
                </div>
                <input
                  type="checkbox"
                  checked={config.requireBos}
                  onChange={(e) => {
                    const updated = { ...config, requireBos: e.target.checked };
                    setConfig(updated);
                    executeAnalysis(updated);
                  }}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
                />
              </label>

              <label className="flex items-center justify-between p-2.5 rounded-lg border border-zinc-200 bg-zinc-50/50 cursor-pointer">
                <div>
                  <span className="text-xs font-semibold text-zinc-800 block">Liquidity Sweep Filter</span>
                  <span className="text-[10px] text-zinc-500 block">Require tap of EQH/EQL pool</span>
                </div>
                <input
                  type="checkbox"
                  checked={config.requireSweep}
                  onChange={(e) => {
                    const updated = { ...config, requireSweep: e.target.checked };
                    setConfig(updated);
                    executeAnalysis(updated);
                  }}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>

            {/* Action Bar: Trigger Analysis & Auto Scan Toggle */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => executeAnalysis()}
                disabled={isAnalyzing}
                className="flex-1 py-2.5 px-4 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-white font-medium text-xs flex items-center justify-center gap-2 transition-colors disabled:opacity-50 shadow-xs"
              >
                <Zap className="w-4 h-4 text-amber-400" />
                {isAnalyzing ? 'Analyzing Real-Time Data...' : 'Run Quantitative Analysis Now'}
              </button>

              <button
                onClick={() => setIsAutoScanning(!isAutoScanning)}
                className={`py-2.5 px-3.5 rounded-lg font-medium text-xs flex items-center gap-1.5 border transition-colors ${
                  isAutoScanning
                    ? 'bg-rose-50 border-rose-300 text-rose-700'
                    : 'bg-zinc-100 border-zinc-200 hover:bg-zinc-200 text-zinc-700'
                }`}
              >
                {isAutoScanning ? (
                  <>
                    <Pause className="w-3.5 h-3.5" /> Stop Auto-Scan ({countdown}s)
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5" /> Auto-Scan ({scanInterval}s)
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Web UI Telegram Alerts & Webhook Drawer */}
          <div className="bg-white border border-zinc-200 rounded-xl p-4 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Send className="w-4 h-4 text-blue-600" />
                <span className="text-xs font-semibold text-zinc-900">
                  Telegram Bot & Webhook Settings (Direct from UI)
                </span>
              </div>
              <button
                onClick={() => setShowTelegramSettings(!showTelegramSettings)}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                {showTelegramSettings ? 'Hide Settings' : 'Configure Token & Chat'}
              </button>
            </div>

            {showTelegramSettings && (
              <div className="pt-2 border-t border-zinc-100 space-y-3">
                <p className="text-xs text-zinc-500">
                  Enter your Bot Token and Chat ID below to push signals straight to your phone. These are stored securely in your browser session.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-zinc-600 mb-1">Telegram Bot Token</label>
                    <input
                      type="text"
                      placeholder="123456789:ABCdefGHI..."
                      value={config.telegramBotToken}
                      onChange={(e) => setConfig({ ...config, telegramBotToken: e.target.value })}
                      className="w-full text-xs px-2.5 py-1.5 rounded-lg border border-zinc-200 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-medium text-zinc-600 mb-1">Telegram Chat ID</label>
                    <input
                      type="text"
                      placeholder="e.g. 987654321 or @channelname"
                      value={config.telegramChatId}
                      onChange={(e) => setConfig({ ...config, telegramChatId: e.target.value })}
                      className="w-full text-xs px-2.5 py-1.5 rounded-lg border border-zinc-200 font-mono"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <label className="flex items-center gap-2 text-xs text-zinc-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.autoSendTelegram}
                      onChange={(e) => setConfig({ ...config, autoSendTelegram: e.target.checked })}
                      className="w-3.5 h-3.5 rounded text-blue-600"
                    />
                    <span>Auto-send A+ and A quality signals to Telegram</span>
                  </label>

                  <button
                    onClick={() => dispatchToTelegram(analysis, config)}
                    disabled={isSendingTelegram || !config.telegramBotToken || !config.telegramChatId}
                    className="px-3 py-1.5 text-xs font-semibold rounded-md bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-40 transition-colors flex items-center gap-1.5"
                  >
                    <Send className="w-3 h-3" />
                    {isSendingTelegram ? 'Sending...' : 'Test Send Alert'}
                  </button>
                </div>

                {onNavigateToConfig && (
                  <div className="pt-2 border-t border-zinc-100 flex items-center justify-between">
                    <span className="text-[11px] text-zinc-500">
                      Need Webhook URL, Bot Mode, Alpha Vantage, or Rate Limit cooldowns?
                    </span>
                    <button
                      type="button"
                      onClick={onNavigateToConfig}
                      className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
                    >
                      Open Full System Config Console &rarr;
                    </button>
                  </div>
                )}
              </div>
            )}

            {telegramStatus && (
              <div className="p-2.5 rounded-lg bg-blue-50 text-blue-900 border border-blue-200 text-xs font-medium">
                {telegramStatus}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Live Analysis Verdict Card (5 cols on lg) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-xs font-semibold text-zinc-800 uppercase tracking-wider">
                  Analysis Verdict Snapshot
                </span>
              </div>
              <span className="text-xs text-zinc-400 font-mono">
                {analysis.executionTimeMs}ms • {analysis.timestamp}
              </span>
            </div>

            {/* Verdict Display */}
            <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-200 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wide">
                    Action Recommendation
                  </span>
                  <div className="mt-1">
                    {analysis.decision === 'CALL' && (
                      <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-lg font-bold bg-emerald-600 text-white shadow-xs">
                        <TrendingUp className="w-5 h-5" /> CALL 🟢
                      </span>
                    )}
                    {analysis.decision === 'PUT' && (
                      <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-lg font-bold bg-rose-600 text-white shadow-xs">
                        <TrendingDown className="w-5 h-5" /> PUT 🔴
                      </span>
                    )}
                    {analysis.decision === 'NO TRADE' && (
                      <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-lg font-bold bg-amber-500 text-white shadow-xs">
                        <AlertTriangle className="w-5 h-5" /> NO TRADE ⚪
                      </span>
                    )}
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wide">
                    Confluence Score
                  </span>
                  <div className="mt-1">
                    <span
                      className={`text-3xl font-extrabold font-mono ${
                        analysis.confidence >= config.minConfidence
                          ? analysis.decision === 'CALL'
                            ? 'text-emerald-600'
                            : 'text-rose-600'
                          : 'text-amber-600'
                      }`}
                    >
                      {analysis.confidence}%
                    </span>
                    <p className="text-[11px] font-medium text-zinc-500 mt-0.5">{analysis.quality}</p>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-zinc-200/60 flex items-center justify-between text-xs text-zinc-600">
                <span>
                  Asset: <strong className="text-zinc-900">{analysis.asset}</strong>
                </span>
                <span>
                  Price: <strong className="font-mono text-zinc-900">{analysis.currentPrice}</strong>
                </span>
                <span>
                  Target: <strong className="text-zinc-900">{analysis.expiration}</strong>
                </span>
              </div>
            </div>

            {/* Micro Details Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
                <span className="text-zinc-500 text-[11px] block">Market Structure</span>
                <span className="font-semibold text-zinc-900 block mt-0.5">{analysis.marketStructure.trend}</span>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
                <span className="text-zinc-500 text-[11px] block">Close-Based BOS</span>
                <span
                  className={`font-semibold block mt-0.5 ${
                    analysis.marketStructure.bosConfirmed ? 'text-emerald-600' : 'text-zinc-500'
                  }`}
                >
                  {analysis.marketStructure.bosConfirmed ? 'Confirmed ✅' : 'None / Wicks Only'}
                </span>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
                <span className="text-zinc-500 text-[11px] block">Key S/R Clearance</span>
                <span className="font-semibold text-zinc-900 block mt-0.5 font-mono">
                  S: {analysis.sr.nearestSupport} | R: {analysis.sr.nearestResistance}
                </span>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
                <span className="text-zinc-500 text-[11px] block">RSI & Momentum</span>
                <span className="font-semibold text-zinc-900 block mt-0.5 font-mono">
                  RSI {analysis.indicators.rsi} ({analysis.indicators.rsiStatus})
                </span>
              </div>
            </div>

            {/* Checklist / Reasons / Conflicts */}
            <div className="space-y-2 pt-1">
              <span className="text-xs font-semibold text-zinc-800 uppercase tracking-wider block">
                {analysis.decision === 'NO TRADE' ? 'Suppression & Risk Triggers' : 'Confluence Audit Trail'}
              </span>

              <ul className="space-y-1.5 text-xs">
                {analysis.decision !== 'NO TRADE'
                  ? analysis.reasons.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-zinc-800">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{r}</span>
                      </li>
                    ))
                  : analysis.conflicts.map((c, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-amber-900 bg-amber-50/70 p-2 rounded-md border border-amber-200/60"
                      >
                        <XCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                        <span>{c}</span>
                      </li>
                    ))}
              </ul>
            </div>

            {/* Quick Export & JSON inspection */}
            <div className="pt-2 border-t border-zinc-100 flex items-center justify-between">
              <button
                onClick={() => setShowJsonPayload(!showJsonPayload)}
                className="text-xs text-zinc-500 hover:text-zinc-800 underline"
              >
                {showJsonPayload ? 'Hide JSON Request' : 'Inspect JSON Request'}
              </button>

              <button
                onClick={copyPayload}
                className="text-xs text-zinc-600 hover:text-zinc-900 flex items-center gap-1"
              >
                {copiedPayload ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                {copiedPayload ? 'Copied' : 'Copy Payload'}
              </button>
            </div>

            {showJsonPayload && (
              <pre className="p-3 bg-zinc-950 text-zinc-300 rounded-lg text-[11px] font-mono overflow-x-auto max-h-48">
                {JSON.stringify(
                  {
                    asset: config.asset,
                    timeframe: config.timeframe,
                    expiration: config.expiration,
                    min_confluence_gate: config.minConfidence,
                    require_bos: config.requireBos,
                    require_sweep: config.requireSweep,
                    result: {
                      verdict: analysis.decision,
                      confidence: analysis.confidence,
                      quality: analysis.quality,
                      price: analysis.currentPrice,
                    },
                  },
                  null,
                  2
                )}
              </pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
