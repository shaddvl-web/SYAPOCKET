export type SignalDecision = 'CALL' | 'PUT' | 'NO TRADE';

export interface SystemBotConfig {
  // Telegram Bot & Webhook
  telegramBotToken: string;
  botMode: 'polling' | 'webhook';
  webhookUrl: string;
  host: string;
  port: number;
  adminIds: string;

  // Database
  databasePath: string;

  // Market Providers & APIs
  defaultMarketProvider: 'binance' | 'alpha_vantage' | 'twelve_data' | 'synthetic';
  alphaVantageApiKey: string;
  twelveDataApiKey: string;
  geminiApiKey: string;

  // Rate Limiting & Cooldowns
  rateLimitRequestsPerMin: number;
  analysisCooldownSeconds: number;
  maxDailyRequestsPerUser: number;
  logLevel: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';

  // Default Request Parameters
  defaultAsset: string;
  defaultTimeframe: string;
  defaultExpiration: string;
  minConfidence: number;
  requireBos: boolean;
  requireSweep: boolean;
  minSrClearanceAtr: number;

  // Telegram Direct Integration (Chat ID for alerts)
  telegramChatId: string;
  autoSendTelegram: boolean;
}

export interface AnalysisConfig {
  asset: string;
  timeframe: string;
  expiration: string;
  minConfidence: number; // 50 to 95
  requireBos: boolean;
  requireSweep: boolean;
  minSrClearanceAtr: number; // 0.2 to 2.0
  rsiOverbought: number;
  rsiOversold: number;
  marketBias: 'auto' | 'bullish' | 'bearish' | 'ranging';
  telegramBotToken: string;
  telegramChatId: string;
  autoSendTelegram: boolean;
}

export interface RequestPreset {
  id: string;
  name: string;
  description: string;
  config: Partial<AnalysisConfig>;
}

export interface MarketAnalysisResult {
  asset: string;
  timeframe: string;
  expiration: string;
  currentPrice: number;
  decision: SignalDecision;
  confidence: number;
  quality: 'A+ (PREMIUM)' | 'A (HIGH QUALITY)' | 'B (MODERATE)' | 'C (LOW / CONFLICTED)';
  marketStructure: {
    summary: string;
    trend: string;
    bosConfirmed: boolean;
    chochDetected: boolean;
  };
  liquidity: {
    status: string;
    sweepDetected: boolean;
    poolCount: number;
  };
  sr: {
    nearestSupport: number;
    nearestResistance: number;
    distSupportPips: number;
    distResistancePips: number;
    callBlocked: boolean;
    putBlocked: boolean;
  };
  indicators: {
    rsi: number;
    rsiStatus: string;
    macdHistogram: number;
    macdSignal: string;
    atr: number;
    emaTrend: string;
  };
  reasons: string[];
  conflicts: string[];
  executionTimeMs: number;
  timestamp: string;
}

export interface DemoTrade {
  id: string;
  asset: string;
  direction: 'CALL' | 'PUT';
  entryPrice: number;
  exitPrice?: number;
  stake: number;
  expiration: string;
  outcome: 'WIN' | 'LOSS' | 'PENDING' | 'REFUND';
  pnl?: number;
  timestamp: string;
}

export interface SystemStats {
  totalTrades: number;
  wins: number;
  losses: number;
  winRate: number;
  netPnl: number;
  profitFactor: number;
  disciplineScore: number;
}
