"""
Unit tests for Database, Repositories, and Transparent Statistics.
"""

import pytest
import os
from app.database.database import Database
from app.database.repositories import UserRepository, TradeRepository


@pytest.mark.asyncio
async def test_database_lifecycle(tmp_path):
    db_file = str(tmp_path / "test_bot.db")
    test_db = Database(db_path=db_file)
    await test_db.init_db()

    # Test user creation
    conn = test_db.get_connection()
    with conn:
        conn.execute("INSERT INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)", (99999, "trader_joe", "Joe"))
        row = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (99999,)).fetchone()
        assert row["username"] == "trader_joe"

    # Test trade logging
    with conn:
        conn.execute(
            """INSERT INTO trades (user_id, asset, direction, entry_price, stake, expiration_seconds, outcome)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (99999, "EUR/USD", "CALL", 1.1000, 10.0, 60, "WIN"),
        )
        conn.execute(
            """INSERT INTO trades (user_id, asset, direction, entry_price, stake, expiration_seconds, outcome)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (99999, "EUR/USD", "PUT", 1.1020, 10.0, 60, "LOSS"),
        )
        trades = conn.execute("SELECT * FROM trades WHERE user_id = ?", (99999,)).fetchall()
        assert len(trades) == 2
