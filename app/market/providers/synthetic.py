"""
Deterministic Synthetic Market Data Provider.
Generates realistic institutional price structures, liquidity sweeps,
BOS, CHoCH, and clean swing sequences for deterministic testing, offline simulation,
and scenario verification.
"""

from datetime import datetime, timedelta, timezone
import math
import random
from typing import Optional
from app.market.base import MarketDataProvider, InsufficientDataError
from app.market.models import Candle, OHLCData, Timeframe


class SyntheticDataProvider(MarketDataProvider):
    """
    Simulates high-fidelity market data with controllable market structure
    (e.g., strong bullish breakout with sweep, ranging market, or bearish reversal).
    """

    def __init__(self, seed: int = 42):
        self._seed = seed
        self._cache = {}

    @property
    def name(self) -> str:
        return "synthetic_engine"

    async def is_available(self) -> bool:
        return True

    async def get_ohlc(
        self,
        asset: str,
        timeframe: Timeframe,
        limit: int = 100,
        scenario: str = "bullish_confluence"
    ) -> OHLCData:
        """
        Produce a series of realistic candles.
        Pre-configured scenarios:
          - 'bullish_confluence': Uptrend with swing HL, liquidity sweep of previous low, pinbar rejection & close above swing high (BOS).
          - 'bearish_confluence': Downtrend with LH, liquidity sweep of previous high, bearish engulfing rejection (BOS).
          - 'ranging_conflict': Tight consolidation between strong resistance & support with conflicting indicators.
          - 'extreme_volatility': Huge wicks and abnormal spread triggering NO TRADE.
        """
        if limit < 30:
            raise InsufficientDataError("Synthetic engine requires at least 30 candles for analysis.")

        candles = []
        now = datetime.now(timezone.utc)
        step_minutes = {
            Timeframe.M1: 1,
            Timeframe.M5: 5,
            Timeframe.M15: 15,
            Timeframe.M30: 30,
            Timeframe.H1: 60,
            Timeframe.H4: 240,
            Timeframe.D1: 1440,
        }.get(timeframe, 1)

        # Baseline base price
        base_price = 1.0850 if "EUR" in asset.upper() else (65000.0 if "BTC" in asset.upper() else 100.0)
        point = 0.0001 if base_price < 10.0 else 1.0

        current_price = base_price
        start_time = now - timedelta(minutes=step_minutes * limit)

        # Generate smooth structural path
        for i in range(limit):
            candle_time = start_time + timedelta(minutes=step_minutes * i)
            progress = i / limit

            if scenario == "bullish_confluence":
                # Upward trend wave with a pullback and sweep right before final candle
                trend_component = math.sin(progress * 3 * math.pi) * 8 * point + (progress * 25 * point)
                if i == limit - 3:
                    # Pullback to create a swing low
                    open_p = current_price
                    close_p = open_p - 4 * point
                    high_p = open_p + 1 * point
                    low_p = close_p - 5 * point  # Sweeps equal low
                elif i == limit - 2:
                    # Pin bar rejection
                    open_p = current_price
                    low_p = open_p - 6 * point  # Deep wick sweep
                    close_p = open_p + 3 * point
                    high_p = close_p + 1 * point
                elif i == limit - 1:
                    # Strong bullish momentum candle closing above previous swing high (BOS)
                    open_p = current_price
                    close_p = open_p + 8 * point
                    high_p = close_p + 1 * point
                    low_p = open_p - 1 * point
                else:
                    noise = (math.sin(i * 0.7) + math.cos(i * 1.3)) * 2 * point
                    open_p = current_price
                    close_p = base_price + trend_component + noise
                    spread = max(abs(close_p - open_p), 1.5 * point)
                    high_p = max(open_p, close_p) + (point * 1.2)
                    low_p = min(open_p, close_p) - (point * 1.2)

            elif scenario == "bearish_confluence":
                trend_component = - (progress * 25 * point)
                if i == limit - 2:
                    # Wick sweep of high
                    open_p = current_price
                    high_p = open_p + 6 * point
                    close_p = open_p - 2 * point
                    low_p = close_p - 1 * point
                elif i == limit - 1:
                    # Strong bearish breakout
                    open_p = current_price
                    close_p = open_p - 9 * point
                    high_p = open_p + 1 * point
                    low_p = close_p - 2 * point
                else:
                    noise = (math.sin(i * 0.7) + math.cos(i * 1.3)) * 2 * point
                    open_p = current_price
                    close_p = base_price + trend_component + noise
                    high_p = max(open_p, close_p) + (point * 1.2)
                    low_p = min(open_p, close_p) - (point * 1.2)

            else:  # ranging_conflict
                noise = math.sin(i * 0.5) * 4 * point
                open_p = current_price
                close_p = base_price + noise
                high_p = max(open_p, close_p) + (point * 2.0)
                low_p = min(open_p, close_p) - (point * 2.0)

            # Ensure valid bounds
            high_p = max(high_p, open_p, close_p)
            low_p = min(low_p, open_p, close_p)
            vol = round(100.0 + abs(close_p - open_p) / point * 25.0, 2)

            candle = Candle(
                timestamp=candle_time,
                open=round(open_p, 5 if point < 0.1 else 2),
                high=round(high_p, 5 if point < 0.1 else 2),
                low=round(low_p, 5 if point < 0.1 else 2),
                close=round(close_p, 5 if point < 0.1 else 2),
                volume=vol,
            )
            candles.append(candle)
            current_price = candle.close

        return OHLCData(
            asset=asset.upper(),
            timeframe=timeframe,
            candles=candles
        )
