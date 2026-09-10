"""
Liquidity Engine.
Detects Equal Highs (EQH), Equal Lows (EQL), Previous Highs/Lows,
Liquidity Sweeps (Wick breach with close rejection), False Breakouts,
and Break & Reverse setups.
Boosts confluence when liquidity is engineered and swept prior to directional moves.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from app.market.models import OHLCData, Candle


class LiquidityType(str, Enum):
    BUY_SIDE_LIQUIDITY = "BUY-SIDE (EQH)"
    SELL_SIDE_LIQUIDITY = "SELL-SIDE (EQL)"
    PREVIOUS_HIGH = "PREVIOUS HIGH"
    PREVIOUS_LOW = "PREVIOUS LOW"


class SweepStatus(str, Enum):
    NO_SWEEP = "NO"
    BUY_SIDE_SWEEP = "BUY-SIDE SWEEP"      # Wick above resistance/EQH, closed below -> Bearish signal
    SELL_SIDE_SWEEP = "SELL-SIDE SWEEP"    # Wick below support/EQL, closed above -> Bullish signal
    FAILED_BREAKOUT = "FAILED BREAKOUT"


@dataclass
class LiquidityPool:
    price: float
    pool_type: LiquidityType
    description: str
    tolerance: float


@dataclass
class LiquidityAnalysisResult:
    sweep_detected: bool
    sweep_type: SweepStatus
    sweep_description: str
    active_pools: List[LiquidityPool]
    rejection_confirmed: bool
    confluence_boost: int  # 0 to 10 points
    details: List[str]


class LiquidityEngine:
    """Quantitative Liquidity and Sweep Detection Engine."""

    def __init__(self, eq_tolerance_atr: float = 0.2):
        self.eq_tolerance_atr = eq_tolerance_atr

    def analyze(self, ohlc: OHLCData, atr: float = 0.001) -> LiquidityAnalysisResult:
        candles = ohlc.candles
        if len(candles) < 15:
            return LiquidityAnalysisResult(
                sweep_detected=False,
                sweep_type=SweepStatus.NO_SWEEP,
                sweep_description="Insufficient data for liquidity analysis.",
                active_pools=[],
                rejection_confirmed=False,
                confluence_boost=0,
                details=[],
            )

        tolerance = atr * self.eq_tolerance_atr
        pools: List[LiquidityPool] = []
        details: List[str] = []

        # 1. Detect Equal Highs (EQH) and Equal Lows (EQL)
        pools.extend(self._find_equal_levels(candles[:-3], tolerance))

        # 2. Previous High and Previous Low in the window
        highest_prev = max(c.high for c in candles[:-3])
        lowest_prev = min(c.low for c in candles[:-3])
        pools.append(LiquidityPool(highest_prev, LiquidityType.PREVIOUS_HIGH, f"Session High at {highest_prev:.5f}", tolerance))
        pools.append(LiquidityPool(lowest_prev, LiquidityType.PREVIOUS_LOW, f"Session Low at {lowest_prev:.5f}", tolerance))

        # 3. Analyze most recent 3 candles for Liquidity Sweeps
        sweep_detected = False
        sweep_type = SweepStatus.NO_SWEEP
        rejection_confirmed = False
        confluence_boost = 0
        sweep_desc = "No liquidity sweep detected."

        recent_window = candles[-3:]
        latest = candles[-1]

        # Check for Sell-Side Sweep (Bullish Reversal):
        # Price wicks below an identified pool or swing low, but closes back above the level
        for pool in pools:
            if pool.pool_type in [LiquidityType.SELL_SIDE_LIQUIDITY, LiquidityType.PREVIOUS_LOW]:
                for c in recent_window:
                    if c.low < pool.price and c.close > pool.price:
                        # Lower wick was deep, close rejected back inside
                        if c.lower_wick > (c.total_range * 0.45):
                            sweep_detected = True
                            sweep_type = SweepStatus.SELL_SIDE_SWEEP
                            rejection_confirmed = True
                            confluence_boost = 10
                            sweep_desc = f"Sell-side liquidity swept at {pool.price:.5f} with strong bullish wick rejection."
                            details.append(sweep_desc)
                            break
            if sweep_detected:
                break

        # If not sell-side, check for Buy-Side Sweep (Bearish Reversal):
        # Price wicks above an identified pool or swing high, but closes back below the level
        if not sweep_detected:
            for pool in pools:
                if pool.pool_type in [LiquidityType.BUY_SIDE_LIQUIDITY, LiquidityType.PREVIOUS_HIGH]:
                    for c in recent_window:
                        if c.high > pool.price and c.close < pool.price:
                            # Upper wick was deep, close rejected back inside
                            if c.upper_wick > (c.total_range * 0.45):
                                sweep_detected = True
                                sweep_type = SweepStatus.BUY_SIDE_SWEEP
                                rejection_confirmed = True
                                confluence_boost = 10
                                sweep_desc = f"Buy-side liquidity swept at {pool.price:.5f} with strong bearish wick rejection."
                                details.append(sweep_desc)
                                break
                if sweep_detected:
                    break

        return LiquidityAnalysisResult(
            sweep_detected=sweep_detected,
            sweep_type=sweep_type,
            sweep_description=sweep_desc,
            active_pools=pools,
            rejection_confirmed=rejection_confirmed,
            confluence_boost=confluence_boost,
            details=details,
        )

    def _find_equal_levels(self, candles: List[Candle], tolerance: float) -> List[LiquidityPool]:
        """Identify double tops/bottoms or equal highs/lows where stop liquidity rests."""
        pools = []
        n = len(candles)
        # Check high pairs
        for i in range(n - 1):
            for j in range(i + 2, min(i + 12, n)):
                c1, c2 = candles[i], candles[j]
                if abs(c1.high - c2.high) <= tolerance:
                    pools.append(
                        LiquidityPool(
                            price=(c1.high + c2.high) / 2.0,
                            pool_type=LiquidityType.BUY_SIDE_LIQUIDITY,
                            description=f"Equal Highs (EQH) at {(c1.high + c2.high)/2.0:.5f}",
                            tolerance=tolerance,
                        )
                    )
                if abs(c1.low - c2.low) <= tolerance:
                    pools.append(
                        LiquidityPool(
                            price=(c1.low + c2.low) / 2.0,
                            pool_type=LiquidityType.SELL_SIDE_LIQUIDITY,
                            description=f"Equal Lows (EQL) at {(c1.low + c2.low)/2.0:.5f}",
                            tolerance=tolerance,
                        )
                    )
        return pools[-6:]
