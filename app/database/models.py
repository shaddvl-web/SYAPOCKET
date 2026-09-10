"""
Pydantic database schemas and entity transfer models.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserRecord(BaseModel):
    id: Optional[int] = None
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    role: str = "USER"
    created_at: Optional[datetime] = None


class UserSettingsRecord(BaseModel):
    user_id: int
    default_asset: str = "EUR/USD"
    default_timeframe: str = "M1"
    default_expiration: str = "1m"
    demo_balance: float = 1000.0
    risk_per_trade: float = 10.0


class TradeRecord(BaseModel):
    id: Optional[int] = None
    user_id: int
    asset: str
    direction: str  # CALL, PUT
    entry_price: float
    stake: float = 10.0
    expiration_seconds: int = 60
    outcome: str = "PENDING"
    payout: float = 0.0
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class StatisticsSummary(BaseModel):
    total_analyses: int = 0
    call_signals: int = 0
    put_signals: int = 0
    no_trades: int = 0
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    avg_confidence: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    best_setup: str = "N/A"
    worst_setup: str = "N/A"
