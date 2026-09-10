"""
Volatility Engine.
Evaluates historical vs. current ATR, spread, and standard deviation.
Classifies volatility: LOW, NORMAL, HIGH, EXTREME.
Extreme volatility automatically penalizes confluence score and triggers caution.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
import numpy as np
from app.market.models import OHLCData


class VolatilityLevel(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


@dataclass
class VolatilityResult:
    level: VolatilityLevel
    current_atr: float
    historical_avg_atr: float
    ratio: float
    is_tradable: bool
    score_penalty: int  # Confluence penalty if extreme
    details: List[str]


class VolatilityEngine:
    """Quantitative Volatility Assessment Engine."""

    def analyze(self, ohlc: OHLCData, current_atr: float) -> VolatilityResult:
        candles = ohlc.candles
        if len(candles) < 20:
            return VolatilityResult(
                level=VolatilityLevel.NORMAL,
                current_atr=current_atr,
                historical_avg_atr=current_atr,
                ratio=1.0,
                is_tradable=True,
                score_penalty=0,
                details=["Default baseline volatility."],
            )

        # Calculate rolling ATR or average candle range over last 30 periods
        ranges = [c.total_range for c in candles[-30:]]
        avg_range = float(np.mean(ranges)) if ranges else current_atr
        ratio = current_atr / max(avg_range, 1e-6)

        details = []
        is_tradable = True
        penalty = 0

        if ratio > 2.2:
            level = VolatilityLevel.EXTREME
            is_tradable = False
            penalty = 25
            details.append(f"EXTREME VOLATILITY: Current ATR ({current_atr:.5f}) is {ratio:.1f}x historical average. Severe whip-saw risk.")
        elif ratio > 1.4:
            level = VolatilityLevel.HIGH
            penalty = 5
            details.append(f"HIGH VOLATILITY: Market moving fast ({ratio:.1f}x average range). Requires wider buffers.")
        elif ratio < 0.6:
            level = VolatilityLevel.LOW
            penalty = 8
            details.append(f"LOW VOLATILITY: Price is stagnant ({ratio:.1f}x average range). High risk of false breakouts.")
        else:
            level = VolatilityLevel.NORMAL
            details.append(f"NORMAL VOLATILITY: Healthy market activity ({ratio:.1f}x baseline). Optimal for fixed-time trading.")

        return VolatilityResult(
            level=level,
            current_atr=current_atr,
            historical_avg_atr=avg_range,
            ratio=round(ratio, 2),
            is_tradable=is_tradable,
            score_penalty=penalty,
            details=details,
        )
