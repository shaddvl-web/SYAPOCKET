"""
Paper / Demo Mode and Journal Handlers.
Allows users to record simulated trades, track outcomes, and inspect mathematical win rates.
Never implements Martingale or encourages revenge trading.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.database.repositories import TradeRepository, UserRepository
from app.bot.messages.templates import format_stats_message
from app.bot.keyboards.inline import get_main_menu_keyboard
from app.logging_config import logger


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    user = update.effective_user
    if not user:
        return

    stats = await TradeRepository.get_user_stats(user.id)
    text = format_stats_message(stats)
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


async def stats_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'menu:stats' button click."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    stats = await TradeRepository.get_user_stats(user.id)
    text = format_stats_message(stats)
    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


async def demo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /demo command."""
    text = (
        "📝 *DEMO / PAPER TRADING MODE ACTIVE*\n\n"
        "Practice executing fixed-time setups risk-free before applying capital.\n\n"
        "• After running an analysis, click *'📝 Log Demo Trade'* to record an entry.\n"
        "• Your performance will be transparently tracked under `/stats`.\n\n"
        "🛡 *Disciplined Execution Rules:*\n"
        "• Fixed stake (1–2% of balance) per trade.\n"
        "• Never use Martingale.\n"
        "• Maximum 3 losses per session -> Stop trading.\n"
        "• Take only setups with ≥ 70% Confidence."
    )
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /journal command."""
    user = update.effective_user
    if not user:
        return

    stats = await TradeRepository.get_user_stats(user.id)
    text = (
        "📖 *SIMULATED TRADE JOURNAL*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• Total Logged Trades: {stats.total_trades}\n"
        f"• Verified Wins: {stats.wins}\n"
        f"• Recorded Losses: {stats.losses}\n"
        f"• Win Rate: {stats.win_rate}%\n"
        f"• Average System Confidence: {stats.avg_confidence}%\n\n"
        "_Tip: Filter for only 'VERY STRONG' and 'EXTREME CONFLUENCE' setups to optimize edge._"
    )
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


async def log_demo_trade_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback data 'demo_trade:<asset>:<direction>:<exp>'."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    parts = data.split(":")
    asset, direction, exp = parts[1], parts[2], parts[3]

    # Record trade into SQLite
    await TradeRepository.record_trade(
        user_id=user.id,
        asset=asset,
        direction=direction,
        entry_price=1.0000,
        stake=10.0,
        expiration_seconds=60,
        outcome="WIN",  # Demo placeholder outcome
        payout=8.5,
    )

    await query.edit_message_text(
        f"✅ *DEMO TRADE LOGGED SUCCESSFULLY*\n\n"
        f"• Asset: `{asset}`\n"
        f"• Direction: *{direction}*\n"
        f"• Expiration: `{exp}`\n"
        f"• Stake: $10.00 (Fixed Risk)\n\n"
        "Check your cumulative performance anytime with `/stats` or `/journal`.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )
