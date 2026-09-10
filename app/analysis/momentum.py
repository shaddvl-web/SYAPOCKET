"""
Momentum Engine.
Analyzes candle velocities, consecutive runs, RSI slopes, MACD acceleration,
and exhaustion signals.
Classifies momentum: STRONG, MODERATE, WEAK, EXHAUSTED.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
from app.market.models import OHLCData, Candle


class MomentumState(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    EXHAUSTED = "EXHAUSTED"


@dataclass
class MomentumAnalysisResult:
    state: MomentumState
    directional_bias: str  # 'BULLISH', 'BEARISH', or 'NEUTRAL'
    consecutive_candles: int
    is_accelerating: bool
    is_exhausted: bool
    score: int  # 0 to 10
    details: List[str]


class MomentumEngine:
    """Quantitative Momentum and Exhaustion Engine."""

    def analyze(self, ohlc: OHLCData, indicators: Dict[str, any]) -> MomentumAnalysisResult:
        candles = ohlc.candles
        if len(candles) < 5:
            return MomentumAnalysisResult(
                state=MomentumState.WEAK,
                directional_bias="NEUTRAL",
                consecutive_candles=0,
                is_accelerating=False,
                is_exhausted=False,
                score=3,
                details=["Insufficient candles to measure momentum."],
            )

        details: List[str] = []
        recent = candles[-5:]

        # 1. Consecutive directional candles
        consecutive = 0
        latest_bullish = candles[-1].is_bullish
        for c in reversed(candles[-6:]):
            if c.is_bullish == latest_bullish:
                consecutive += 1
            else:
                break

        # 2. Acceleration: are body sizes growing or shrinking?
        b1 = candles[-3].body_size
        b2 = candles[-2].body_size
        b3 = candles[-1].body_size
        accelerating = (b3 > b2 > b1) and (b3 > 0.0001)

        # 3. Exhaustion: very extended run with giant candle into extreme RSI or huge opposing wick
        rsi = indicators.get("rsi", 50.0)
        atr = indicators.get("atr", 0.001)
        exhausted = False

        if consecutive >= 4 and ((latest_bullish and rsi > 78) or (not latest_bullish and rsi < 22)):
            exhausted = True
            details.append(f"Momentum exhaustion detected: {consecutive} consecutive candles with extreme RSI ({rsi:.1f}).")
        elif b3 > (2.5 * atr) and (candles[-1].upper_wick > b3 * 0.5 or candles[-1].lower_wick > b3 * 0.5):
            exhausted = True
            details.append("Blow-off exhaustion candle with opposing wick rejection.")

        # 4. Indicator alignment
        macd_expanding = indicators.get("macd_expanding", False)
        macd_bullish = indicators.get("macd_bullish", False)

        direction = "BULLISH" if latest_bullish else "BEARISH"
        score = 5

        if exhausted:
            state = MomentumState.EXHAUSTED
            score = 2
            details.append("State: EXHAUSTED. High risk of immediate mean reversion.")
        elif accelerating and consecutive >= 2:
            state = MomentumState.STRONG
            score = 10
            details.append(f"State: STRONG {direction} acceleration. High candle velocity.")
        elif (latest_bullish and macd_bullish and rsi > 52) or (not latest_bullish and not macd_bullish and rsi < 48):
            state = MomentumState.MODERATE
            score = 7
            details.append(f"State: MODERATE {direction} momentum confirmed by MACD/RSI.")
        else:
            state = MomentumState.WEAK
            score = 4
            details.append("State: WEAK. Choppy candle bodies and conflicting indicators.")

        return MomentumAnalysisResult(
            state=state,
            directional_bias=direction if state != MomentumState.EXHAUSTED else "NEUTRAL",
            consecutive_candles=consecutive,
            is_accelerating=accelerating,
            is_exhausted=exhausted,
            score=score,
            details=details,
        )
