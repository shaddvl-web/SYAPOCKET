import { SystemBotConfig } from '../types';

export const DEFAULT_SYSTEM_CONFIG: SystemBotConfig = {
  telegramBotToken: '',
  botMode: 'polling',
  webhookUrl: '',
  host: '0.0.0.0',
  port: 3000,
  adminIds: '',
  databasePath: 'data/bot.db',
  defaultMarketProvider: 'binance',
  alphaVantageApiKey: '',
  twelveDataApiKey: '',
  geminiApiKey: '',
  rateLimitRequestsPerMin: 20,
  analysisCooldownSeconds: 5,
  maxDailyRequestsPerUser: 100,
  logLevel: 'INFO',
  defaultAsset: 'EUR/USD',
  defaultTimeframe: 'M1',
  defaultExpiration: '1m',
  minConfidence: 70,
  requireBos: true,
  requireSweep: false,
  minSrClearanceAtr: 0.4,
  telegramChatId: '',
  autoSendTelegram: false,
};

const STORAGE_KEY = 'po_analyzer_system_master_config';

/**
 * Load system configuration from localStorage, merging with defaults
 */
export function loadSystemConfig(): SystemBotConfig {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return { ...DEFAULT_SYSTEM_CONFIG, ...parsed };
    }
    // Also check older key for backwards compatibility
    const oldConfigRaw = localStorage.getItem('po_analyzer_user_config');
    if (oldConfigRaw) {
      const oldConfig = JSON.parse(oldConfigRaw);
      return {
        ...DEFAULT_SYSTEM_CONFIG,
        telegramBotToken: oldConfig.telegramBotToken || '',
        telegramChatId: oldConfig.telegramChatId || '',
        autoSendTelegram: oldConfig.autoSendTelegram || false,
        defaultAsset: oldConfig.asset || 'EUR/USD',
        defaultTimeframe: oldConfig.timeframe || 'M1',
        defaultExpiration: oldConfig.expiration || '1m',
        minConfidence: oldConfig.minConfidence ?? 70,
        requireBos: oldConfig.requireBos ?? true,
        requireSweep: oldConfig.requireSweep ?? false,
        minSrClearanceAtr: oldConfig.minSrClearanceAtr ?? 0.4,
      };
    }
  } catch (err) {
    console.warn('Failed to load saved system config from storage:', err);
  }
  return DEFAULT_SYSTEM_CONFIG;
}

/**
 * Save system configuration to localStorage and sync with user config key
 */
export function saveSystemConfig(config: SystemBotConfig): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    // Keep user config in sync for the AnalyzerConsole
    const userConfig = {
      asset: config.defaultAsset,
      timeframe: config.defaultTimeframe,
      expiration: config.defaultExpiration,
      minConfidence: config.minConfidence,
      requireBos: config.requireBos,
      requireSweep: config.requireSweep,
      minSrClearanceAtr: config.minSrClearanceAtr,
      rsiOverbought: 70,
      rsiOversold: 30,
      marketBias: 'auto',
      telegramBotToken: config.telegramBotToken,
      telegramChatId: config.telegramChatId,
      autoSendTelegram: config.autoSendTelegram,
    };
    localStorage.setItem('po_analyzer_user_config', JSON.stringify(userConfig));
  } catch (err) {
    console.warn('Failed to persist system config:', err);
  }
}

/**
 * Generate formatted .env file content
 */
export function generateEnvFile(config: SystemBotConfig): string {
  return `# ==============================================================================
# Pocket Option AI Analyzer Bot - Environment Configuration
# Generated directly from Web UI System & API Settings Console
# ==============================================================================

# Application Metadata
APP_NAME="Pocket Option AI Analyzer Bot"
APP_VERSION="1.0.0"
ENVIRONMENT="production"
LOG_LEVEL="${config.logLevel || 'INFO'}"

# Telegram Bot Credentials (Obtained from @BotFather)
TELEGRAM_BOT_TOKEN="${config.telegramBotToken || 'YOUR_TELEGRAM_BOT_TOKEN_HERE'}"

# Bot Operation Mode: 'polling' (dev/vps standard) or 'webhook' (cloud/ssl)
BOT_MODE="${config.botMode}"

# Webhook & Server Ingress
WEBHOOK_URL="${config.webhookUrl || ''}"
HOST="${config.host || '0.0.0.0'}"
PORT=${config.port || 3000}

# Admin Telegram IDs (comma-separated chat IDs authorized for /stats and admin commands)
ADMIN_IDS="${config.adminIds || ''}"

# Database Configuration (SQLite WAL Mode)
DATABASE_PATH="${config.databasePath || 'data/bot.db'}"

# Market Data Providers
# Supported: 'binance' (default crypto/fx), 'alpha_vantage', 'twelve_data', 'synthetic'
DEFAULT_MARKET_PROVIDER="${config.defaultMarketProvider}"
ALPHA_VANTAGE_API_KEY="${config.alphaVantageApiKey || ''}"
TWELVE_DATA_API_KEY="${config.twelveDataApiKey || ''}"

# Rate Limiting & Cooldown Protection
RATE_LIMIT_REQUESTS_PER_MIN=${config.rateLimitRequestsPerMin || 20}
ANALYSIS_COOLDOWN_SECONDS=${config.analysisCooldownSeconds || 5}

# Quantitative Default Strategy Gates
DEFAULT_ASSET="${config.defaultAsset || 'EUR/USD'}"
DEFAULT_TIMEFRAME="${config.defaultTimeframe || 'M1'}"
DEFAULT_EXPIRATION="${config.defaultExpiration || '1m'}"
MIN_CONFLUENCE_THRESHOLD=${config.minConfidence || 70}
REQUIRE_CLOSE_BASED_BOS=${config.requireBos ? 'true' : 'false'}
REQUIRE_LIQUIDITY_SWEEP=${config.requireSweep ? 'true' : 'false'}
MIN_SR_CLEARANCE_ATR=${config.minSrClearanceAtr || 0.4}

# Optional Vision AI Engine (Gemini Pro/Flash for screenshot chart analysis)
GEMINI_API_KEY="${config.geminiApiKey || ''}"
`;
}

/**
 * Live test of Telegram Bot Token against official Telegram API
 */
export async function testTelegramBotToken(token: string): Promise<{
  success: boolean;
  message: string;
  botDetails?: {
    id: number;
    is_bot: boolean;
    first_name: string;
    username?: string;
    can_join_groups?: boolean;
    can_read_all_group_messages?: boolean;
  };
}> {
  if (!token || !token.trim()) {
    return { success: false, message: 'Please provide a Telegram Bot Token first.' };
  }

  const cleanToken = token.trim();
  try {
    const res = await fetch(`https://api.telegram.org/bot${cleanToken}/getMe`);
    const data = await res.json();
    if (data.ok && data.result) {
      return {
        success: true,
        message: `Verified! Connected to @${data.result.username || data.result.first_name} (ID: ${data.result.id})`,
        botDetails: data.result,
      };
    } else {
      return {
        success: false,
        message: `Telegram Error: ${data.description || 'Invalid token or bot not found.'}`,
      };
    }
  } catch (err) {
    return {
      success: false,
      message: `Network/CORS error reaching Telegram: ${String(err)}`,
    };
  }
}

/**
 * Test Telegram Webhook Info
 */
export async function testTelegramWebhook(token: string): Promise<{
  success: boolean;
  message: string;
  details?: Record<string, any>;
}> {
  if (!token || !token.trim()) {
    return { success: false, message: 'Bot Token required to query webhook status.' };
  }
  try {
    const res = await fetch(`https://api.telegram.org/bot${token.trim()}/getWebhookInfo`);
    const data = await res.json();
    if (data.ok && data.result) {
      const url = data.result.url || 'None (Running in Polling mode)';
      return {
        success: true,
        message: `Current Webhook URL: ${url}`,
        details: data.result,
      };
    }
    return { success: false, message: data.description || 'Failed to fetch webhook info.' };
  } catch (err) {
    return { success: false, message: `Error checking webhook: ${String(err)}` };
  }
}

/**
 * Set Webhook on Telegram
 */
export async function setTelegramWebhook(token: string, webhookUrl: string): Promise<{
  success: boolean;
  message: string;
}> {
  if (!token || !webhookUrl) {
    return { success: false, message: 'Both Bot Token and Webhook URL are required.' };
  }
  try {
    const endpoint = `https://api.telegram.org/bot${token.trim()}/setWebhook?url=${encodeURIComponent(
      webhookUrl.trim()
    )}`;
    const res = await fetch(endpoint);
    const data = await res.json();
    if (data.ok) {
      return { success: true, message: `Webhook set successfully: ${data.description || 'OK'}` };
    }
    return { success: false, message: `Telegram Error: ${data.description || 'Failed to set webhook'}` };
  } catch (err) {
    return { success: false, message: `Error setting webhook: ${String(err)}` };
  }
}

/**
 * Delete Webhook on Telegram to restore Polling Mode
 */
export async function deleteTelegramWebhook(token: string): Promise<{
  success: boolean;
  message: string;
}> {
  if (!token) {
    return { success: false, message: 'Bot Token required.' };
  }
  try {
    const endpoint = `https://api.telegram.org/bot${token.trim()}/deleteWebhook?drop_pending_updates=true`;
    const res = await fetch(endpoint);
    const data = await res.json();
    if (data.ok) {
      return { success: true, message: 'Webhook deleted. Bot is ready for Polling Mode.' };
    }
    return { success: false, message: data.description || 'Failed to delete webhook.' };
  } catch (err) {
    return { success: false, message: `Error deleting webhook: ${String(err)}` };
  }
}

/**
 * Test Alpha Vantage API Key
 */
export async function testAlphaVantageKey(apiKey: string): Promise<{
  success: boolean;
  message: string;
}> {
  if (!apiKey || !apiKey.trim()) {
    return { success: false, message: 'Please enter an Alpha Vantage API key.' };
  }
  try {
    const cleanKey = apiKey.trim();
    // Query a standard quote to test validity
    const res = await fetch(
      `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=${cleanKey}`
    );
    const data = await res.json();

    if (data['Global Quote'] && Object.keys(data['Global Quote']).length > 0) {
      const price = data['Global Quote']['05. price'];
      return {
        success: true,
        message: `Valid! Alpha Vantage live test quote returned successfully (Sample: IBM @ $${price})`,
      };
    } else if (data['Note']) {
      return {
        success: true,
        message: `Valid API Key (Alpha Vantage API rate limit notice: ${data['Note'].slice(0, 70)}...)`,
      };
    } else if (data['Information']) {
      return {
        success: true,
        message: `Valid API Key: ${data['Information'].slice(0, 80)}...`,
      };
    } else if (data['Error Message']) {
      return {
        success: false,
        message: `Alpha Vantage Error: ${data['Error Message']}`,
      };
    } else {
      return {
        success: false,
        message: 'Unexpected response format from Alpha Vantage. Please verify key.',
      };
    }
  } catch (err) {
    return {
      success: false,
      message: `Network/CORS error testing Alpha Vantage: ${String(err)}`,
    };
  }
}
