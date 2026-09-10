"""
Unit tests for Confluence Engine & Decision Gating.
"""

from app.analysis.confluence import ConfluenceEngine, SignalDecision
from app.analysis.structure import StructureAnalysisResult, TrendState
from app.analysis.support_resistance import SRAnalysisResult, SRLevel, LevelType, LevelStrength
from app.analysis.liquidity import LiquidityAnalysisResult, SweepStatus
from app.analysis.price_action import PriceActionResult, PatternType
from app.analysis.momentum import MomentumAnalysisResult, MomentumState
from app.analysis.volatility import VolatilityResult, VolatilityLevel
from app.analysis.expiration import ExpirationAnalysisResult, ExpirationSuitability


def test_confluence_under_70_forces_no_trade():
    engine = ConfluenceEngine()

    structure = StructureAnalysisResult(
        trend=TrendState.RANGING,
        structure_summary="RANGING (Unclear)",
        swing_points=[],
        bos_confirmed=False,
        bos_direction=None,
        choch_detected=False,
        choch_direction=None,
        last_swing_high=1.1050,
        last_swing_low=1.1000,
        details=[],
    )
    sr = SRAnalysisResult(
        nearest_support=None,
        nearest_resistance=None,
        distance_to_support_pips=100.0,
        distance_to_resistance_pips=100.0,
        call_blocked_by_resistance=False,
        put_blocked_by_support=False,
        all_levels=[],
        details=[],
    )
    liquidity = LiquidityAnalysisResult(
        sweep_detected=False,
        sweep_type=SweepStatus.NO_SWEEP,
        sweep_description="",
        active_pools=[],
        rejection_confirmed=False,
        confluence_boost=0,
        details=[],
    )
    pa = PriceActionResult(
        primary_pattern=PatternType.NONE,
        pattern_bias="NEUTRAL",
        candle_strength=0.5,
        is_momentum_confirmed=False,
        is_rejection_confirmed=False,
        details=[],
    )
    momentum = MomentumAnalysisResult(
        state=MomentumState.WEAK,
        directional_bias="NEUTRAL",
        consecutive_candles=1,
        is_accelerating=False,
        is_exhausted=False,
        score=3,
        details=[],
    )
    volatility = VolatilityResult(
        level=VolatilityLevel.NORMAL,
        current_atr=0.001,
        historical_avg_atr=0.001,
        ratio=1.0,
        is_tradable=True,
        score_penalty=0,
        details=[],
    )
    expiration = ExpirationAnalysisResult(
        suitability=ExpirationSuitability.ACCEPTABLE,
        is_compatible=True,
        recommended_duration="1m",
        expiration_seconds=60,
        score=3,
        details=[],
    )

    res = engine.evaluate(
        structure=structure,
        sr=sr,
        liquidity=liquidity,
        price_action=pa,
        momentum=momentum,
        volatility=volatility,
        expiration=expiration,
        indicators={"rsi": 50.0},
    )

    # Must be gated as NO TRADE because confidence is below 70
    assert res.confidence < 70.0
    assert res.decision == SignalDecision.NO_TRADE


def test_confluence_high_quality_call():
    engine = ConfluenceEngine()

    structure = StructureAnalysisResult(
        trend=TrendState.STRONG_BULLISH,
        structure_summary="STRONG BULLISH (HH -> HL)",
        swing_points=[],
        bos_confirmed=True,
        bos_direction="BULLISH",
        choch_detected=False,
        choch_direction=None,
        last_swing_high=1.1080,
        last_swing_low=1.1000,
        details=[],
    )
    sr = SRAnalysisResult(
        nearest_support=SRLevel(1.1000, LevelType.SUPPORT, LevelStrength.STRONG, 3, "Key Support"),
        nearest_resistance=SRLevel(1.1080, LevelType.RESISTANCE, LevelStrength.MODERATE, 2, "Key Resistance"),
        distance_to_support_pips=5.0,
        distance_to_resistance_pips=75.0,
        call_blocked_by_resistance=False,
        put_blocked_by_support=False,
        all_levels=[],
        details=[],
    )
    liquidity = LiquidityAnalysisResult(
        sweep_detected=True,
        sweep_type=SweepStatus.SELL_SIDE_SWEEP,
        sweep_description="Sell-side sweep",
        active_pools=[],
        rejection_confirmed=True,
        confluence_boost=10,
        details=[],
    )
    pa = PriceActionResult(
        primary_pattern=PatternType.BULLISH_ENGULFING,
        pattern_bias="BULLISH",
        candle_strength=0.9,
        is_momentum_confirmed=True,
        is_rejection_confirmed=True,
        details=[],
    )
    momentum = MomentumAnalysisResult(
        state=MomentumState.STRONG,
        directional_bias="BULLISH",
        consecutive_candles=3,
        is_accelerating=True,
        is_exhausted=False,
        score=9,
        details=[],
    )
    volatility = VolatilityResult(
        level=VolatilityLevel.NORMAL,
        current_atr=0.001,
        historical_avg_atr=0.001,
        ratio=1.0,
        is_tradable=True,
        score_penalty=0,
        details=[],
    )
    expiration = ExpirationAnalysisResult(
        suitability=ExpirationSuitability.GOOD,
        is_compatible=True,
        recommended_duration="1m",
        expiration_seconds=60,
        score=5,
        details=[],
    )

    res = engine.evaluate(
        structure=structure,
        sr=sr,
        liquidity=liquidity,
        price_action=pa,
        momentum=momentum,
        volatility=volatility,
        expiration=expiration,
        indicators={"rsi": 58.0, "macd_bullish": True},
        htf_bias="BULLISH",
    )

    assert res.confidence >= 75.0
    assert res.decision == SignalDecision.CALL
