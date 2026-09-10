"""
Market Structure Engine.
Detects Swing Highs, Swing Lows, HH, HL, LH, LL.
Determines Trend: STRONG BULLISH, BULLISH, RANGING, BEARISH, STRONG BEARISH.
Implements Close-Based BOS (Break of Structure) with ATR buffer and CHoCH (Change of Character).
Deterministic and fully testable.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import numpy as np
from app.market.models import OHLCData, Candle


class TrendState(str, Enum):
    STRONG_BULLISH = "STRONG BULLISH"
    BULLISH = "BULLISH"
    RANGING = "RANGING"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG BEARISH"


@dataclass
class SwingPoint:
    index: int
    price: float
    point_type: str  # 'HIGH' or 'LOW'
    label: str       # 'HH', 'LH', 'HL', 'LL'
    candle: Candle


@dataclass
class StructureAnalysisResult:
    trend: TrendState
    structure_summary: str          # e.g., "HH → HL → HH"
    swing_points: List[SwingPoint]
    bos_confirmed: bool             # Break of Structure
    bos_direction: Optional[str]    # 'BULLISH' or 'BEARISH'
    choch_detected: bool            # Change of Character
    choch_direction: Optional[str]  # 'BULLISH' or 'BEARISH'
    last_swing_high: Optional[float]
    last_swing_low: Optional[float]
    details: List[str]


class MarketStructureEngine:
    """Quantitative SMC Market Structure and Fractal Engine."""

    def __init__(self, swing_window: int = 3, atr_multiplier: float = 0.15):
        self.swing_window = swing_window
        self.atr_multiplier = atr_multiplier

    def analyze(self, ohlc: OHLCData, atr: float = 0.001) -> StructureAnalysisResult:
        candles = ohlc.candles
        if len(candles) < (self.swing_window * 2 + 3):
            return StructureAnalysisResult(
                trend=TrendState.RANGING,
                structure_summary="INSUFFICIENT_DATA",
                swing_points=[],
                bos_confirmed=False,
                bos_direction=None,
                choch_detected=False,
                choch_direction=None,
                last_swing_high=None,
                last_swing_low=None,
                details=["Not enough candles to reliably detect swing structures."],
            )

        # 1. Identify raw swing points using fractal rolling window
        swings = self._detect_swings(candles)

        # 2. Label swing points (HH, HL, LH, LL)
        labeled_swings = self._label_swings(swings)

        # 3. Determine overall trend from recent labeled swings
        trend, summary_str = self._determine_trend(labeled_swings)

        # 4. Check BOS and CHoCH on the most recent candles
        bos_confirmed, bos_direction, choch_detected, choch_direction, details = self._evaluate_bos_and_choch(
            candles, labeled_swings, trend, atr
        )

        # Extract last confirmed swing levels
        last_high = next((s.price for s in reversed(labeled_swings) if s.point_type == "HIGH"), None)
        last_low = next((s.price for s in reversed(labeled_swings) if s.point_type == "LOW"), None)

        return StructureAnalysisResult(
            trend=trend,
            structure_summary=summary_str,
            swing_points=labeled_swings,
            bos_confirmed=bos_confirmed,
            bos_direction=bos_direction,
            choch_detected=choch_detected,
            choch_direction=choch_direction,
            last_swing_high=last_high,
            last_swing_low=last_low,
            details=details,
        )

    def _detect_swings(self, candles: List[Candle]) -> List[SwingPoint]:
        """Detect local swing highs and swing lows using centered window."""
        w = self.swing_window
        swings: List[SwingPoint] = []
        n = len(candles)

        for i in range(w, n - w):
            current = candles[i]
            # Check swing high: current high strictly greater than neighbors
            is_high = all(current.high > candles[i - k].high for k in range(1, w + 1)) and \
                      all(current.high >= candles[i + k].high for k in range(1, w + 1))

            # Check swing low: current low strictly less than neighbors
            is_low = all(current.low < candles[i - k].low for k in range(1, w + 1)) and \
                     all(current.low <= candles[i + k].low for k in range(1, w + 1))

            if is_high:
                swings.append(SwingPoint(i, current.high, "HIGH", "H", current))
            elif is_low:
                swings.append(SwingPoint(i, current.low, "LOW", "L", current))

        return swings

    def _label_swings(self, swings: List[SwingPoint]) -> List[SwingPoint]:
        """Classify swings into HH, HL, LH, LL."""
        labeled: List[SwingPoint] = []
        prev_high: Optional[float] = None
        prev_low: Optional[float] = None

        for s in swings:
            if s.point_type == "HIGH":
                if prev_high is None:
                    label = "H"
                elif s.price > prev_high:
                    label = "HH"
                else:
                    label = "LH"
                prev_high = s.price
                labeled.append(SwingPoint(s.index, s.price, s.point_type, label, s.candle))
            elif s.point_type == "LOW":
                if prev_low is None:
                    label = "L"
                elif s.price < prev_low:
                    label = "LL"
                else:
                    label = "HL"
                prev_low = s.price
                labeled.append(SwingPoint(s.index, s.price, s.point_type, label, s.candle))

        return labeled

    def _determine_trend(self, labeled_swings: List[SwingPoint]) -> Tuple[TrendState, str]:
        """Determine trend based on sequence of recent swing highs and lows."""
        if len(labeled_swings) < 3:
            return TrendState.RANGING, "INCIPIENT"

        recent = labeled_swings[-5:]
        labels = [s.label for s in recent]
        summary_str = " → ".join(labels)

        bullish_count = sum(1 for l in labels if l in ["HH", "HL"])
        bearish_count = sum(1 for l in labels if l in ["LH", "LL"])

        # Check last 2 highs and last 2 lows
        highs = [s for s in recent if s.point_type == "HIGH"]
        lows = [s for s in recent if s.point_type == "LOW"]

        hh_sequence = len(highs) >= 2 and highs[-1].price > highs[-2].price
        hl_sequence = len(lows) >= 2 and lows[-1].price > lows[-2].price
        lh_sequence = len(highs) >= 2 and highs[-1].price < highs[-2].price
        ll_sequence = len(lows) >= 2 and lows[-1].price < lows[-2].price

        if hh_sequence and hl_sequence:
            return TrendState.STRONG_BULLISH, summary_str
        elif hh_sequence or (bullish_count >= 3 and bearish_count <= 1):
            return TrendState.BULLISH, summary_str
        elif ll_sequence and lh_sequence:
            return TrendState.STRONG_BEARISH, summary_str
        elif ll_sequence or (bearish_count >= 3 and bullish_count <= 1):
            return TrendState.BEARISH, summary_str
        else:
            return TrendState.RANGING, summary_str

    def _evaluate_bos_and_choch(
        self,
        candles: List[Candle],
        swings: List[SwingPoint],
        trend: TrendState,
        atr: float,
    ) -> Tuple[bool, Optional[str], bool, Optional[str], List[str]]:
        """
        Check for Break of Structure (BOS) and Change of Character (CHoCH).
        MANDATORY RULES:
          1. BOS must be CLOSE-BASED! A wick alone does NOT confirm BOS.
          2. ATR buffer added: close must exceed swing level by at least atr * atr_multiplier.
          3. CHoCH only occurs against an established previous trend.
        """
        details = []
        bos_confirmed = False
        bos_direction = None
        choch_detected = False
        choch_direction = None

        if len(swings) < 2:
            return False, None, False, None, ["Insufficient swing history for BOS/CHoCH."]

        buffer = atr * self.atr_multiplier
        latest_candle = candles[-1]
        prior_candles = candles[-3:]  # Check recent closes

        # Recent swing high and low
        swing_highs = [s for s in swings if s.point_type == "HIGH"]
        swing_lows = [s for s in swings if s.point_type == "LOW"]

        target_high = swing_highs[-1].price if swing_highs else None
        target_low = swing_lows[-1].price if swing_lows else None

        # Check for Bullish breakout above target_high
        if target_high:
            for c in prior_candles:
                # Rule: Close must be strictly greater than target_high + buffer
                if c.close > (target_high + buffer):
                    if trend in [TrendState.BULLISH, TrendState.STRONG_BULLISH, TrendState.RANGING]:
                        bos_confirmed = True
                        bos_direction = "BULLISH"
                        details.append(f"Bullish BOS confirmed by candle close ({c.close:.5f} > {target_high:.5f} + buffer).")
                    elif trend in [TrendState.BEARISH, TrendState.STRONG_BEARISH]:
                        choch_detected = True
                        choch_direction = "BULLISH"
                        details.append(f"Bullish CHoCH detected: Bearish trend interrupted by close above prior high ({target_high:.5f}).")
                    break
                elif c.high > target_high and c.close <= target_high:
                    details.append(f"Wick breakout rejected at {target_high:.5f}. BOS NOT confirmed (wick-only rule enforced).")

        # Check for Bearish breakout below target_low
        if target_low:
            for c in prior_candles:
                if c.close < (target_low - buffer):
                    if trend in [TrendState.BEARISH, TrendState.STRONG_BEARISH, TrendState.RANGING]:
                        bos_confirmed = True
                        bos_direction = "BEARISH"
                        details.append(f"Bearish BOS confirmed by candle close ({c.close:.5f} < {target_low:.5f} - buffer).")
                    elif trend in [TrendState.BULLISH, TrendState.STRONG_BULLISH]:
                        choch_detected = True
                        choch_direction = "BEARISH"
                        details.append(f"Bearish CHoCH detected: Bullish trend broken by close below prior low ({target_low:.5f}).")
                    break
                elif c.low < target_low and c.close >= target_low:
                    details.append(f"Wick penetration below {target_low:.5f} rejected. Bearish BOS NOT confirmed (wick-only rule enforced).")

        return bos_confirmed, bos_direction, choch_detected, choch_direction, details
