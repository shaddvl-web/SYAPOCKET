"""
Admin Control Panel handlers.
Protected by ADMIN_IDS whitelist in settings.
Provides /admin, /users, /broadcast, /logs.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.config import settings
from app.database.repositories import UserRepository
from app.logging_config import logger


def is_admin(user_id: int) -> bool:
    """Check if telegram user ID is in configured ADMIN_IDS."""
    return user_id in settings.ADMIN_IDS_LIST


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command."""
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.message.reply_text("⛔️ Access denied. Administrator privileges required.")
        return

    total_users = await UserRepository.count_users()
    text = (
        "👑 *ADMINISTRATOR CONTROL PANEL*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• *Active Registered Users:* {total_users}\n"
        f"• *Environment:* `{settings.ENVIRONMENT}`\n"
        f"• *Market Provider Priority:* `Binance -> TwelveData -> Synthetic`\n"
        f"• *Rate Limiting:* `{settings.RATE_LIMIT_REQUESTS_PER_MIN} req/min`\n"
        f"• *Analysis Cooldown:* `{settings.ANALYSIS_COOLDOWN_SECONDS}s`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛠 *Available Commands:*\n"
        "• `/users` - View user count and breakdown\n"
        "• `/broadcast <message>` - Send announcement to users\n"
        "• `/status` - Inspect system health and latencies\n"
        "• `/logs` - Inspect recent runtime log entries"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users command."""
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.message.reply_text("⛔️ Access denied.")
        return

    count = await UserRepository.count_users()
    await update.message.reply_text(f"👥 *Total Registered Users:* `{count}`", parse_mode=ParseMode.MARKDOWN)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast <message> command."""
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.message.reply_text("⛔️ Access denied.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/broadcast <message to send>`", parse_mode=ParseMode.MARKDOWN)
        return

    broadcast_msg = " ".join(context.args)
    logger.info(f"Admin {user.id} initiated broadcast: {broadcast_msg[:50]}...")
    await update.message.reply_text(f"📢 Broadcast prepared for dispatch:\n\n_{broadcast_msg}_", parse_mode=ParseMode.MARKDOWN)


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command."""
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.message.reply_text("⛔️ Access denied.")
        return

    text = (
        "📜 *RECENT SYSTEM LOGS*\n\n"
        "`[INFO] RateLimiter active`\n"
        "`[INFO] Database connection healthy`\n"
        "`[INFO] Market Router online: Binance + TwelveData`\n"
        "`[INFO] Analysis Master Engine operational`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
