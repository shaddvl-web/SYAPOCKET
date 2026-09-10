"""
Binance Market Data Provider.
Direct async integration with Binance Public REST API (no API key required for market data).
Supports crypto pairs (BTCUSDT, ETHUSDT, SOLUSDT, EURUSDT, etc.).
"""

from datetime import datetime, timezone
from typing import Optional
import httpx
from app.market.base import MarketDataProvider, MarketDataError, InsufficientDataError, ProviderUnavailableError
from app.market.models import Candle, OHLCData, Timeframe
from app.logging_config import logger


class BinanceDataProvider(MarketDataProvider):
    """Fetches real-time and historical klines from Binance public API."""

    BASE_URL = "https://api.binance.com/api/v3"

    TIMEFRAME_MAP = {
        Timeframe.M1: "1m",
        Timeframe.M5: "5m",
        Timeframe.M15: "15m",
        Timeframe.M30: "30m",
        Timeframe.H1: "1h",
        Timeframe.H4: "4h",
        Timeframe.D1: "1d",
    }

    def __init__(self, timeout: float = 10.0):
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "binance"

    def _normalize_symbol(self, symbol: str) -> str:
        clean = symbol.replace("/", "").replace("-", "").replace("_", "").upper()
        # Common aliases
        if clean in ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE"]:
            clean += "USDT"
        return clean

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.BASE_URL}/ping")
                return res.status_code == 200
        except Exception:
            return False

    async def get_ohlc(
        self,
        asset: str,
        timeframe: Timeframe,
        limit: int = 100
    ) -> OHLCData:
        symbol = self._normalize_symbol(asset)
        interval = self.TIMEFRAME_MAP.get(timeframe, "1m")
        url = f"{self.BASE_URL}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, 1000)
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(url, params=params)

            if resp.status_code == 400:
                # Invalid symbol
                raise MarketDataError(f"Symbol '{asset}' not found on Binance. Check spelling or try synthetic engine.")

            if resp.status_code != 200:
                raise ProviderUnavailableError(f"Binance API returned status {resp.status_code}: {resp.text}")

            raw_data = resp.json()
            if not isinstance(raw_data, list) or len(raw_data) < 10:
                raise InsufficientDataError(f"Binance returned insufficient candles ({len(raw_data)}) for {symbol}")

            candles = []
            for item in raw_data:
                # item: [open_time, open, high, low, close, volume, close_time, ...]
                ts = datetime.fromtimestamp(item[0] / 1000.0, tz=timezone.utc)
                candles.append(
                    Candle(
                        timestamp=ts,
                        open=float(item[1]),
                        high=float(item[2]),
                        low=float(item[3]),
                        close=float(item[4]),
                        volume=float(item[5]),
                    )
                )

            return OHLCData(
                asset=symbol,
                timeframe=timeframe,
                candles=candles
            )

        except (MarketDataError, InsufficientDataError, ProviderUnavailableError):
            raise
        except Exception as e:
            logger.warning(f"Binance API request error for {asset}: {e}")
            raise ProviderUnavailableError(f"Failed to fetch market data from Binance: {str(e)}")
