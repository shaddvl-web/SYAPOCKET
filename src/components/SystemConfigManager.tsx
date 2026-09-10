import React, { useState, useEffect } from 'react';
import { SystemBotConfig } from '../types';
import {
  loadSystemConfig,
  saveSystemConfig,
  generateEnvFile,
  testTelegramBotToken,
  testTelegramWebhook,
  setTelegramWebhook,
  deleteTelegramWebhook,
  testAlphaVantageKey,
  DEFAULT_SYSTEM_CONFIG,
} from '../engine/configStore';
import {
  Settings,
  Key,
  Bot,
  Globe,
  Database,
  Shield,
  Clock,
  Sliders,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Download,
  RotateCcw,
  Save,
  Send,
  Eye,
  EyeOff,
  Radio,
  ExternalLink,
  Layers,
  Terminal,
  Zap,
  Lock,
  Cpu,
  RefreshCw,
} from 'lucide-react';

export const SystemConfigManager: React.FC = () => {
  const [config, setConfig] = useState<SystemBotConfig>(loadSystemConfig);
  const [showToken, setShowToken] = useState(false);
  const [showAlphaKey, setShowAlphaKey] = useState(false);
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [copiedEnv, setCopiedEnv] = useState(false);
  const [saveNotification, setSaveNotification] = useState<string | null>(null);

  // Testing states
  const [isTestingToken, setIsTestingToken] = useState(false);
  const [tokenTestResult, setTokenTestResult] = useState<{
    success: boolean;
    message: string;
    botDetails?: any;
  } | null>(null);

  const [isTestingWebhook, setIsTestingWebhook] = useState(false);
  const [webhookTestResult, setWebhookTestResult] = useState<{
    success: boolean;
    message: string;
    details?: any;
  } | null>(null);

  const [isTestingAlpha, setIsTestingAlpha] = useState(false);
  const [alphaTestResult, setAlphaTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const [activeSection, setActiveSection] = useState<
    'all' | 'telegram' | 'market' | 'admin' | 'ratelimit' | 'database' | 'env'
  >('all');

  // Handle saving
  const handleSave = () => {
    saveSystemConfig(config);
    setSaveNotification('✅ All system configurations and tokens successfully saved to persistent storage!');
    setTimeout(() => setSaveNotification(null), 4000);
  };

  // Reset to defaults
  const handleReset = () => {
    if (window.confirm('Reset all configuration to factory defaults? This will clear customized tokens.')) {
      setConfig(DEFAULT_SYSTEM_CONFIG);
      saveSystemConfig(DEFAULT_SYSTEM_CONFIG);
      setSaveNotification('Reset to factory default settings.');
      setTimeout(() => setSaveNotification(null), 3000);
    }
  };

  // Test Telegram Bot Token
  const runTestToken = async () => {
    setIsTestingToken(true);
    setTokenTestResult(null);
    const res = await testTelegramBotToken(config.telegramBotToken);
    setTokenTestResult(res);
    setIsTestingToken(false);
  };

  // Test Telegram Webhook Info
  const runTestWebhook = async () => {
    setIsTestingWebhook(true);
    setWebhookTestResult(null);
    const res = await testTelegramWebhook(config.telegramBotToken);
    setWebhookTestResult(res);
    setIsTestingWebhook(false);
  };

  // Register Webhook
  const runSetWebhook = async () => {
    if (!config.webhookUrl) {
      alert('Please enter a Webhook URL first (e.g. https://your-server.com/webhook/telegram)');
      return;
    }
    setIsTestingWebhook(true);
    const res = await setTelegramWebhook(config.telegramBotToken, config.webhookUrl);
    setWebhookTestResult(res);
    setIsTestingWebhook(false);
  };

  // Delete Webhook (switch to Polling)
  const runDeleteWebhook = async () => {
    setIsTestingWebhook(true);
    const res = await deleteTelegramWebhook(config.telegramBotToken);
    setWebhookTestResult(res);
    setIsTestingWebhook(false);
  };

  // Test Alpha Vantage Key
  const runTestAlpha = async () => {
    setIsTestingAlpha(true);
    setAlphaTestResult(null);
    const res = await testAlphaVantageKey(config.alphaVantageApiKey);
    setAlphaTestResult(res);
    setIsTestingAlpha(false);
  };

  // Copy .env
  const copyEnvFile = () => {
    const text = generateEnvFile(config);
    navigator.clipboard.writeText(text);
    setCopiedEnv(true);
    setTimeout(() => setCopiedEnv(false), 2000);
  };

  // Download .env file
  const downloadEnvFile = () => {
    const text = generateEnvFile(config);
    const element = document.createElement('a');
    const file = new Blob([text], { type: 'text/plain;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = '.env';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Admin IDs helper
  const addCurrentChatToAdmin = () => {
    if (!config.telegramChatId) return;
    const current = config.adminIds
      .split(',')
      .map((id) => id.trim())
      .filter(Boolean);
    if (!current.includes(config.telegramChatId.trim())) {
      current.push(config.telegramChatId.trim());
      setConfig({ ...config, adminIds: current.join(',') });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-zinc-900 text-white flex items-center justify-center">
              <Settings className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h1 className="text-base font-bold text-zinc-900">System & API Configuration Console</h1>
              <p className="text-xs text-zinc-500">
                Configure Telegram Bot tokens, bot execution mode, webhooks, database paths, Alpha Vantage API, and rate limit cooldowns.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleReset}
            className="px-3 py-2 text-xs font-medium text-zinc-600 hover:text-zinc-900 bg-zinc-100 hover:bg-zinc-200 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset Defaults
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition-colors flex items-center gap-1.5"
          >
            <Save className="w-3.5 h-3.5" /> Save Configuration
          </button>
        </div>
      </div>

      {/* Save Notification Alert */}
      {saveNotification && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-medium flex items-center gap-2 shadow-2xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{saveNotification}</span>
        </div>
      )}

      {/* Navigation Filter Tabs */}
      <div className="flex items-center gap-1 border-b border-zinc-200 overflow-x-auto pb-1 text-xs">
        {[
          { id: 'all', label: 'All Settings', icon: Layers },
          { id: 'telegram', label: 'Telegram & Webhook', icon: Bot },
          { id: 'market', label: 'APIs & Providers', icon: Key },
          { id: 'ratelimit', label: 'Rate Limits & Cooldown', icon: Clock },
          { id: 'database', label: 'Database Path', icon: Database },
          { id: 'admin', label: 'Admin Access', icon: Shield },
          { id: 'env', label: '.env Synchronizer', icon: Terminal },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSection === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id as any)}
              className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                isActive
                  ? 'bg-zinc-900 text-white'
                  : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* System Status Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3 bg-white border border-zinc-200 rounded-xl shadow-2xs">
          <span className="text-[11px] text-zinc-500 font-medium block">Bot Mode</span>
          <div className="flex items-center gap-1.5 mt-1">
            <span
              className={`w-2 h-2 rounded-full ${
                config.botMode === 'polling' ? 'bg-emerald-500' : 'bg-blue-500'
              }`}
            />
            <span className="text-xs font-bold uppercase font-mono text-zinc-800">
              {config.botMode}
            </span>
          </div>
        </div>

        <div className="p-3 bg-white border border-zinc-200 rounded-xl shadow-2xs">
          <span className="text-[11px] text-zinc-500 font-medium block">Telegram Token</span>
          <span
            className={`text-xs font-bold block mt-1 ${
              config.telegramBotToken ? 'text-emerald-600' : 'text-amber-600'
            }`}
          >
            {config.telegramBotToken ? 'Configured ✅' : 'Missing ⚠️'}
          </span>
        </div>

        <div className="p-3 bg-white border border-zinc-200 rounded-xl shadow-2xs">
          <span className="text-[11px] text-zinc-500 font-medium block">Market Provider</span>
          <span className="text-xs font-bold font-mono text-zinc-800 block mt-1 uppercase">
            {config.defaultMarketProvider}
          </span>
        </div>

        <div className="p-3 bg-white border border-zinc-200 rounded-xl shadow-2xs">
          <span className="text-[11px] text-zinc-500 font-medium block">Alpha Vantage</span>
          <span
            className={`text-xs font-bold block mt-1 ${
              config.alphaVantageApiKey ? 'text-emerald-600' : 'text-zinc-500'
            }`}
          >
            {config.alphaVantageApiKey ? 'API Ready' : 'Unset (Optional)'}
          </span>
        </div>

        <div className="p-3 bg-white border border-zinc-200 rounded-xl shadow-2xs">
          <span className="text-[11px] text-zinc-500 font-medium block">Rate Limit</span>
          <span className="text-xs font-bold font-mono text-zinc-800 block mt-1">
            {config.rateLimitRequestsPerMin} req/min
          </span>
        </div>

        <div className="p-3 bg-white border border-zinc-200 rounded-xl shadow-2xs">
          <span className="text-[11px] text-zinc-500 font-medium block">Analysis Cooldown</span>
          <span className="text-xs font-bold font-mono text-zinc-800 block mt-1">
            {config.analysisCooldownSeconds}s delay
          </span>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 1. Telegram Bot, Mode & Webhook Section */}
      {/* ========================================================================= */}
      {(activeSection === 'all' || activeSection === 'telegram') && (
        <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-5">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-blue-600" />
              <div>
                <h2 className="text-sm font-bold text-zinc-900">Telegram Bot & Webhook Ingress</h2>
                <p className="text-[11px] text-zinc-500">
                  Bot Father token, polling vs. webhook operational mode, and endpoint ingress routing.
                </p>
              </div>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              Mode: {config.botMode}
            </span>
          </div>

          {/* Telegram Bot Token Input & Real-Time Test */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-zinc-800 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-zinc-500" />
                Telegram Bot Token (TELEGRAM_BOT_TOKEN)
              </label>
              <a
                href="https://t.me/BotFather"
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                Get Token from @BotFather <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type={showToken ? 'text' : 'password'}
                  value={config.telegramBotToken}
                  onChange={(e) => setConfig({ ...config, telegramBotToken: e.target.value })}
                  placeholder="e.g. 1234567890:ABCdefGhIjkLmNoPqRsTuVwXyZ..."
                  className="w-full text-xs font-mono px-3 py-2 pr-10 rounded-lg border border-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={() => setShowToken(!showToken)}
                  className="absolute right-2.5 top-2.5 text-zinc-400 hover:text-zinc-600"
                >
                  {showToken ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>

              <button
                type="button"
                onClick={runTestToken}
                disabled={isTestingToken || !config.telegramBotToken}
                className="px-3 py-2 text-xs font-semibold rounded-lg bg-zinc-900 hover:bg-zinc-800 text-white disabled:opacity-40 transition-colors flex items-center gap-1.5 shrink-0"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isTestingToken ? 'animate-spin' : ''}`} />
                {isTestingToken ? 'Testing...' : 'Test Bot Token'}
              </button>
            </div>

            {tokenTestResult && (
              <div
                className={`p-3 rounded-lg text-xs font-medium border flex items-start gap-2 ${
                  tokenTestResult.success
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : 'bg-rose-50 border-rose-200 text-rose-900'
                }`}
              >
                {tokenTestResult.success ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
                )}
                <div>
                  <p className="font-semibold">{tokenTestResult.message}</p>
                  {tokenTestResult.botDetails && (
                    <div className="mt-1 text-[11px] text-emerald-800 flex flex-wrap gap-x-3">
                      <span>Bot ID: {tokenTestResult.botDetails.id}</span>
                      <span>Username: @{tokenTestResult.botDetails.username}</span>
                      <span>Groups: {tokenTestResult.botDetails.can_join_groups ? 'Allowed' : 'Disabled'}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Bot Execution Mode Selector */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div
              onClick={() => setConfig({ ...config, botMode: 'polling' })}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                config.botMode === 'polling'
                  ? 'border-blue-600 bg-blue-50/40 ring-1 ring-blue-500'
                  : 'border-zinc-200 hover:border-zinc-300 bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Radio className={`w-4 h-4 ${config.botMode === 'polling' ? 'text-blue-600' : 'text-zinc-400'}`} />
                  <span className="font-bold text-xs text-zinc-900">Polling Mode (BOT_MODE="polling")</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">
                  Recommended for Dev / VPS
                </span>
              </div>
              <p className="text-xs text-zinc-600 mt-2 leading-relaxed">
                The bot initiates continuous long-polling requests directly to Telegram servers. No public domain, HTTPS SSL certificates, or open port forwarding required.
              </p>
            </div>

            <div
              onClick={() => setConfig({ ...config, botMode: 'webhook' })}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                config.botMode === 'webhook'
                  ? 'border-blue-600 bg-blue-50/40 ring-1 ring-blue-500'
                  : 'border-zinc-200 hover:border-zinc-300 bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Globe className={`w-4 h-4 ${config.botMode === 'webhook' ? 'text-blue-600' : 'text-zinc-400'}`} />
                  <span className="font-bold text-xs text-zinc-900">Webhook Mode (BOT_MODE="webhook")</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold">
                  Production / Cloud Run
                </span>
              </div>
              <p className="text-xs text-zinc-600 mt-2 leading-relaxed">
                Telegram pushes updates instantaneously via HTTP POST requests to your public HTTPS endpoint. Eliminates polling overhead and scales efficiently.
              </p>
            </div>
          </div>

          {/* Webhook URL & Server Ingress Controls */}
          {config.botMode === 'webhook' && (
            <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-200 space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-800 flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-blue-600" />
                  Public Webhook URL (WEBHOOK_URL)
                </label>
                <input
                  type="text"
                  value={config.webhookUrl}
                  onChange={(e) => setConfig({ ...config, webhookUrl: e.target.value })}
                  placeholder="https://your-domain.com/webhook/telegram"
                  className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                />
                <p className="text-[11px] text-zinc-500">
                  Must be a publicly resolvable HTTPS address pointing to the FastAPI webhook router.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={runTestWebhook}
                  disabled={isTestingWebhook || !config.telegramBotToken}
                  className="px-3 py-1.5 text-xs font-medium bg-white hover:bg-zinc-100 border border-zinc-200 rounded-lg text-zinc-700 transition-colors"
                >
                  Check Webhook Status
                </button>
                <button
                  type="button"
                  onClick={runSetWebhook}
                  disabled={isTestingWebhook || !config.telegramBotToken || !config.webhookUrl}
                  className="px-3 py-1.5 text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Register Webhook with Telegram
                </button>
                <button
                  type="button"
                  onClick={runDeleteWebhook}
                  disabled={isTestingWebhook || !config.telegramBotToken}
                  className="px-3 py-1.5 text-xs font-medium bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 rounded-lg transition-colors"
                >
                  Delete Webhook (Back to Polling)
                </button>
              </div>

              {webhookTestResult && (
                <div className="p-3 rounded-lg bg-white border border-zinc-200 text-xs space-y-1 font-mono">
                  <p className="font-semibold text-zinc-900">{webhookTestResult.message}</p>
                  {webhookTestResult.details && (
                    <div className="text-[11px] text-zinc-600 space-y-0.5 pt-1">
                      <p>Pending Updates: {webhookTestResult.details.pending_update_count ?? 0}</p>
                      {webhookTestResult.details.last_error_message && (
                        <p className="text-rose-600">Last Error: {webhookTestResult.details.last_error_message}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Host & Port Configuration */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
            <div>
              <label className="text-xs font-medium text-zinc-700 block mb-1">
                Server Bind Host (HOST)
              </label>
              <input
                type="text"
                value={config.host}
                onChange={(e) => setConfig({ ...config, host: e.target.value })}
                placeholder="0.0.0.0"
                className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-zinc-200"
              />
              <span className="text-[10px] text-zinc-400 mt-1 block">Default 0.0.0.0 for container / docker ingress</span>
            </div>

            <div>
              <label className="text-xs font-medium text-zinc-700 block mb-1">
                Server Bind Port (PORT)
              </label>
              <input
                type="number"
                value={config.port}
                onChange={(e) => setConfig({ ...config, port: Number(e.target.value) })}
                placeholder="3000"
                className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-zinc-200"
              />
              <span className="text-[10px] text-zinc-400 mt-1 block">Standard HTTP listening port</span>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2. Market Providers & Alpha Vantage / APIs Section */}
      {/* ========================================================================= */}
      {(activeSection === 'all' || activeSection === 'market') && (
        <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-5">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div className="flex items-center gap-2">
              <Key className="w-5 h-5 text-amber-600" />
              <div>
                <h2 className="text-sm font-bold text-zinc-900">Market Data Providers & API Keys</h2>
                <p className="text-[11px] text-zinc-500">
                  Configure real-time price feeds, Alpha Vantage institutional forex API, and Twelve Data.
                </p>
              </div>
            </div>
          </div>

          {/* Primary Market Provider Selector */}
          <div>
            <label className="text-xs font-semibold text-zinc-800 block mb-2">
              Default Market Data Provider (DEFAULT_MARKET_PROVIDER)
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                {
                  id: 'binance',
                  name: 'Binance Feed',
                  badge: 'Free / No Key',
                  desc: 'High-frequency millisecond ticks for BTC, ETH, SOL, and crypto OTC.',
                },
                {
                  id: 'alpha_vantage',
                  name: 'Alpha Vantage',
                  badge: 'Forex & Commodities',
                  desc: 'Institutional FX quotes for EUR/USD, GBP/USD, USD/JPY, Gold.',
                },
                {
                  id: 'twelve_data',
                  name: 'Twelve Data',
                  badge: 'Multi-Asset',
                  desc: 'Real-time WebSocket & REST for global currencies and Pocket Option OTC.',
                },
                {
                  id: 'synthetic',
                  name: 'Autonomous SMC',
                  badge: 'Built-in Engine',
                  desc: 'Zero-latency mathematical order flow engine with simulated liquidity.',
                },
              ].map((provider) => {
                const isSelected = config.defaultMarketProvider === provider.id;
                return (
                  <div
                    key={provider.id}
                    onClick={() => setConfig({ ...config, defaultMarketProvider: provider.id as any })}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50/40 ring-1 ring-blue-500'
                        : 'border-zinc-200 hover:border-zinc-300 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-zinc-900">{provider.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-100 text-zinc-600 font-mono">
                        {provider.badge}
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-500 mt-1.5 leading-relaxed">{provider.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Alpha Vantage API Key with Real Test */}
          <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-200 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-xs font-bold text-zinc-900 block">
                  Alpha Vantage API Key (ALPHA_VANTAGE_API_KEY)
                </label>
                <p className="text-[11px] text-zinc-500">
                  Powers accurate real-time Forex exchange rates and historical OHLC candlestick feeds.
                </p>
              </div>
              <a
                href="https://www.alphavantage.co/support/#api-key"
                target="_blank"
                rel="noreferrer"
                className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 shrink-0"
              >
                Claim Free API Key <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type={showAlphaKey ? 'text' : 'password'}
                  value={config.alphaVantageApiKey}
                  onChange={(e) => setConfig({ ...config, alphaVantageApiKey: e.target.value })}
                  placeholder="Enter your Alpha Vantage key (e.g. DEMO or 16-character alphanumeric)..."
                  className="w-full text-xs font-mono px-3 py-2 pr-10 rounded-lg border border-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                />
                <button
                  type="button"
                  onClick={() => setShowAlphaKey(!showAlphaKey)}
                  className="absolute right-2.5 top-2.5 text-zinc-400 hover:text-zinc-600"
                >
                  {showAlphaKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>

              <button
                type="button"
                onClick={runTestAlpha}
                disabled={isTestingAlpha || !config.alphaVantageApiKey}
                className="px-3 py-2 text-xs font-semibold rounded-lg bg-zinc-900 hover:bg-zinc-800 text-white disabled:opacity-40 transition-colors flex items-center gap-1.5 shrink-0"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isTestingAlpha ? 'animate-spin' : ''}`} />
                {isTestingAlpha ? 'Testing...' : 'Test Alpha Vantage Key'}
              </button>
            </div>

            {alphaTestResult && (
              <div
                className={`p-3 rounded-lg text-xs font-medium border flex items-start gap-2 ${
                  alphaTestResult.success
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : 'bg-rose-50 border-rose-200 text-rose-900'
                }`}
              >
                {alphaTestResult.success ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
                )}
                <span>{alphaTestResult.message}</span>
              </div>
            )}
          </div>

          {/* Twelve Data & Gemini AI Vision Keys */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-zinc-800 block mb-1">
                Twelve Data API Key (TWELVE_DATA_API_KEY)
              </label>
              <input
                type="text"
                value={config.twelveDataApiKey}
                onChange={(e) => setConfig({ ...config, twelveDataApiKey: e.target.value })}
                placeholder="Optional Twelve Data key for multi-broker OTC rates..."
                className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-zinc-200"
              />
              <span className="text-[10px] text-zinc-400 mt-1 block">Optional secondary fallback provider</span>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-zinc-800">
                  Gemini API Key (GEMINI_API_KEY)
                </label>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 font-medium">
                  Vision Chart AI
                </span>
              </div>
              <div className="relative">
                <input
                  type={showGeminiKey ? 'text' : 'password'}
                  value={config.geminiApiKey}
                  onChange={(e) => setConfig({ ...config, geminiApiKey: e.target.value })}
                  placeholder="Optional Gemini key for screenshot OCR and SMC pattern vision..."
                  className="w-full text-xs font-mono px-3 py-2 pr-10 rounded-lg border border-zinc-200"
                />
                <button
                  type="button"
                  onClick={() => setShowGeminiKey(!showGeminiKey)}
                  className="absolute right-2.5 top-2.5 text-zinc-400 hover:text-zinc-600"
                >
                  {showGeminiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
              <span className="text-[10px] text-zinc-400 mt-1 block">
                Powers AI Vision chart screenshot analysis tab
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 3. Rate Limiting & Cooldown Section */}
      {/* ========================================================================= */}
      {(activeSection === 'all' || activeSection === 'ratelimit') && (
        <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-5">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-indigo-600" />
              <div>
                <h2 className="text-sm font-bold text-zinc-900">Rate Limiting & Analysis Cooldown</h2>
                <p className="text-[11px] text-zinc-500">
                  Prevent Telegram bot flooding, abuse, API quota depletion, and enforce disciplined waiting periods.
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Analysis Cooldown Seconds */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-800">
                  Analysis Cooldown (ANALYSIS_COOLDOWN_SECONDS):{' '}
                  <span className="font-mono text-indigo-600 text-sm">{config.analysisCooldownSeconds}s</span>
                </label>
                <span className="text-[11px] text-zinc-500">Delay between /analyze</span>
              </div>
              <input
                type="range"
                min="1"
                max="30"
                step="1"
                value={config.analysisCooldownSeconds}
                onChange={(e) =>
                  setConfig({ ...config, analysisCooldownSeconds: Number(e.target.value) })
                }
                className="w-full accent-indigo-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-zinc-400 font-mono">
                <span>1s (Instant)</span>
                <span>5s (Standard)</span>
                <span>15s (Strict)</span>
                <span>30s (Disciplined)</span>
              </div>
              <p className="text-[11px] text-zinc-500 mt-1">
                Minimum wait time enforced before the same user can request another full quantitative snapshot.
              </p>
            </div>

            {/* Rate Limit Requests Per Min */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-800">
                  Max Requests Per Minute (RATE_LIMIT_REQUESTS_PER_MIN):{' '}
                  <span className="font-mono text-indigo-600 text-sm">{config.rateLimitRequestsPerMin} req/m</span>
                </label>
                <span className="text-[11px] text-zinc-500">Per user burst window</span>
              </div>
              <input
                type="range"
                min="5"
                max="60"
                step="5"
                value={config.rateLimitRequestsPerMin}
                onChange={(e) =>
                  setConfig({ ...config, rateLimitRequestsPerMin: Number(e.target.value) })
                }
                className="w-full accent-indigo-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-zinc-400 font-mono">
                <span>5 req/m (Safe)</span>
                <span>20 req/m (Standard)</span>
                <span>40 req/m</span>
                <span>60 req/m (High)</span>
              </div>
              <p className="text-[11px] text-zinc-500 mt-1">
                Sliding 60-second window quota. Excessive requests receive a gentle 429 cooldown prompt.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-zinc-100">
            <div>
              <label className="text-xs font-medium text-zinc-700 block mb-1">
                Max Daily Requests Per User
              </label>
              <input
                type="number"
                min="10"
                max="1000"
                value={config.maxDailyRequestsPerUser}
                onChange={(e) =>
                  setConfig({ ...config, maxDailyRequestsPerUser: Number(e.target.value) })
                }
                className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-zinc-200"
              />
              <span className="text-[10px] text-zinc-400 mt-1 block">
                Protects free tier Alpha Vantage quotas (500 calls/day)
              </span>
            </div>

            <div>
              <label className="text-xs font-medium text-zinc-700 block mb-1">
                System Logging Level (LOG_LEVEL)
              </label>
              <select
                value={config.logLevel}
                onChange={(e) => setConfig({ ...config, logLevel: e.target.value as any })}
                className="w-full text-xs font-medium px-3 py-2 rounded-lg border border-zinc-200 bg-white"
              >
                <option value="DEBUG">DEBUG (Detailed telemetry & trace logs)</option>
                <option value="INFO">INFO (Standard production logs)</option>
                <option value="WARNING">WARNING (Only warnings & errors)</option>
                <option value="ERROR">ERROR (Only critical faults)</option>
              </select>
              <span className="text-[10px] text-zinc-400 mt-1 block">Controls server and bot terminal verbosity</span>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 4. Database Path & SQLite Engine Section */}
      {/* ========================================================================= */}
      {(activeSection === 'all' || activeSection === 'database') && (
        <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-emerald-600" />
              <div>
                <h2 className="text-sm font-bold text-zinc-900">Database Storage Path (DATABASE_PATH)</h2>
                <p className="text-[11px] text-zinc-500">
                  SQLite database file location for users, signal performance logs, trade journal, and rate limiter caches.
                </p>
              </div>
            </div>
            <span className="text-xs px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 font-mono font-medium border border-emerald-200">
              WAL Mode Active
            </span>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-zinc-800 block">
              SQLite Database Path (DATABASE_PATH)
            </label>
            <input
              type="text"
              value={config.databasePath}
              onChange={(e) => setConfig({ ...config, databasePath: e.target.value })}
              placeholder="data/bot.db"
              className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-zinc-200 focus:ring-1 focus:ring-emerald-500"
            />
            <p className="text-[11px] text-zinc-500">
              The parent directory is automatically provisioned if it does not exist. Uses Write-Ahead Logging (WAL) for concurrent reads/writes.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 text-xs space-y-2">
            <span className="font-semibold text-zinc-800 block">Configured SQLite Schema Tables:</span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 font-mono text-[11px]">
              <div className="p-2 rounded bg-white border border-zinc-200">
                <span className="font-bold text-zinc-900">users</span>
                <p className="text-[10px] text-zinc-500 mt-0.5">telegram_id, registered_at, risk_tier</p>
              </div>
              <div className="p-2 rounded bg-white border border-zinc-200">
                <span className="font-bold text-zinc-900">trades</span>
                <p className="text-[10px] text-zinc-500 mt-0.5">asset, timeframe, confidence, outcome</p>
              </div>
              <div className="p-2 rounded bg-white border border-zinc-200">
                <span className="font-bold text-zinc-900">audit_logs</span>
                <p className="text-[10px] text-zinc-500 mt-0.5">confluence_score, bos, sweep, pips</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 5. Admin Access & Security Section */}
      {/* ========================================================================= */}
      {(activeSection === 'all' || activeSection === 'admin') && (
        <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-rose-600" />
              <div>
                <h2 className="text-sm font-bold text-zinc-900">Admin Authorization & Permissions (ADMIN_IDS)</h2>
                <p className="text-[11px] text-zinc-500">
                  Telegram user chat IDs permitted to execute administrative control commands (/stats, /broadcast, /cooldown).
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-zinc-800">
                Authorized Admin Chat IDs (Comma-separated)
              </label>
              {config.telegramChatId && (
                <button
                  type="button"
                  onClick={addCurrentChatToAdmin}
                  className="text-[11px] text-blue-600 hover:text-blue-800 font-medium"
                >
                  + Add Current Alert Chat ID ({config.telegramChatId})
                </button>
              )}
            </div>

            <input
              type="text"
              value={config.adminIds}
              onChange={(e) => setConfig({ ...config, adminIds: e.target.value })}
              placeholder="e.g. 123456789, 987654321"
              className="w-full text-xs font-mono px-3 py-2 rounded-lg border border-zinc-200"
            />
            <p className="text-[11px] text-zinc-500">
              Only IDs specified here can execute privileged bot commands, bypass analysis cooldowns, and view global performance stats.
            </p>

            {config.adminIds && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {config.adminIds
                  .split(',')
                  .map((id) => id.trim())
                  .filter(Boolean)
                  .map((id, index) => (
                    <span
                      key={index}
                      className="px-2 py-0.5 rounded-md bg-zinc-100 border border-zinc-200 text-zinc-800 font-mono text-[11px] flex items-center gap-1"
                    >
                      <Lock className="w-3 h-3 text-rose-500" />
                      Admin: {id}
                    </span>
                  ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 6. Live .env Exporter & Synchronizer */}
      {/* ========================================================================= */}
      {(activeSection === 'all' || activeSection === 'env') && (
        <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div className="flex items-center gap-2">
              <Terminal className="w-5 h-5 text-blue-600" />
              <div>
                <h2 className="text-sm font-bold text-zinc-900">Environment File (.env) Synchronizer</h2>
                <p className="text-[11px] text-zinc-500">
                  Dynamically compiled from all above Web UI inputs. Ready to run directly with Python or Docker.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={copyEnvFile}
                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-700 transition-colors flex items-center gap-1"
              >
                {copiedEnv ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                {copiedEnv ? 'Copied to Clipboard' : 'Copy .env'}
              </button>

              <button
                type="button"
                onClick={downloadEnvFile}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-zinc-900 hover:bg-zinc-800 text-white transition-colors flex items-center gap-1"
              >
                <Download className="w-3.5 h-3.5" />
                Download .env
              </button>
            </div>
          </div>

          <pre className="p-4 bg-zinc-950 text-zinc-300 rounded-xl text-xs font-mono overflow-x-auto max-h-72 border border-zinc-800 leading-relaxed select-all">
            {generateEnvFile(config)}
          </pre>
        </div>
      )}
    </div>
  );
};
