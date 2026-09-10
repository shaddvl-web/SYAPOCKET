"""
Market Data Router.
Selects best provider based on asset symbol (crypto -> Binance, forex -> TwelveData/Synthetic fallback).
Provides in-memory caching to avoid redundant API hits.
"""

from typing import Dict, Optional, Tuple
import time
from app.config import settings
from app.market.base import MarketDataProvider, MarketDataError, ProviderUnavailableError
from app.market.models import OHLCData, Timeframe
from app.market.providers.binance import BinanceDataProvider
from app.market.providers.twelve_data import TwelveDataProvider
from app.market.providers.synthetic import SyntheticDataProvider
from app.logging_config import logger


class MarketDataRouter:
    """Manages data providers, caching, and fallback policies."""

    def __init__(self):
        self.binance = BinanceDataProvider()
        self.twelve_data = TwelveDataProvider(api_key=settings.TWELVE_DATA_API_KEY)
        self.synthetic = SyntheticDataProvider()
        self._cache: Dict[Tuple[str, str], Tuple[float, OHLCData]] = {}
        self.cache_ttl_seconds = 10  # Cache for 10 seconds to protect rate limits

    def _is_crypto(self, asset: str) -> bool:
        clean = asset.upper().replace("/", "").replace("-", "")
        crypto_keywords = ["BTC", "ETH", "SOL", "USDT", "XRP", "DOGE", "ADA", "BNB", "LTC"]
        return any(k in clean for k in crypto_keywords)

    async def get_ohlc(
        self,
        asset: str,
        timeframe: Timeframe,
        limit: int = 100,
        allow_fallback: bool = True
    ) -> OHLCData:
        """Route request to appropriate provider with caching."""
        cache_key = (asset.upper(), timeframe.value)
        now = time.time()

        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if now - cached_time < self.cache_ttl_seconds:
                return cached_data

        # Select primary provider
        primary_provider: MarketDataProvider
        if self._is_crypto(asset):
            primary_provider = self.binance
        elif settings.TWELVE_DATA_API_KEY:
            primary_provider = self.twelve_data
        else:
            # If no forex key configured, use synthetic deterministic market generator
            primary_provider = self.synthetic

        try:
            ohlc = await primary_provider.get_ohlc(asset, timeframe, limit=limit)
            self._cache[cache_key] = (now, ohlc)
            return ohlc
        except Exception as e:
            logger.warning(f"Primary provider '{primary_provider.name}' failed for {asset}: {e}")
            if allow_fallback and primary_provider != self.synthetic:
                logger.info(f"Flipping to synthetic provider for {asset} to maintain continuity.")
                ohlc = await self.synthetic.get_ohlc(asset, timeframe, limit=limit)
                self._cache[cache_key] = (now, ohlc)
                return ohlc
            raise


# Global data router instance
data_router = MarketDataRouter()
