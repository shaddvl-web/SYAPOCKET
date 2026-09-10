"""
Bot Handler Registration Hub.
Registers all commands, message listeners, callback queries, and error handlers.
"""

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from app.bot.handlers.start import start_command, help_command, about_command, status_command, menu_navigation_callback
from app.bot.handlers.analyze import analyze_command, analyze_callback_handler
from app.bot.handlers.signal import signal_command, signal_callback_handler
from app.bot.handlers.screenshot import photo_message_handler
from app.bot.handlers.demo import (
    stats_command,
    stats_callback_handler,
    demo_command,
    journal_command,
    log_demo_trade_callback,
)
from app.bot.handlers.admin import admin_command, users_command, broadcast_command, logs_command
from app.bot.handlers.settings import settings_command, settings_callback_handler
from app.logging_config import logger


async def error_handler(update, context):
    """Global uncaught exception handler."""
    logger.error(f"Uncaught Telegram exception: {context.error}", exc_info=context.error)
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ An internal system error occurred while processing your request. Please try again in a few moments."
            )
        except Exception:
            pass


def register_all_handlers(application: Application):
    """Register all bot command and callback handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("signal", signal_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("demo", demo_command))
    application.add_handler(CommandHandler("journal", journal_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # Admin commands
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("logs", logs_command))

    # Photo / Screenshot handler
    application.add_handler(MessageHandler(filters.PHOTO, photo_message_handler))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(menu_navigation_callback, pattern=r"^nav:.*"))
    application.add_handler(CallbackQueryHandler(signal_callback_handler, pattern=r"^menu:signal$"))
    application.add_handler(CallbackQueryHandler(stats_callback_handler, pattern=r"^menu:stats$"))
    application.add_handler(CallbackQueryHandler(journal_command, pattern=r"^menu:journal$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern=r"^menu:help$"))
    application.add_handler(CallbackQueryHandler(settings_callback_handler, pattern=r"^(menu:settings|set:|save_).*"))
    application.add_handler(CallbackQueryHandler(log_demo_trade_callback, pattern=r"^demo_trade:.*"))
    application.add_handler(CallbackQueryHandler(analyze_callback_handler))

    # Global error handler
    application.add_error_handler(error_handler)
    logger.info("Registered all Telegram handlers successfully.")
