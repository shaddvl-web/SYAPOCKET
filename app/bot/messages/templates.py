"""
Telegram Message Templates.
Implements the exact layout and visual design requested in Sections 19, 21, and 25.
Never claims guaranteed profits or 100% accuracy.
"""

from app.analysis.engine import MarketAnalysisSnapshot
from app.database.models import StatisticsSummary


def format_start_message(first_name: str = "Trader") -> str:
    """Welcome greeting, bot description, risk warning, and primary guidance."""
    return (
        f"👋 *Welcome, {first_name}!* to\n\n"
        "⚡️ *POCKET OPTION AI ANALYZER BOT* ⚡️\n\n"
        "An institutional-grade quantitative decision-support system designed specifically "
        "for fixed-time market analysis.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *CORE CAPABILITIES:*\n"
        "• *Market Structure*: True close-based BOS, CHoCH, HH/HL/LH/LL\n"
        "• *Liquidity Engine*: Equal highs/lows & wick sweeps\n"
        "• *Key Levels*: Dynamic S/R, Supply/Demand order blocks\n"
        "• *Confluence Gating*: Strict 0–100 score (signals require ≥ 70%)\n"
        "• *Pocket Expiration*: Timeframe & ATR ratio compatibility\n"
        "• *Vision AI*: Chart screenshot perception\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ *RISK DISCLAIMER:*\n"
        "This system is an analytical and educational decision-support tool. "
        "It *NEVER* guarantees profits or 100% accuracy. "
        "Financial markets carry substantial risk. Always manage your capital responsibly.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an option below to begin:"
    )


def format_help_message() -> str:
    """Help and command reference guide."""
    return (
        "📖 *POCKET OPTION AI ANALYZER - COMMAND GUIDE*\n\n"
        "• `/start` - Open the main menu\n"
        "• `/analyze` - Launch interactive market analysis wizard\n"
        "• `/analyze <Asset> <Timeframe> <Expiration>` - Quick analysis\n"
        "   _Example: `/analyze EURUSD M1 1m`_\n"
        "• `/signal` - Generate immediate high-confluence setup\n"
        "• `/stats` - View your analysis and demo trading performance\n"
        "• `/demo` - Enter paper trading mode (record simulated trades)\n"
        "• `/journal` - Review recent demo trades\n"
        "• `/settings` - Configure preferred assets and timeframes\n"
        "• `/status` - Check provider latency and system health\n"
        "• Send any *chart screenshot* to trigger AI Vision Analysis 📷\n\n"
        "💡 *Golden Rule*: When the market is unclear or conflicting, "
        "the bot will return *NO TRADE*. Quality always beats quantity."
    )


def format_signal_message(s: MarketAnalysisSnapshot) -> str:
    """
    Format output matching Section 21 of user specification.
    """
    bos_str = "CONFIRMED" if s.bos_confirmed else "NO"
    choch_str = "YES" if s.choch_detected else "NO"

    sup_str = f"{s.nearest_support:.5f}" if s.nearest_support else "N/A"
    res_str = f"{s.nearest_resistance:.5f}" if s.nearest_resistance else "N/A"

    if s.decision.value == "CALL":
        decision_header = "🟢 CALL"
    elif s.decision.value == "PUT":
        decision_header = "🔴 PUT"
    else:
        decision_header = "🔴 NO TRADE"

    # Bullets for reasons
    reasons_formatted = "\n".join(f"• {r}" for r in s.reasons)

    msg = (
        "━━━━━━━━━━━━━━━━━━\n"
        "🧠 *AI MARKET ANALYSIS*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💱 *Asset:*\n{s.asset}\n\n"
        f"⏱ *Timeframe:*\n{s.timeframe}\n\n"
        f"⌛ *Expiration:*\n{s.expiration}\n\n"
        f"📊 *Market:*\n{s.trend}\n\n"
        f"📈 *Structure:*\n{s.structure_summary}\n\n"
        f"🟢 *BOS:*\n{bos_str}\n\n"
        f"🔄 *CHoCH:*\n{choch_str}\n\n"
        f"💧 *Liquidity:*\n{s.liquidity_summary}\n\n"
        f"📍 *Support:*\n{sup_str}\n\n"
        f"📍 *Resistance:*\n{res_str}\n\n"
        f"📈 *Momentum:*\n{s.momentum}\n\n"
        f"📊 *RSI:*\n{s.rsi:.1f}\n\n"
        f"🔥 *Volatility:*\n{s.volatility}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 *DECISION:*\n\n"
        f"{decision_header}\n\n"
        f"Confidence:\n{s.confidence:.0f}%\n\n"
        f"Quality:\n{s.quality}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🧠 *REASON:*\n\n"
        f"{reasons_formatted}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ _This is market analysis, not a guaranteed outcome._\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    return msg


def format_stats_message(stats: StatisticsSummary) -> str:
    """Section 25 performance and statistics display."""
    return (
        "📊 *QUANTITATIVE SYSTEM STATISTICS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📈 *Total Analyses Generated:* {stats.total_analyses}\n"
        f"🟢 *CALL Signals:* {stats.call_signals}\n"
        f"🔴 *PUT Signals:* {stats.put_signals}\n"
        f"🟡 *NO TRADE (Filtered):* {stats.no_trades}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📝 *DEMO TRADING JOURNAL:*\n"
        f"🎯 *Total Paper Trades:* {stats.total_trades}\n"
        f"✅ *Wins:* {stats.wins}\n"
        f"❌ *Losses:* {stats.losses}\n"
        f"🏆 *Win Rate:* {stats.win_rate:.1f}%\n"
        f"🔍 *Average Confidence:* {stats.avg_confidence:.1f}%\n"
        f"🔥 *Max Consecutive Wins:* {stats.consecutive_wins}\n"
        f"❄️ *Max Consecutive Losses:* {stats.consecutive_losses}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌟 *Best Setup:* {stats.best_setup}\n"
        f"⚠️ *Worst Setup:* {stats.worst_setup}\n\n"
        "_Note: Simulated statistics are strictly transparent and unmanipulated._"
    )
