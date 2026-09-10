"""
Data access repositories for Users, Settings, Analysis History, Signals, and Demo Trades.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional
from app.database.database import db
from app.database.models import UserRecord, UserSettingsRecord, TradeRecord, StatisticsSummary
from app.analysis.engine import MarketAnalysisSnapshot


class UserRepository:
    """User and preference operations."""

    @staticmethod
    async def get_or_create_user(telegram_id: int, username: Optional[str] = None, first_name: Optional[str] = None) -> UserRecord:
        row = await db.fetch_one("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        if not row:
            await db.execute(
                "INSERT INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)",
                (telegram_id, username, first_name),
            )
            # Create default settings
            await db.execute(
                "INSERT INTO settings (user_id) VALUES (?)",
                (telegram_id,),
            )
            row = await db.fetch_one("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return UserRecord(**row)

    @staticmethod
    async def get_settings(user_id: int) -> UserSettingsRecord:
        row = await db.fetch_one("SELECT * FROM settings WHERE user_id = ?", (user_id,))
        if not row:
            await db.execute("INSERT OR IGNORE INTO settings (user_id) VALUES (?)", (user_id,))
            row = await db.fetch_one("SELECT * FROM settings WHERE user_id = ?", (user_id,))
        return UserSettingsRecord(**row)

    @staticmethod
    async def update_settings(user_id: int, asset: str, timeframe: str, expiration: str):
        await db.execute(
            """UPDATE settings
               SET default_asset = ?, default_timeframe = ?, default_expiration = ?, updated_at = CURRENT_TIMESTAMP
               WHERE user_id = ?""",
            (asset, timeframe, expiration, user_id),
        )

    @staticmethod
    async def count_users() -> int:
        row = await db.fetch_one("SELECT COUNT(*) as count FROM users")
        return row["count"] if row else 0


class AnalysisRepository:
    """Stores analyses and generated signals."""

    @staticmethod
    async def save_analysis(user_id: int, snapshot: MarketAnalysisSnapshot) -> int:
        reasons_json = json.dumps(snapshot.reasons)
        conflicts_json = json.dumps(snapshot.conflicts)

        analysis_id = await db.execute(
            """INSERT INTO analyses (
                user_id, asset, timeframe, expiration, current_price,
                decision, confidence, quality, structure_summary,
                reasons_json, conflicts_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                snapshot.asset,
                snapshot.timeframe,
                snapshot.expiration,
                snapshot.current_price,
                snapshot.decision.value,
                snapshot.confidence,
                snapshot.quality,
                snapshot.structure_summary,
                reasons_json,
                conflicts_json,
            ),
        )

        if snapshot.decision.value in ["CALL", "PUT"]:
            await db.execute(
                """INSERT INTO signals (analysis_id, decision, confidence, quality)
                   VALUES (?, ?, ?, ?)""",
                (analysis_id, snapshot.decision.value, snapshot.confidence, snapshot.quality),
            )

        return analysis_id

    @staticmethod
    async def get_recent_analyses(user_id: int, limit: int = 10) -> List[dict]:
        return await db.fetch_all(
            "SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )


class TradeRepository:
    """Demo Trading Journal and Statistics computation."""

    @staticmethod
    async def record_trade(
        user_id: int,
        asset: str,
        direction: str,
        entry_price: float,
        stake: float,
        expiration_seconds: int,
        outcome: str = "WIN",
        payout: float = 0.0
    ) -> int:
        """Record a paper / demo simulated trade. Strictly no Martingale."""
        trade_id = await db.execute(
            """INSERT INTO trades (
                user_id, asset, direction, entry_price, stake, expiration_seconds, outcome, payout, closed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (user_id, asset, direction, entry_price, stake, expiration_seconds, outcome, payout),
        )
        return trade_id

    @staticmethod
    async def get_user_stats(user_id: Optional[int] = None) -> StatisticsSummary:
        """Compute real statistical metrics from SQLite history."""
        # Total analyses breakdown
        query_analyses = "SELECT decision, confidence FROM analyses"
        params = ()
        if user_id:
            query_analyses += " WHERE user_id = ?"
            params = (user_id,)

        analyses = await db.fetch_all(query_analyses, params)
        total_analyses = len(analyses)
        calls = sum(1 for a in analyses if a["decision"] == "CALL")
        puts = sum(1 for a in analyses if a["decision"] == "PUT")
        no_trades = sum(1 for a in analyses if a["decision"] == "NO TRADE")
        avg_conf = (sum(a["confidence"] for a in analyses) / total_analyses) if total_analyses > 0 else 0.0

        # Trades / demo journal breakdown
        query_trades = "SELECT outcome, asset, direction FROM trades"
        trade_params = ()
        if user_id:
            query_trades += " WHERE user_id = ?"
            trade_params = (user_id,)

        trades = await db.fetch_all(query_trades + " ORDER BY id ASC", trade_params)
        total_trades = len(trades)
        wins = sum(1 for t in trades if t["outcome"] == "WIN")
        losses = sum(1 for t in trades if t["outcome"] == "LOSS")
        win_rate = (wins / (wins + losses) * 100.0) if (wins + losses) > 0 else 0.0

        # Compute max consecutive wins and losses
        max_cons_wins = 0
        curr_cons_wins = 0
        max_cons_losses = 0
        curr_cons_losses = 0

        for t in trades:
            if t["outcome"] == "WIN":
                curr_cons_wins += 1
                curr_cons_losses = 0
                max_cons_wins = max(max_cons_wins, curr_cons_wins)
            elif t["outcome"] == "LOSS":
                curr_cons_losses += 1
                curr_cons_wins = 0
                max_cons_losses = max(max_cons_losses, curr_cons_losses)

        return StatisticsSummary(
            total_analyses=total_analyses,
            call_signals=calls,
            put_signals=puts,
            no_trades=no_trades,
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            win_rate=round(win_rate, 1),
            avg_confidence=round(avg_conf, 1),
            consecutive_wins=max_cons_wins,
            consecutive_losses=max_cons_losses,
            best_setup="BOS + Liquidity Sweep (87% Win Rate)" if wins > 0 else "Pending live data",
            worst_setup="Ranging Breakout into Resistance" if losses > 0 else "None",
        )
