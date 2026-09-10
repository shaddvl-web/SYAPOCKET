"""
Signal generation handler.
Scans primary tradable pairs to identify immediate high-probability setups
or runs analysis on the user's preferred asset.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.analysis.engine import master_engine
from app.bot.keyboards.inline import get_analysis_result_keyboard, get_main_menu_keyboard
from app.bot.messages.templates import format_signal_message
from app.bot.middleware.rate_limit import rate_limiter
from app.database.repositories import UserRepository, AnalysisRepository
from app.market.models import Timeframe
from app.logging_config import logger


async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate high-confluence signal on user's default asset or scan top pairs."""
    user = update.effective_user
    if not user:
        return

    allowed, msg = rate_limiter.is_allowed(user.id)
    if not allowed:
        await update.message.reply_text(msg)
        return

    settings_record = await UserRepository.get_settings(user.id)
    asset = settings_record.default_asset
    tf = Timeframe.from_str(settings_record.default_timeframe)
    exp_str = settings_record.default_expiration

    status_msg = await update.message.reply_text(
        f"🎯 *SCANNING MARKET FOR HIGH CONFLUENCE SETUP...*\n"
        f"Inspecting `{asset}` ({tf.value} / {exp_str})...",
        parse_mode=ParseMode.MARKDOWN,
    )

    try:
        snapshot = await master_engine.analyze_market(
            asset=asset,
            timeframe=tf,
            expiration=exp_str,
            user_id=user.id,
        )
        await AnalysisRepository.save_analysis(user.id, snapshot)
        text = format_signal_message(snapshot)
        await status_msg.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_analysis_result_keyboard(asset, tf.value, exp_str, snapshot.decision.value),
        )
    except Exception as e:
        logger.error(f"Signal command error: {e}")
        await status_msg.edit_text(
            f"❌ Unable to generate signal: {str(e)}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )


async def signal_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle clicking 'menu:signal' in main menu."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    allowed, msg = rate_limiter.check_analysis_cooldown(user.id)
    if not allowed:
        await query.edit_message_text(f"⚠️ {msg}", reply_markup=get_main_menu_keyboard())
        return

    settings_record = await UserRepository.get_settings(user.id)
    asset = settings_record.default_asset
    tf = Timeframe.from_str(settings_record.default_timeframe)
    exp_str = settings_record.default_expiration

    await query.edit_message_text(
        f"🎯 *SCANNING MARKET FOR HIGH CONFLUENCE SETUP...*\n"
        f"Inspecting `{asset}` ({tf.value} / {exp_str})...",
        parse_mode=ParseMode.MARKDOWN,
    )

    try:
        snapshot = await master_engine.analyze_market(
            asset=asset,
            timeframe=tf,
            expiration=exp_str,
            user_id=user.id,
        )
        await AnalysisRepository.save_analysis(user.id, snapshot)
        text = format_signal_message(snapshot)
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_analysis_result_keyboard(asset, tf.value, exp_str, snapshot.decision.value),
        )
    except Exception as e:
        logger.error(f"Signal callback error: {e}")
        await query.edit_message_text(
            f"❌ Unable to generate signal: {str(e)}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )
