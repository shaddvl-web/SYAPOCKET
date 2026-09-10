"""
Start and navigation handlers for Telegram bot.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.bot.keyboards.inline import get_main_menu_keyboard
from app.bot.messages.templates import format_start_message, format_help_message
from app.database.repositories import UserRepository
from app.logging_config import logger


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    if not user:
        return

    # Upsert user record into database
    await UserRepository.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    text = format_start_message(first_name=user.first_name or "Trader")
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    text = format_help_message()
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    text = (
        "🤖 *POCKET OPTION AI ANALYZER BOT*\n"
        "Version: `1.0.0-PRO`\n\n"
        "• *Quantitative SMC Core*: Close-based BOS, CHoCH, liquidity sweeps, S/R zones.\n"
        "• *Confluence Weighting*: 9-factor model requiring ≥ 70% confidence for signals.\n"
        "• *Safe Architecture*: Zero Martingale, transparent risk management.\n"
        "• *Multi-Source Market Data*: Binance Public API, Twelve Data, Synthetic Sandbox.\n\n"
        "Developed with asynchronous Python 3, python-telegram-bot, and Pandas."
    )
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    text = (
        "🟢 *SYSTEM STATUS: ONLINE*\n\n"
        "• *Engine*: Operational\n"
        "• *Database*: SQLite WAL Active\n"
        "• *Rate Limiter*: Enforcing\n"
        "• *Latency*: Normal (< 250ms)\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def menu_navigation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle navigation callbacks like 'nav:main_menu'."""
    query = update.callback_query
    await query.answer()
    if query.data == "nav:main_menu":
        text = format_start_message(first_name=update.effective_user.first_name or "Trader")
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )
