"""
Support and Resistance Engine.
Identifies horizontal swing clusters, order block supply/demand zones,
psychological round levels, and calculates price clearance distances.
Classifies levels as WEAK, MODERATE, STRONG, VERY STRONG.
Prevents CALLs into strong overhead resistance and PUTs into strong support.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import numpy as np
from app.market.models import OHLCData, Candle


class LevelStrength(str, Enum):
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY STRONG"


class LevelType(str, Enum):
    SUPPORT = "SUPPORT"
    RESISTANCE = "RESISTANCE"
    PSYCHOLOGICAL = "PSYCHOLOGICAL"
    SUPPLY_ZONE = "SUPPLY"
    DEMAND_ZONE = "DEMAND"


@dataclass
class SRLevel:
    price: float
    level_type: LevelType
    strength: LevelStrength
    touch_count: int
    description: str


@dataclass
class SRAnalysisResult:
    nearest_support: Optional[SRLevel]
    nearest_resistance: Optional[SRLevel]
    distance_to_support_pips: float
    distance_to_resistance_pips: float
    call_blocked_by_resistance: bool
    put_blocked_by_support: bool
    all_levels: List[SRLevel]
    details: List[str]


class SupportResistanceEngine:
    """Quantitative Key Price Level Engine."""

    def __init__(self, cluster_tolerance_atr: float = 0.35, min_clearance_atr: float = 0.4):
        self.cluster_tolerance_atr = cluster_tolerance_atr
        self.min_clearance_atr = min_clearance_atr

    def analyze(self, ohlc: OHLCData, atr: float = 0.001) -> SRAnalysisResult:
        candles = ohlc.candles
        if len(candles) < 10:
            return SRAnalysisResult(
                nearest_support=None,
                nearest_resistance=None,
                distance_to_support_pips=999.0,
                distance_to_resistance_pips=999.0,
                call_blocked_by_resistance=False,
                put_blocked_by_support=False,
                all_levels=[],
                details=["Insufficient data for S/R clustering."],
            )

        current_price = candles[-1].close
        levels: List[SRLevel] = []

        # 1. Collect price pivot points (highs and lows)
        highs = [c.high for c in candles[:-1]]
        lows = [c.low for c in candles[:-1]]

        # Cluster horizontal levels
        tolerance = max(atr * self.cluster_tolerance_atr, 0.0001)
        levels.extend(self._cluster_levels(highs, LevelType.RESISTANCE, tolerance, candles))
        levels.extend(self._cluster_levels(lows, LevelType.SUPPORT, tolerance, candles))

        # 2. Add Psychological Round Numbers
        psych_levels = self._get_psychological_levels(current_price, atr)
        levels.extend(psych_levels)

        # 3. Add Supply and Demand Order Blocks (last opposing candle before strong displacement)
        sd_levels = self._detect_supply_demand(candles, atr)
        levels.extend(sd_levels)

        # 4. Filter levels relative to current price
        supports = [lvl for lvl in levels if lvl.price < current_price]
        resistances = [lvl for lvl in levels if lvl.price > current_price]

        # Find nearest
        nearest_sup = max(supports, key=lambda l: l.price) if supports else None
        nearest_res = min(resistances, key=lambda l: l.price) if resistances else None

        dist_sup = (current_price - nearest_sup.price) if nearest_sup else 999.0
        dist_res = (nearest_res.price - current_price) if nearest_res else 999.0

        # Blocking criteria: If distance to level < min_clearance_atr * atr AND strength is STRONG or VERY_STRONG
        min_clearance = atr * self.min_clearance_atr
        call_blocked = False
        put_blocked = False
        details = []

        if nearest_res and dist_res < min_clearance and nearest_res.strength in [LevelStrength.STRONG, LevelStrength.VERY_STRONG]:
            call_blocked = True
            details.append(f"CALL BLOCKED: Price is directly inside strong resistance at {nearest_res.price:.5f} (clearance: {dist_res:.5f} < {min_clearance:.5f}).")

        if nearest_sup and dist_sup < min_clearance and nearest_sup.strength in [LevelStrength.STRONG, LevelStrength.VERY_STRONG]:
            put_blocked = True
            details.append(f"PUT BLOCKED: Price is directly on strong support at {nearest_sup.price:.5f} (clearance: {dist_sup:.5f} < {min_clearance:.5f}).")

        return SRAnalysisResult(
            nearest_support=nearest_sup,
            nearest_resistance=nearest_res,
            distance_to_support_pips=dist_sup,
            distance_to_resistance_pips=dist_res,
            call_blocked_by_resistance=call_blocked,
            put_blocked_by_support=put_blocked,
            all_levels=levels,
            details=details,
        )

    def _cluster_levels(
        self,
        prices: List[float],
        level_type: LevelType,
        tolerance: float,
        candles: List[Candle]
    ) -> List[SRLevel]:
        clusters: List[List[float]] = []
        for p in sorted(prices):
            placed = False
            for c in clusters:
                if abs(p - np.mean(c)) <= tolerance:
                    c.append(p)
                    placed = True
                    break
            if not placed:
                clusters.append([p])

        levels = []
        for cluster in clusters:
            touch_count = len(cluster)
            avg_price = float(np.mean(cluster))
            if touch_count >= 5:
                strength = LevelStrength.VERY_STRONG
            elif touch_count >= 3:
                strength = LevelStrength.STRONG
            elif touch_count >= 2:
                strength = LevelStrength.MODERATE
            else:
                strength = LevelStrength.WEAK

            levels.append(
                SRLevel(
                    price=avg_price,
                    level_type=level_type,
                    strength=strength,
                    touch_count=touch_count,
                    description=f"{level_type.value} cluster ({touch_count} touches)",
                )
            )
        return levels

    def _get_psychological_levels(self, price: float, atr: float) -> List[SRLevel]:
        """Detect round institutional / psychological round figures (e.g. .000, .500)."""
        levels = []
        if price > 1000:
            # e.g., Crypto BTC
            step = 500.0 if price > 20000 else 100.0
            round_below = (price // step) * step
            round_above = round_below + step
            levels.append(SRLevel(round_below, LevelType.PSYCHOLOGICAL, LevelStrength.MODERATE, 1, f"Psychological Round Level ({round_below:.0f})"))
            levels.append(SRLevel(round_above, LevelType.PSYCHOLOGICAL, LevelStrength.MODERATE, 1, f"Psychological Round Level ({round_above:.0f})"))
        elif price < 10.0:
            # Forex e.g. 1.08500
            step = 0.0050  # 50 pips / round numbers
            round_below = (price // step) * step
            round_above = round_below + step
            levels.append(SRLevel(round_below, LevelType.PSYCHOLOGICAL, LevelStrength.MODERATE, 1, f"Psychological Level ({round_below:.4f})"))
            levels.append(SRLevel(round_above, LevelType.PSYCHOLOGICAL, LevelStrength.MODERATE, 1, f"Psychological Level ({round_above:.4f})"))
        return levels

    def _detect_supply_demand(self, candles: List[Candle], atr: float) -> List[SRLevel]:
        """Identify institutional displacement order blocks."""
        zones = []
        for i in range(len(candles) - 3):
            c1, c2, c3 = candles[i], candles[i + 1], candles[i + 2]
            # Bullish displacement (Demand): c1 is bearish or neutral, followed by explosive bullish expansion
            if c2.is_bullish and c2.body_size > 1.8 * atr and c3.close > c2.high:
                zones.append(
                    SRLevel(
                        price=c1.low,
                        level_type=LevelType.DEMAND_ZONE,
                        strength=LevelStrength.STRONG,
                        touch_count=2,
                        description=f"Institutional Demand Zone at {c1.low:.5f}",
                    )
                )
            # Bearish displacement (Supply): c1 is bullish, followed by sharp drop
            elif c2.is_bearish and c2.body_size > 1.8 * atr and c3.close < c2.low:
                zones.append(
                    SRLevel(
                        price=c1.high,
                        level_type=LevelType.SUPPLY_ZONE,
                        strength=LevelStrength.STRONG,
                        touch_count=2,
                        description=f"Institutional Supply Zone at {c1.high:.5f}",
                    )
                )
        return zones[-4:]  # Keep most recent
