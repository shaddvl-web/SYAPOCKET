"""
Market Analysis handlers for Telegram Bot.
Provides interactive inline keyboard wizard and direct command argument parsing (/analyze EURUSD M1 1m).
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.analysis.engine import master_engine
from app.bot.keyboards.inline import (
    get_asset_selection_keyboard,
    get_timeframe_keyboard,
    get_expiration_keyboard,
    get_analysis_result_keyboard,
    get_main_menu_keyboard,
)
from app.bot.messages.templates import format_signal_message
from app.bot.middleware.rate_limit import rate_limiter
from app.database.repositories import UserRepository, AnalysisRepository
from app.market.models import Timeframe
from app.logging_config import logger


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /analyze command.
    Accepts direct syntax: /analyze EURUSD M1 1m
    Or opens interactive selection menu if no args provided.
    """
    user = update.effective_user
    if not user:
        return

    # Check general rate limit
    allowed, msg = rate_limiter.is_allowed(user.id)
    if not allowed:
        await update.message.reply_text(msg)
        return

    args = context.args or []
    if len(args) >= 1:
        # User provided direct arguments, e.g. /analyze EURUSD M1 1m
        asset = args[0].upper()
        tf_str = args[1].upper() if len(args) > 1 else "M1"
        exp_str = args[2].lower() if len(args) > 2 else "1m"

        try:
            tf = Timeframe.from_str(tf_str)
        except ValueError:
            await update.message.reply_text(f"❌ Invalid timeframe '{tf_str}'. Supported: M1, M5, M15, M30, H1.")
            return

        await run_and_reply_analysis(update, user.id, asset, tf, exp_str)
    else:
        # Prompt user with asset picker
        await update.message.reply_text(
            "📊 *MARKET ANALYSIS WIZARD*\n\n"
            "Step 1: Select the asset you want the AI to analyze:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_asset_selection_keyboard(),
        )


async def analyze_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle interactive inline keyboard clicks for analysis wizard."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    if data == "menu:analyze":
        await query.edit_message_text(
            "📊 *MARKET ANALYSIS WIZARD*\n\n"
            "Step 1: Select the asset you want the AI to analyze:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_asset_selection_keyboard(),
        )

    elif data.startswith("asset:"):
        asset = data.split(":", 1)[1]
        await query.edit_message_text(
            f"📊 *Asset Selected:* `{asset}`\n\n"
            "Step 2: Choose your chart timeframe:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_timeframe_keyboard(asset),
        )

    elif data.startswith("tf:"):
        parts = data.split(":")
        asset, tf_str = parts[1], parts[2]
        await query.edit_message_text(
            f"📊 *Asset:* `{asset}`\n"
            f"⏱ *Timeframe:* `{tf_str}`\n\n"
            "Step 3: Select your target fixed-time expiration:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_expiration_keyboard(asset, tf_str),
        )

    elif data.startswith("run:"):
        parts = data.split(":")
        asset, tf_str, exp_str = parts[1], parts[2], parts[3]
        tf = Timeframe.from_str(tf_str)

        # Rate limit cooldown check
        allowed, msg = rate_limiter.check_analysis_cooldown(user.id)
        if not allowed:
            await query.edit_message_text(f"⚠️ {msg}", reply_markup=get_main_menu_keyboard())
            return

        await query.edit_message_text(
            f"🧠 *ANALYZING {asset} ({tf.value} / {exp_str})...*\n\n"
            "• Inspecting price action & order blocks\n"
            "• Verifying close-based BOS & CHoCH\n"
            "• Testing liquidity sweeps & wick rejections\n"
            "• Computing multi-factor confluence score...",
            parse_mode=ParseMode.MARKDOWN,
        )

        try:
            snapshot = await master_engine.analyze_market(
                asset=asset,
                timeframe=tf,
                expiration=exp_str,
                user_id=user.id,
            )

            # Persist to database
            await AnalysisRepository.save_analysis(user.id, snapshot)

            # Send formatted signal message
            reply_text = format_signal_message(snapshot)
            await query.edit_message_text(
                reply_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_analysis_result_keyboard(asset, tf.value, exp_str, snapshot.decision.value),
            )

        except Exception as e:
            logger.error(f"Analysis error for {user.id}: {e}")
            await query.edit_message_text(
                f"❌ *Analysis Notice:*\n\n"
                f"Market data temporarily unavailable for `{asset}`: {str(e)}\n\n"
                "Please try another asset or check back in a moment.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard(),
            )


async def run_and_reply_analysis(update: Update, user_id: int, asset: str, tf: Timeframe, exp_str: str):
    """Helper to run analysis and send response."""
    allowed, msg = rate_limiter.check_analysis_cooldown(user_id)
    if not allowed:
        await update.message.reply_text(f"⚠️ {msg}")
        return

    status_msg = await update.message.reply_text(
        f"🧠 *ANALYZING {asset}...*\nCalculating confluence score...",
        parse_mode=ParseMode.MARKDOWN,
    )

    try:
        snapshot = await master_engine.analyze_market(
            asset=asset,
            timeframe=tf,
            expiration=exp_str,
            user_id=user_id,
        )
        await AnalysisRepository.save_analysis(user_id, snapshot)
        reply_text = format_signal_message(snapshot)
        await status_msg.edit_text(
            reply_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_analysis_result_keyboard(asset, tf.value, exp_str, snapshot.decision.value),
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        await status_msg.edit_text(
            f"❌ *Analysis Error:* {str(e)}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )
