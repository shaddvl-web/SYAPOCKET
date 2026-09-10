"""
Application Entry Point.
Supports running FastAPI Webhook server, Telegram Polling runner, or combined mode.
Windows and Linux compatible.
"""

import argparse
import asyncio
import os
import sys
import uvicorn
from app.config import settings
from app.logging_config import logger
from app.database.database import db
from app.bot.bot import build_bot_app


async def run_polling():
    """Run bot in standalone long-polling mode."""
    logger.info("Initializing SQLite database...")
    await db.init_db()

    app = build_bot_app()
    if not app:
        logger.error("Failed to start bot: TELEGRAM_BOT_TOKEN is missing or invalid in .env.")
        sys.exit(1)

    logger.info("Starting Telegram Bot in Polling Mode...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    logger.info("Bot is active and running. Press Ctrl+C to terminate.")
    # Keep alive
    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Stopping bot polling...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Pocket Option AI Analyzer Bot Entrypoint")
    parser.add_argument(
        "--mode",
        choices=["server", "polling", "both"],
        default=os.environ.get("RUN_MODE", "server"),
        help="Run mode: 'server' (FastAPI + Webhook/Healthcheck), 'polling' (Telegram polling), or 'both'",
    )
    args = parser.parse_args()

    logger.info(f"Starting Pocket Option AI Analyzer in mode: {args.mode}")

    if args.mode == "polling":
        asyncio.run(run_polling())
    else:
        # FastAPI server mode (binds to PORT=3000 or config)
        port = int(os.environ.get("PORT", settings.WEBHOOK_PORT))
        uvicorn.run(
            "app.api.server:api_app",
            host="0.0.0.0",
            port=port,
            log_level="info",
        )


if __name__ == "__main__":
    main()
