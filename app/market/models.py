"""
Market data domain models.
Defines Candle, OHLC series, Timeframe, and Market Request models.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
import pandas as pd
from pydantic import BaseModel, Field, field_validator


class Timeframe(str, Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"

    @classmethod
    def from_str(cls, val: str) -> "Timeframe":
        clean = val.strip().upper()
        # Support aliases like 1m, 5m, 15m, 1h
        alias_map = {
            "1M": cls.M1, "M1": cls.M1, "1MIN": cls.M1, "1MINUTE": cls.M1,
            "5M": cls.M5, "M5": cls.M5, "5MIN": cls.M5, "5MINUTES": cls.M5,
            "15M": cls.M15, "M15": cls.M15, "15MIN": cls.M15,
            "30M": cls.M30, "M30": cls.M30, "30MIN": cls.M30,
            "1H": cls.H1, "H1": cls.H1, "60M": cls.H1,
            "4H": cls.H4, "H4": cls.H4,
            "1D": cls.D1, "D1": cls.D1, "DAILY": cls.D1,
        }
        if clean in alias_map:
            return alias_map[clean]
        raise ValueError(f"Unsupported timeframe: {val}. Choose from M1, M5, M15, M30, H1, H4, D1.")


class Candle(BaseModel):
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(default=0.0, ge=0)

    @field_validator("high")
    @classmethod
    def validate_high(cls, v, info):
        # High must be >= open and close
        values = info.data
        if "open" in values and v < values["open"] * 0.9999:
            raise ValueError(f"High ({v}) cannot be substantially lower than Open ({values['open']})")
        return v

    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)

    @property
    def total_range(self) -> float:
        return max(self.high - self.low, 1e-6)

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open

    @property
    def is_bearish(self) -> bool:
        return self.close < self.open


class OHLCData(BaseModel):
    asset: str
    timeframe: Timeframe
    candles: List[Candle] = Field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.candles)

    @property
    def latest_candle(self) -> Optional[Candle]:
        return self.candles[-1] if self.candles else None

    @property
    def latest_close(self) -> float:
        return self.candles[-1].close if self.candles else 0.0

    def to_dataframe(self) -> pd.DataFrame:
        """Convert candle series to Pandas DataFrame indexed by timestamp."""
        if not self.candles:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        data = [
            {
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            }
            for c in self.candles
        ]
        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)
        return df


class AnalysisRequest(BaseModel):
    asset: str
    timeframe: Timeframe = Timeframe.M1
    expiration: str = "1m"
    user_id: Optional[int] = None
