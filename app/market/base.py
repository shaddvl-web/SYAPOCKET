"""
Abstract Base Class for Market Data Providers.
Decouples data acquisition from the quantitative analysis engine.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.market.models import Candle, OHLCData, Timeframe


class MarketDataError(Exception):
    """Base exception for all market data errors."""
    pass


class InsufficientDataError(MarketDataError):
    """Raised when available candles are fewer than required for analysis."""
    pass


class ProviderUnavailableError(MarketDataError):
    """Raised when the third-party market provider fails or times out."""
    pass


class SymbolNotFoundError(MarketDataError):
    """Raised when the requested asset is not recognized or supported."""
    pass


class MarketDataProvider(ABC):
    """Abstract interface that all data feed implementations must follow."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the data provider."""
        pass

    @abstractmethod
    async def get_ohlc(
        self,
        asset: str,
        timeframe: Timeframe,
        limit: int = 100
    ) -> OHLCData:
        """
        Fetch historical and real-time OHLC candles for the asset.
        Must return candles sorted chronologically (oldest to newest).
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Health check for provider connectivity."""
        pass
