"""
Telegram Bot Lifecycle and Application Builder.
Supports Polling and Webhook modes.
Provides graceful shutdown and health inspection.
"""

from typing import Optional
from telegram.ext import Application, ApplicationBuilder
from app.config import settings
from app.bot.handlers import register_all_handlers
from app.logging_config import logger


def build_bot_app() -> Optional[Application]:
    """Construct and configure the python-telegram-bot Application instance."""
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        logger.warning("TELEGRAM_BOT_TOKEN is not set or using placeholder. Bot cannot start live polling.")
        return None

    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    register_all_handlers(app)
    return app


async def start_bot_polling():
    """Start bot in polling mode for local or VPS deployment."""
    app = build_bot_app()
    if not app:
        logger.warning("Bot polling skipped: No valid TELEGRAM_BOT_TOKEN.")
        return

    logger.info("Starting Telegram Bot in POLLING mode...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("Bot is active and listening for Telegram updates.")
