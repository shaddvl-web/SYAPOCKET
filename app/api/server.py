"""
FastAPI HTTP & Webhook Application.
Provides:
  - GET /health: Healthcheck endpoint for Docker/Cloud Run
  - GET /status: System & provider telemetry
  - POST /webhook/telegram: Telegram Webhook updates ingestion
  - POST /api/analyze: Direct HTTP endpoint for triggering quantitative market analysis
  - GET /api/stats: System-wide aggregated quantitative statistics
"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from telegram import Update
from app.config import settings
from app.database.database import db
from app.database.repositories import UserRepository, TradeRepository
from app.analysis.engine import master_engine
from app.market.models import Timeframe
from app.bot.bot import build_bot_app
from app.logging_config import logger

telegram_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycles."""
    logger.info("Initializing Pocket Option AI Analyzer System...")
    # Initialize SQLite tables
    await db.init_db()

    global telegram_app
    telegram_app = build_bot_app()
    if telegram_app:
        await telegram_app.initialize()
        await telegram_app.start()
        logger.info("Telegram Application successfully initialized in FastAPI lifespan.")

    yield

    # Teardown
    if telegram_app:
        logger.info("Shutting down Telegram Application...")
        await telegram_app.stop()
        await telegram_app.shutdown()
    logger.info("System shutdown complete.")


api_app = FastAPI(
    title="Pocket Option AI Analyzer API",
    description="Quantitative AI Decision-Support System for Fixed-Time Trading",
    version="1.0.0",
    lifespan=lifespan,
)


class HTTPAnalysisRequest(BaseModel):
    asset: str = "EUR/USD"
    timeframe: str = "M1"
    expiration: str = "1m"
    user_id: Optional[int] = 0


@api_app.get("/health")
async def health_check():
    """Healthcheck endpoint for VPS, Docker, and Cloud Run load balancers."""
    return {
        "status": "ok",
        "service": "pocket-option-ai-analyzer",
        "environment": settings.ENVIRONMENT,
    }


@api_app.get("/status")
async def system_status():
    """Detailed telemetry on components, database, and rate limits."""
    user_count = await UserRepository.count_users()
    return {
        "status": "operational",
        "bot_initialized": telegram_app is not None,
        "database": "sqlite_wal_active",
        "registered_users": user_count,
        "rate_limiting": {
            "requests_per_min": settings.RATE_LIMIT_REQUESTS_PER_MIN,
            "analysis_cooldown_seconds": settings.ANALYSIS_COOLDOWN_SECONDS,
        },
    }


@api_app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Ingest incoming Telegram updates via Webhook."""
    if not telegram_app:
        raise HTTPException(status_code=503, detail="Telegram bot is not initialized.")

    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@api_app.post("/api/analyze")
async def trigger_analysis(req: HTTPAnalysisRequest):
    """
    Direct programmatic API endpoint to trigger full multi-engine market analysis.
    Returns complete breakdown: structure, liquidity, momentum, volatility, confluence.
    """
    try:
        tf = Timeframe.from_str(req.timeframe)
        snapshot = await master_engine.analyze_market(
            asset=req.asset,
            timeframe=tf,
            expiration=req.expiration,
            user_id=req.user_id,
        )
        return {
            "asset": snapshot.asset,
            "timeframe": snapshot.timeframe,
            "expiration": snapshot.expiration,
            "current_price": snapshot.current_price,
            "decision": snapshot.decision.value,
            "confidence": snapshot.confidence,
            "quality": snapshot.quality,
            "market_structure": {
                "summary": snapshot.structure_summary,
                "trend": snapshot.trend,
                "bos_confirmed": snapshot.bos_confirmed,
                "choch_detected": snapshot.choch_detected,
            },
            "liquidity": snapshot.liquidity_summary,
            "support": snapshot.nearest_support,
            "resistance": snapshot.nearest_resistance,
            "momentum": snapshot.momentum,
            "rsi": round(snapshot.rsi, 2),
            "volatility": snapshot.volatility,
            "reasons": snapshot.reasons,
            "conflicts": snapshot.conflicts,
            "execution_time_ms": round(snapshot.execution_time_ms, 2),
        }
    except Exception as e:
        logger.error(f"API analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_app.get("/api/stats")
async def get_system_stats():
    """Retrieve global quantitative trading and analysis statistics."""
    stats = await TradeRepository.get_user_stats(user_id=None)
    return stats.model_dump()
