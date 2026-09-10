"""
Twelve Data Market Provider for Forex, Commodities, and OTC Pairs.
Uses REST API with API key.
"""

from datetime import datetime, timezone
import httpx
from app.market.base import MarketDataProvider, MarketDataError, InsufficientDataError, ProviderUnavailableError
from app.market.models import Candle, OHLCData, Timeframe
from app.logging_config import logger


class TwelveDataProvider(MarketDataProvider):
    """Twelve Data REST API client."""

    BASE_URL = "https://api.twelvedata.com"

    TIMEFRAME_MAP = {
        Timeframe.M1: "1min",
        Timeframe.M5: "5min",
        Timeframe.M15: "15min",
        Timeframe.M30: "30min",
        Timeframe.H1: "1h",
        Timeframe.H4: "4h",
        Timeframe.D1: "1day",
    }

    def __init__(self, api_key: str = "", timeout: float = 10.0):
        self.api_key = api_key
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "twelve_data"

    def _format_symbol(self, symbol: str) -> str:
        s = symbol.strip().upper()
        if "/" not in s and len(s) == 6:
            return f"{s[:3]}/{s[3:]}"
        return s

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def get_ohlc(
        self,
        asset: str,
        timeframe: Timeframe,
        limit: int = 100
    ) -> OHLCData:
        if not self.api_key:
            raise ProviderUnavailableError("Twelve Data API key is missing. Set TWELVE_DATA_API_KEY in .env.")

        symbol = self._format_symbol(asset)
        interval = self.TIMEFRAME_MAP.get(timeframe, "1min")
        url = f"{self.BASE_URL}/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": limit,
            "apikey": self.api_key,
            "order": "ASC",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(url, params=params)

            data = resp.json()
            if "status" in data and data["status"] == "error":
                raise MarketDataError(f"Twelve Data error: {data.get('message', 'Unknown error')}")

            values = data.get("values", [])
            if not values:
                raise InsufficientDataError(f"No candle data returned for {symbol}")

            candles = []
            for item in values:
                # datetime format '2026-09-10 12:30:00'
                dt = datetime.fromisoformat(item["datetime"]).replace(tzinfo=timezone.utc)
                candles.append(
                    Candle(
                        timestamp=dt,
                        open=float(item["open"]),
                        high=float(item["high"]),
                        low=float(item["low"]),
                        close=float(item["close"]),
                        volume=float(item.get("volume", 0.0) or 0.0),
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
            logger.warning(f"TwelveData request error: {e}")
            raise ProviderUnavailableError(f"Twelve Data provider error: {str(e)}")
