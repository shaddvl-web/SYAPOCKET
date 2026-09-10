# Pocket Option AI Analyzer Bot 📈🤖

An institutional-grade Quantitative Analysis and Decision-Support Telegram Bot specifically engineered for short-duration binary options / fixed-time trading (Pocket Option, Quotex, Deriv, Olymp Trade).

Built using **Python 3.12**, **python-telegram-bot (v21+)**, **FastAPI**, **Pandas**, **NumPy**, **SQLite (WAL Mode)**, and **httpx**.

---

## ⚠️ Important Disclaimer & Core Philosophy

> **Analysis & Decision Support Tool Only**  
> This system is designed solely to provide quantitative confirmation, market structure mapping, and risk-managed decision support. It does **NEVER claim guaranteed profits, 100% win-rates, or magical algorithmic predictions**. Financial markets involve significant risk. Never risk capital you cannot afford to lose.

### Core Tenets:
1. **Confirmation > Prediction**: We never forecast where price "will" go without structural proof.
2. **Quality > Quantity**: A gated **70% minimum confluence score** is required to trigger CALL or PUT. Conflicted, low-quality, or low-liquidity setups are strictly classified as **NO TRADE**.
3. **Context > Single Indicator**: Indicators (RSI, MACD, Bollinger Bands) never generate signals in isolation. They serve strictly as tertiary confirmation for close-based SMC structure, support/resistance clearance, and liquidity sweeps.

---

## 🏛️ System Architecture

The codebase adheres strictly to separation of concerns:
```
├── app/
│   ├── config.py              # Pydantic v2 settings & environment configuration
│   ├── logging_config.py      # Structured JSON logging & credential redaction
│   ├── market/                # Market Data Ingestion & Router
│   │   ├── models.py          # Candle, OHLCData, Timeframe domain models
│   │   ├── router.py          # Multi-provider router with fallback & TTL cache
│   │   └── providers/         # Synthetic, Deriv, Binance, CoinGecko providers
│   ├── analysis/              # Pure Quantitative Analysis Engines
│   │   ├── structure.py       # SMC: Swing High/Low, Close-based BOS, CHoCH
│   │   ├── indicators.py      # Vectorized RSI, MACD, EMA (9/21/50), ATR, Bollinger Bands
│   │   ├── support_resistance.py # Horizontal clustering, order blocks, round numbers
│   │   ├── liquidity.py       # Equal Highs (EQH), Equal Lows (EQL), Wick sweeps & rejections
│   │   ├── price_action.py    # Pinbar, Engulfing, Rejections, Marubozu
│   │   ├── momentum.py        # Acceleration, consecutive closes, exhaustion detection
│   │   ├── volatility.py      # ATR compression/expansion, spread & noise filters
│   │   ├── expiration.py      # 1m, 2m, 3m, 5m suitability & opposing level clearance
│   │   ├── confluence.py      # 0-100 Weighted scoring matrix & conflict gating
│   │   └── engine.py          # Master Analysis Orchestrator (Returns MarketAnalysisSnapshot)
│   ├── database/              # Persistence Layer
│   │   ├── database.py        # SQLite connection pool with PRAGMA journal_mode = WAL
│   │   ├── models.py          # User, AnalysisLog, TradeLog, UserStats
│   │   └── repositories.py    # Repositories for Users, Analytics, and Demo Journal
│   ├── utils/
│   │   └── vision.py          # AI Vision Chart Analyzer (Gemini Flash 1.5 + Fallback)
│   ├── bot/                   # Telegram Interface
│   │   ├── bot.py             # Bot builder & lifecycle management
│   │   ├── keyboards/         # Interactive inline menus (asset, TF, exp, demo logging)
│   │   ├── messages/          # Formatted output templates (Signals, Stats, Help, Admin)
│   │   ├── middleware/        # Rate limiting, user registration, anti-spam
│   │   └── handlers/          # Start, Analyze, Signal, Screenshot, Demo, Admin, Settings
│   └── api/
│       └── server.py          # FastAPI server for Docker, Cloud Run & Webhook mode
├── data/                      # Persistent SQLite DB directory
├── tests/                     # Automated Pytest Suite (Indicators, Structure, Confluence, etc.)
├── Dockerfile                 # Production multi-stage container
├── docker-compose.yml         # Container composition with persistent volume
├── run_windows.bat            # One-click Windows runner
├── run_linux.sh               # One-click Linux / VPS runner
├── requirements.txt           # Python dependencies
└── .env.example               # Environment variables template
```

---

## ⚖️ Confluence & Scoring Logic (0 - 100)

Signals are calculated using a 9-factor weighted scoring model:

| Factor | Max Weight | Criteria |
| :--- | :---: | :--- |
| **Market Structure (SMC)** | **20%** | Close-based BOS (no wicks) in direction of trade (+20), CHoCH reversal (+15), or aligned HH/HL sequence (+10). |
| **HTF Trend Confluence** | **15%** | M5 / M15 Higher Timeframe alignment with current lower timeframe direction. |
| **Support & Resistance** | **15%** | Clearance from opposing barrier (≥ 0.4 ATR) and bounce off key S/R or order block. |
| **Price Action Pattern** | **15%** | Rejection pin bar, engulfing candle, or momentum displacement candle. |
| **Momentum** | **10%** | Consecutive directional candles with expanding body sizes, not exhausted. |
| **Liquidity Sweep** | **10%** | Wick sweep beyond Equal Highs/Lows (EQH/EQL) with close back inside. |
| **Technical Indicators** | **5%** | RSI out of extreme zone + MACD line/signal expansion in signal direction. |
| **Volatility Condition** | **5%** | ATR in normal tradable range (penalties applied for dead market or chaotic spikes). |
| **Expiration Fit** | **5%** | Candle momentum and distance to nearest obstacle align with selected expiration. |

### Decision Thresholds:
- **CALL**: $\ge 70\%$ Confluence, Bullish structure, Clear upside to resistance.
- **PUT**: $\ge 70\%$ Confluence, Bearish structure, Clear downside to support.
- **NO TRADE**: $< 70\%$ Confluence, or when opposing conflicts are detected (e.g., trying to CALL directly into strong resistance or overbought RSI).

---

## 🚀 Quickstart Guide

### 1. Telegram Bot Token Setup via @BotFather
1. Open Telegram and search for [@BotFather](https://t.me/botfather).
2. Send `/newbot` and follow the instructions to choose a display name and username (e.g. `MyPocketOptionAnalyzerBot`).
3. Copy the HTTP API token provided by BotFather (looks like `123456789:ABCDefgh-ijk...`).

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your variables:
```env
TELEGRAM_BOT_TOKEN="your-telegram-bot-token-here"
ADMIN_IDS="your-telegram-user-id"
GEMINI_API_KEY="optional-for-screenshot-chart-analysis"
BOT_MODE="polling"
PORT=3000
```

---

## 💻 Running the Bot

### Option A: Windows
Double click `run_windows.bat` or run:
```bat
run_windows.bat
```
The script will create a virtual environment, install requirements, and prompt you to run either Long Polling mode or the FastAPI Webhook Server.

### Option B: Linux / VPS
```bash
chmod +x run_linux.sh
# Run in Long Polling mode:
./run_linux.sh polling

# Or run in Webhook / FastAPI Server mode:
./run_linux.sh server
```

### Option C: Docker / Docker Compose
Build and start the container with persistent storage:
```bash
docker compose up --build -d
```
View logs:
```bash
docker compose logs -f
```

---

## 📱 Bot Commands & Usage

| Command | Description |
| :--- | :--- |
| `/start` | Launch the bot, display welcome banner, risk disclaimer, and main menu. |
| `/analyze` | Interactive menu to choose Asset (EUR/USD, GBP/USD, etc.), Timeframe (M1-M15), and Expiration (1m-5m). |
| `/signal` | Quick-analyze the current default asset and return an immediate recommendation. |
| `/screenshot` | Send a screenshot of your Pocket Option chart for Vision AI multimodal structure analysis. |
| `/demo` | Log a demo/paper trade (Asset, Direction, Stake, Expiry) to track discipline. |
| `/stats` | View real performance statistics (Win Rate, Total Trades, Profit Factor, Discipline Score). |
| `/settings` | Customize your default asset, timeframe, expiration, and sensitivity threshold. |
| `/help` | Detailed trading guide explaining SMC, BOS, CHoCH, liquidity sweeps, and risk management. |
| `/admin` | (Admin Only) View total users, system health, and database metrics. |

---

## 🧪 Automated Testing

Run the full pytest suite:
```bash
python3 -m pytest -v
```
All 14 tests validate:
- Vectorized RSI, MACD, ATR, EMA, Bollinger calculations
- Close-based BOS (Break of Structure) vs. wick-only breakout rejection
- Liquidity sweeps & wick rejections of Equal Highs/Lows
- Confluence gating (< 70% strictly forces NO TRADE)
- Multi-engine master pipeline execution
- Market data provider failovers & caching
- SQLite WAL mode database persistence & telemetry
- FastAPI `/health`, `/status`, and `/api/analyze` endpoints

---

## 🛠️ Troubleshooting

1. **"Bot token is invalid"**: Verify `TELEGRAM_BOT_TOKEN` in your `.env` matches the token provided by BotFather.
2. **"Rate limit reached"**: Users are protected against spam by a rolling cooldown (default 5 seconds between analysis calls).
3. **"Chart image could not be analyzed"**: Ensure `GEMINI_API_KEY` is set in `.env` if you want multimodal Vision analysis of chart images. If not set, the bot automatically falls back to an algorithmic heuristic analysis.
4. **FastAPI port conflict**: The API binds to port `3000` by default. You can change `PORT=3000` in `.env` if running locally without Docker.
