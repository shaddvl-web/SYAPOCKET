"""
SQLite Database Initializer and Connection Manager.
Uses SQLite WAL mode for high concurrent throughput.
Provides schema migration and connection utilities.
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import Any, List, Optional, Tuple
from app.config import settings
from app.logging_config import logger


class Database:
    """Async wrapper around SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    async def execute(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE and return lastrowid or affected rows."""
        def _exec():
            with self.get_connection() as conn:
                cur = conn.execute(query, params)
                conn.commit()
                return cur.lastrowid
        return await asyncio.to_thread(_exec)

    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[dict]:
        """Fetch single row as dictionary."""
        def _query():
            with self.get_connection() as conn:
                cur = conn.execute(query, params)
                row = cur.fetchone()
                return dict(row) if row else None
        return await asyncio.to_thread(_query)

    async def fetch_all(self, query: str, params: Tuple = ()) -> List[dict]:
        """Fetch all matching rows as dictionaries."""
        def _query():
            with self.get_connection() as conn:
                cur = conn.execute(query, params)
                return [dict(r) for r in cur.fetchall()]
        return await asyncio.to_thread(_query)

    async def init_db(self):
        """Create all required tables with indexes."""
        def _create_tables():
            with self.get_connection() as conn:
                conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    role TEXT DEFAULT 'USER',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    user_id INTEGER PRIMARY KEY,
                    default_asset TEXT DEFAULT 'EUR/USD',
                    default_timeframe TEXT DEFAULT 'M1',
                    default_expiration TEXT DEFAULT '1m',
                    demo_balance REAL DEFAULT 1000.0,
                    risk_per_trade REAL DEFAULT 10.0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    asset TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    expiration TEXT NOT NULL,
                    current_price REAL,
                    decision TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    quality TEXT,
                    structure_summary TEXT,
                    reasons_json TEXT,
                    conflicts_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER,
                    decision TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    quality TEXT,
                    status TEXT DEFAULT 'ACTIVE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    asset TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stake REAL DEFAULT 10.0,
                    expiration_seconds INTEGER NOT NULL,
                    outcome TEXT DEFAULT 'PENDING',  -- 'WIN', 'LOSS', 'TIE', 'PENDING'
                    payout REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    user_id INTEGER,
                    details_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_analyses_user ON analyses(user_id);
                CREATE INDEX IF NOT EXISTS idx_trades_user ON trades(user_id);
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
                """)
                conn.commit()

        await asyncio.to_thread(_create_tables)
        logger.info(f"Database initialized successfully at {self.db_path}")


# Global database instance
db = Database()
