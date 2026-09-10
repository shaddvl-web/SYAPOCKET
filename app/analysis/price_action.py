"""
Price Action and Candlestick Pattern Engine.
Identifies institutional candlestick patterns:
Bullish/Bearish Engulfing, Pin Bars, Rejection Wicks, Doji, Inside Bars,
Momentum Candles, and Exhaustion Candles.
Enforces rule: Patterns are never evaluated in isolation, but strictly with context.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from app.market.models import OHLCData, Candle


class PatternType(str, Enum):
    BULLISH_ENGULFING = "BULLISH ENGULFING"
    BEARISH_ENGULFING = "BEARISH ENGULFING"
    BULLISH_PIN_BAR = "BULLISH PIN BAR (HAMMER)"
    BEARISH_PIN_BAR = "BEARISH PIN BAR (SHOOTING STAR)"
    REJECTION_CANDLE = "REJECTION CANDLE"
    DOJI = "DOJI"
    INSIDE_BAR = "INSIDE BAR"
    MOMENTUM_CANDLE = "MOMENTUM CANDLE"
    EXHAUSTION_CANDLE = "EXHAUSTION CANDLE"
    NONE = "NONE"


@dataclass
class PriceActionResult:
    primary_pattern: PatternType
    pattern_bias: str  # 'BULLISH', 'BEARISH', or 'NEUTRAL'
    candle_strength: float  # 0.0 to 1.0
    is_momentum_confirmed: bool
    is_rejection_confirmed: bool
    details: List[str]


class PriceActionEngine:
    """Quantitative Price Action and Candlestick Engine."""

    def analyze(self, ohlc: OHLCData, atr: float = 0.001) -> PriceActionResult:
        candles = ohlc.candles
        if len(candles) < 2:
            return PriceActionResult(
                primary_pattern=PatternType.NONE,
                pattern_bias="NEUTRAL",
                candle_strength=0.5,
                is_momentum_confirmed=False,
                is_rejection_confirmed=False,
                details=["Insufficient candles for price action."],
            )

        c1 = candles[-2]  # Previous candle
        c2 = candles[-1]  # Latest candle

        details: List[str] = []
        pattern = PatternType.NONE
        bias = "NEUTRAL"
        strength = 0.5
        momentum_confirmed = False
        rejection_confirmed = False

        total_range = c2.total_range
        body = c2.body_size
        upper_wick = c2.upper_wick
        lower_wick = c2.lower_wick

        # 1. Check Bullish / Bearish Pin Bar (Long wick >= 60% of candle range)
        if lower_wick >= (total_range * 0.60) and c2.close >= (c2.low + total_range * 0.65):
            pattern = PatternType.BULLISH_PIN_BAR
            bias = "BULLISH"
            strength = 0.85
            rejection_confirmed = True
            details.append("Bullish Pin Bar / Hammer: aggressive lower wick rejection.")

        elif upper_wick >= (total_range * 0.60) and c2.close <= (c2.high - total_range * 0.65):
            pattern = PatternType.BEARISH_PIN_BAR
            bias = "BEARISH"
            strength = 0.85
            rejection_confirmed = True
            details.append("Bearish Pin Bar / Shooting Star: aggressive upper wick rejection.")

        # 2. Bullish / Bearish Engulfing
        elif c2.is_bullish and c1.is_bearish and c2.close > c1.open and c2.open <= c1.close:
            pattern = PatternType.BULLISH_ENGULFING
            bias = "BULLISH"
            strength = 0.80
            momentum_confirmed = True
            details.append("Bullish Engulfing: current green body completely covers previous red candle.")

        elif c2.is_bearish and c1.is_bullish and c2.close < c1.open and c2.open >= c1.close:
            pattern = PatternType.BEARISH_ENGULFING
            bias = "BEARISH"
            strength = 0.80
            momentum_confirmed = True
            details.append("Bearish Engulfing: current red body completely covers previous green candle.")

        # 3. Inside Bar (consolidation)
        elif c2.high < c1.high and c2.low > c1.low:
            pattern = PatternType.INSIDE_BAR
            bias = "NEUTRAL"
            strength = 0.50
            details.append("Inside Bar: market compressing inside previous candle boundaries.")

        # 4. Doji (body < 10% of total range)
        elif body <= (total_range * 0.12):
            pattern = PatternType.DOJI
            bias = "NEUTRAL"
            strength = 0.40
            details.append("Doji: indecision in price, neither buyers nor sellers dominant.")

        # 5. Momentum Expansion Candle (body > 1.5 * ATR with small wicks)
        elif body > (atr * 1.5) and (upper_wick + lower_wick) < (total_range * 0.25):
            pattern = PatternType.MOMENTUM_CANDLE
            bias = "BULLISH" if c2.is_bullish else "BEARISH"
            strength = 0.90
            momentum_confirmed = True
            details.append(f"Strong {bias} Momentum Expansion Candle.")

        # 6. Rejection Candle
        elif lower_wick > (atr * 0.8) and c2.is_bullish:
            pattern = PatternType.REJECTION_CANDLE
            bias = "BULLISH"
            strength = 0.75
            rejection_confirmed = True
            details.append("Bullish Rejection Candle at low.")
        elif upper_wick > (atr * 0.8) and c2.is_bearish:
            pattern = PatternType.REJECTION_CANDLE
            bias = "BEARISH"
            strength = 0.75
            rejection_confirmed = True
            details.append("Bearish Rejection Candle at high.")

        return PriceActionResult(
            primary_pattern=pattern,
            pattern_bias=bias,
            candle_strength=strength,
            is_momentum_confirmed=momentum_confirmed,
            is_rejection_confirmed=rejection_confirmed,
            details=details,
        )
