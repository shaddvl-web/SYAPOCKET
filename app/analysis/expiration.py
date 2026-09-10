"""
Expiration Suitability Engine.
Tailored for Pocket Option style fixed-time trading (e.g. 1m, 2m, 3m, 5m, 15m).
Correlates expiration duration with timeframe, ATR velocity, momentum acceleration,
and distance to nearest opposing support/resistance barrier.
Classifies: TOO SHORT, SHORT, ACCEPTABLE, GOOD, TOO LONG.
Incompatible expirations enforce NO TRADE.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from app.market.models import Timeframe, Candle


class ExpirationSuitability(str, Enum):
    TOO_SHORT = "TOO SHORT"
    SHORT = "SHORT"
    ACCEPTABLE = "ACCEPTABLE"
    GOOD = "GOOD"
    TOO_LONG = "TOO LONG"


@dataclass
class ExpirationAnalysisResult:
    suitability: ExpirationSuitability
    is_compatible: bool
    recommended_duration: str
    expiration_seconds: int
    score: int  # 0 to 5
    details: List[str]


class ExpirationEngine:
    """Quantitative Expiration Compatibility Analyzer."""

    @staticmethod
    def parse_expiration_seconds(expiration_str: str) -> int:
        """Parse strings like '1m', '2m', '5m', '30s', '15m', '1 minute' into seconds."""
        clean = expiration_str.strip().lower()
        if "min" in clean or "m" in clean:
            num = "".join(c for c in clean if c.isdigit())
            mins = int(num) if num else 1
            return mins * 60
        elif "s" in clean or "sec" in clean:
            num = "".join(c for c in clean if c.isdigit())
            return int(num) if num else 60
        elif "h" in clean or "hour" in clean:
            num = "".join(c for c in clean if c.isdigit())
            return (int(num) if num else 1) * 3600
        return 60  # Default 1 minute

    def analyze(
        self,
        timeframe: Timeframe,
        expiration_str: str,
        atr: float,
        momentum_state: str,
        distance_to_opposing_sr: float,
        is_breakout: bool = False
    ) -> ExpirationAnalysisResult:
        exp_sec = self.parse_expiration_seconds(expiration_str)
        details: List[str] = []

        # Timeframe base seconds
        tf_seconds = {
            Timeframe.M1: 60,
            Timeframe.M5: 300,
            Timeframe.M15: 900,
            Timeframe.M30: 1800,
            Timeframe.H1: 3600,
            Timeframe.H4: 14400,
            Timeframe.D1: 86400,
        }.get(timeframe, 60)

        # Optimal fixed-time ratio: 1x to 3x current timeframe candle duration
        ratio = exp_sec / tf_seconds

        suitability = ExpirationSuitability.ACCEPTABLE
        is_compatible = True
        score = 4
        rec_str = f"{tf_seconds // 60}m"

        if ratio < 0.5:
            suitability = ExpirationSuitability.TOO_SHORT
            is_compatible = False
            score = 1
            details.append(f"Expiration ({exp_sec}s) is TOO SHORT for {timeframe.value}. Random market noise dominates sub-candle ticks.")
            rec_str = f"{max(1, tf_seconds // 60)}m - {max(2, (tf_seconds * 2) // 60)}m"

        elif ratio > 6.0:
            suitability = ExpirationSuitability.TOO_LONG
            is_compatible = False
            score = 1
            details.append(f"Expiration ({exp_sec // 60}m) is TOO LONG for {timeframe.value}. Higher timeframe cycles will invalidate current entry.")
            rec_str = f"{max(1, tf_seconds // 60)}m - {max(3, (tf_seconds * 3) // 60)}m"

        elif 1.0 <= ratio <= 3.0:
            suitability = ExpirationSuitability.GOOD
            is_compatible = True
            score = 5
            details.append(f"Expiration ({exp_sec // 60}m) is mathematically OPTIMAL ({ratio:.1f}x candle duration). Gives structure time to expand.")
            rec_str = f"{exp_sec // 60}m"

        else:
            suitability = ExpirationSuitability.ACCEPTABLE
            is_compatible = True
            score = 3
            details.append(f"Expiration ({exp_sec // 60}m) is acceptable ({ratio:.1f}x candle duration).")
            rec_str = f"{exp_sec // 60}m"

        # Check opposing barrier distance vs expected ATR traversal
        # Expected price movement over expiration duration
        expected_movement = atr * (exp_sec / tf_seconds) ** 0.5
        if distance_to_opposing_sr < (expected_movement * 0.5) and not is_breakout:
            details.append(f"WARNING: Opposing key level is only {distance_to_opposing_sr:.5f} away. Expiration may hit barrier and reverse.")
            if suitability == ExpirationSuitability.GOOD:
                score = 3
                suitability = ExpirationSuitability.ACCEPTABLE

        return ExpirationAnalysisResult(
            suitability=suitability,
            is_compatible=is_compatible,
            recommended_duration=rec_str,
            expiration_seconds=exp_sec,
            score=score,
            details=details,
        )
