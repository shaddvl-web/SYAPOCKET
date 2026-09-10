"""
Confluence Scoring and Conflict Resolution Engine.
Computes mathematically weighted Confluence Score (0 to 100):
  - Market Structure: 20 pts
  - HTF Bias: 15 pts
  - Support/Resistance: 15 pts
  - Price Action: 15 pts
  - Momentum: 10 pts
  - Liquidity: 10 pts
  - Volatility: 5 pts
  - Candlestick: 5 pts
  - Expiration: 5 pts
Enforces strict conflict detection, late-entry suppression, and signal classification.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from app.analysis.structure import TrendState, StructureAnalysisResult
from app.analysis.support_resistance import SRAnalysisResult
from app.analysis.liquidity import LiquidityAnalysisResult, SweepStatus
from app.analysis.price_action import PriceActionResult, PatternType
from app.analysis.momentum import MomentumAnalysisResult, MomentumState
from app.analysis.volatility import VolatilityResult, VolatilityLevel
from app.analysis.expiration import ExpirationAnalysisResult, ExpirationSuitability


class SignalDecision(str, Enum):
    CALL = "CALL"
    PUT = "PUT"
    NO_TRADE = "NO TRADE"


class QualityRating(str, Enum):
    EXTREME = "EXTREME CONFLUENCE"
    VERY_STRONG = "VERY STRONG"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    NO_TRADE = "NO TRADE"


@dataclass
class ConfluenceScoreResult:
    decision: SignalDecision
    confidence: float  # 0 to 100
    quality: QualityRating
    sub_scores: dict
    bullish_points: float
    bearish_points: float
    conflicts: List[str]
    supporting_reasons: List[str]
    is_late_entry: bool
    is_blocked: bool


class ConfluenceEngine:
    """Rigorous quantitative confluence calculation and gating."""

    MIN_TRADABLE_CONFIDENCE = 70.0

    def evaluate(
        self,
        structure: StructureAnalysisResult,
        sr: SRAnalysisResult,
        liquidity: LiquidityAnalysisResult,
        price_action: PriceActionResult,
        momentum: MomentumAnalysisResult,
        volatility: VolatilityResult,
        expiration: ExpirationAnalysisResult,
        indicators: dict,
        htf_bias: str = "NEUTRAL",
    ) -> ConfluenceScoreResult:
        conflicts: List[str] = []
        bull_reasons: List[str] = []
        bear_reasons: List[str] = []

        sub_scores = {
            "market_structure": 0.0,
            "htf_bias": 0.0,
            "support_resistance": 0.0,
            "price_action": 0.0,
            "momentum": 0.0,
            "liquidity": 0.0,
            "volatility": 0.0,
            "candlestick": 0.0,
            "expiration": 0.0,
        }

        bull_points = 0.0
        bear_points = 0.0

        # -------------------------------------------------------------
        # 1. MARKET STRUCTURE (Max 20 pts)
        # -------------------------------------------------------------
        if structure.trend in [TrendState.STRONG_BULLISH, TrendState.BULLISH]:
            pts = 20.0 if structure.trend == TrendState.STRONG_BULLISH else 15.0
            if structure.bos_confirmed and structure.bos_direction == "BULLISH":
                pts = min(20.0, pts + 5.0)
                bull_reasons.append("Bullish Break of Structure (BOS) confirmed on candle close")
            bull_points += pts
            sub_scores["market_structure"] = pts
            bull_reasons.append(f"{structure.trend.value} market structure ({structure.structure_summary})")

        elif structure.trend in [TrendState.STRONG_BEARISH, TrendState.BEARISH]:
            pts = 20.0 if structure.trend == TrendState.STRONG_BEARISH else 15.0
            if structure.bos_confirmed and structure.bos_direction == "BEARISH":
                pts = min(20.0, pts + 5.0)
                bear_reasons.append("Bearish Break of Structure (BOS) confirmed on candle close")
            bear_points += pts
            sub_scores["market_structure"] = pts
            bear_reasons.append(f"{structure.trend.value} market structure ({structure.structure_summary})")

        else:
            sub_scores["market_structure"] = 5.0
            conflicts.append("Market structure is RANGING or UNCLEAR.")

        # -------------------------------------------------------------
        # 2. HTF BIAS (Max 15 pts)
        # -------------------------------------------------------------
        if htf_bias == "BULLISH":
            bull_points += 15.0
            sub_scores["htf_bias"] = 15.0
            bull_reasons.append("Higher timeframe bias is aligned BULLISH")
            if structure.trend in [TrendState.BEARISH, TrendState.STRONG_BEARISH]:
                conflicts.append("CONFLICT: HTF is BULLISH but LTF structure is BEARISH.")
        elif htf_bias == "BEARISH":
            bear_points += 15.0
            sub_scores["htf_bias"] = 15.0
            bear_reasons.append("Higher timeframe bias is aligned BEARISH")
            if structure.trend in [TrendState.BULLISH, TrendState.STRONG_BULLISH]:
                conflicts.append("CONFLICT: HTF is BEARISH but LTF structure is BULLISH.")
        else:
            # Neutral or single timeframe
            sub_scores["htf_bias"] = 8.0

        # -------------------------------------------------------------
        # 3. SUPPORT / RESISTANCE (Max 15 pts)
        # -------------------------------------------------------------
        # Bullish: price reacted at support, room to resistance
        if sr.nearest_support and sr.distance_to_support_pips < (sr.distance_to_resistance_pips * 0.4):
            pts = 15.0 if not sr.call_blocked_by_resistance else 0.0
            bull_points += pts
            sub_scores["support_resistance"] = pts
            bull_reasons.append(f"Price reacted cleanly from {sr.nearest_support.description}")
        elif sr.nearest_resistance and sr.distance_to_resistance_pips < (sr.distance_to_support_pips * 0.4):
            pts = 15.0 if not sr.put_blocked_by_support else 0.0
            bear_points += pts
            sub_scores["support_resistance"] = pts
            bear_reasons.append(f"Price reacted cleanly from {sr.nearest_resistance.description}")
        else:
            sub_scores["support_resistance"] = 7.0

        # Check blocking
        if sr.call_blocked_by_resistance:
            conflicts.append("CONFLICT: Strong overhead resistance blocks CALL trajectory.")
        if sr.put_blocked_by_support:
            conflicts.append("CONFLICT: Strong underlying support blocks PUT trajectory.")

        # -------------------------------------------------------------
        # 4. PRICE ACTION (Max 15 pts)
        # -------------------------------------------------------------
        if price_action.pattern_bias == "BULLISH":
            pts = 15.0 * price_action.candle_strength
            bull_points += pts
            sub_scores["price_action"] = round(pts, 1)
            bull_reasons.append(f"Price action confirmation: {price_action.primary_pattern.value}")
        elif price_action.pattern_bias == "BEARISH":
            pts = 15.0 * price_action.candle_strength
            bear_points += pts
            sub_scores["price_action"] = round(pts, 1)
            bear_reasons.append(f"Price action confirmation: {price_action.primary_pattern.value}")
        else:
            sub_scores["price_action"] = 5.0

        # -------------------------------------------------------------
        # 5. MOMENTUM (Max 10 pts)
        # -------------------------------------------------------------
        if momentum.state == MomentumState.EXHAUSTED:
            conflicts.append("Momentum is EXHAUSTED (overextended run into extreme RSI/spread).")
            sub_scores["momentum"] = 2.0
        elif momentum.directional_bias == "BULLISH":
            pts = float(momentum.score)
            bull_points += pts
            sub_scores["momentum"] = pts
            bull_reasons.append(f"Bullish momentum acceleration ({momentum.state.value})")
        elif momentum.directional_bias == "BEARISH":
            pts = float(momentum.score)
            bear_points += pts
            sub_scores["momentum"] = pts
            bear_reasons.append(f"Bearish momentum acceleration ({momentum.state.value})")
        else:
            sub_scores["momentum"] = 3.0

        # -------------------------------------------------------------
        # 6. LIQUIDITY (Max 10 pts)
        # -------------------------------------------------------------
        if liquidity.sweep_detected:
            if liquidity.sweep_type == SweepStatus.SELL_SIDE_SWEEP:
                bull_points += 10.0
                sub_scores["liquidity"] = 10.0
                bull_reasons.append("Sell-side liquidity sweep & wick rejection")
            elif liquidity.sweep_type == SweepStatus.BUY_SIDE_SWEEP:
                bear_points += 10.0
                sub_scores["liquidity"] = 10.0
                bear_reasons.append("Buy-side liquidity sweep & wick rejection")
        else:
            sub_scores["liquidity"] = 4.0

        # -------------------------------------------------------------
        # 7. VOLATILITY (Max 5 pts)
        # -------------------------------------------------------------
        if not volatility.is_tradable or volatility.level == VolatilityLevel.EXTREME:
            conflicts.append("EXTREME VOLATILITY: Abnormal spread & slippage risk.")
            sub_scores["volatility"] = 0.0
        elif volatility.level == VolatilityLevel.NORMAL:
            sub_scores["volatility"] = 5.0
            bull_points += 2.5
            bear_points += 2.5
            bull_reasons.append("Normal market volatility")
            bear_reasons.append("Normal market volatility")
        else:
            sub_scores["volatility"] = 3.0

        # -------------------------------------------------------------
        # 8. CANDLESTICK / INDICATOR CONFIRMATION (Max 5 pts)
        # -------------------------------------------------------------
        rsi = indicators.get("rsi", 50.0)
        macd_bullish = indicators.get("macd_bullish", False)

        if macd_bullish and 45.0 <= rsi <= 68.0:
            bull_points += 5.0
            sub_scores["candlestick"] = 5.0
            bull_reasons.append(f"RSI ({rsi:.1f}) & MACD confirm bullish expansion")
        elif not macd_bullish and 32.0 <= rsi <= 55.0:
            bear_points += 5.0
            sub_scores["candlestick"] = 5.0
            bear_reasons.append(f"RSI ({rsi:.1f}) & MACD confirm bearish expansion")
        else:
            sub_scores["candlestick"] = 2.0

        # -------------------------------------------------------------
        # 9. EXPIRATION SUITABILITY (Max 5 pts)
        # -------------------------------------------------------------
        if not expiration.is_compatible:
            conflicts.append(f"Expiration ({expiration.suitability.value}) is incompatible with setup.")
            sub_scores["expiration"] = 1.0
        else:
            sub_scores["expiration"] = float(expiration.score)
            bull_points += expiration.score / 2.0
            bear_points += expiration.score / 2.0
            bull_reasons.append(f"Expiration compatible ({expiration.suitability.value})")
            bear_reasons.append(f"Expiration compatible ({expiration.suitability.value})")

        # -------------------------------------------------------------
        # 10. DECISION & GATEKEEPING
        # -------------------------------------------------------------
        is_blocked = False
        is_late_entry = False

        # Determine raw bias
        if bull_points > bear_points:
            raw_decision = SignalDecision.CALL
            confidence = min(100.0, bull_points)
            reasons = bull_reasons
        else:
            raw_decision = SignalDecision.PUT
            confidence = min(100.0, bear_points)
            reasons = bear_reasons

        # Late entry check: If momentum has already pushed for 4+ bars and distance to target S/R is tiny
        if raw_decision == SignalDecision.CALL and sr.distance_to_resistance_pips < (sr.distance_to_support_pips * 0.2):
            is_late_entry = True
            conflicts.append("LATE ENTRY: Price has already covered the majority of the expansion leg.")
        elif raw_decision == SignalDecision.PUT and sr.distance_to_support_pips < (sr.distance_to_resistance_pips * 0.2):
            is_late_entry = True
            conflicts.append("LATE ENTRY: Price has already covered the majority of the drop.")

        # Hard blocks
        if raw_decision == SignalDecision.CALL and sr.call_blocked_by_resistance:
            is_blocked = True
        if raw_decision == SignalDecision.PUT and sr.put_blocked_by_support:
            is_blocked = True
        if not expiration.is_compatible or not volatility.is_tradable:
            is_blocked = True

        # Conflict penalty
        confidence -= (len(conflicts) * 8.0)
        confidence = max(0.0, min(100.0, confidence))

        # Final Decision Filter
        if confidence < self.MIN_TRADABLE_CONFIDENCE or is_blocked or is_late_entry:
            final_decision = SignalDecision.NO_TRADE
            reasons = conflicts if conflicts else ["Confluence score insufficient for high-probability entry."]
        else:
            final_decision = raw_decision

        # Quality Rating
        if confidence >= 90.0:
            quality = QualityRating.EXTREME
        elif confidence >= 80.0:
            quality = QualityRating.VERY_STRONG
        elif confidence >= 70.0:
            quality = QualityRating.STRONG
        elif confidence >= 60.0:
            quality = QualityRating.MODERATE
        elif confidence >= 50.0:
            quality = QualityRating.WEAK
        else:
            quality = QualityRating.NO_TRADE

        return ConfluenceScoreResult(
            decision=final_decision,
            confidence=round(confidence, 1),
            quality=quality,
            sub_scores=sub_scores,
            bullish_points=round(bull_points, 1),
            bearish_points=round(bear_points, 1),
            conflicts=conflicts,
            supporting_reasons=reasons,
            is_late_entry=is_late_entry,
            is_blocked=is_blocked,
        )
