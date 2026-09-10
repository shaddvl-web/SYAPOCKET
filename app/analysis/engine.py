"""
Master AI Market Analysis Engine.
Orchestrates all sub-engines:
Structure -> Indicators -> S/R -> Liquidity -> Price Action -> Momentum -> Volatility -> Expiration -> Confluence.
Completely decoupled from Telegram and HTTP layers.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import time
from typing import Dict, List, Optional
from app.market.models import OHLCData, Timeframe, AnalysisRequest
from app.market.router import data_router
from app.analysis.indicators import IndicatorsEngine
from app.analysis.structure import MarketStructureEngine, StructureAnalysisResult
from app.analysis.support_resistance import SupportResistanceEngine, SRAnalysisResult
from app.analysis.liquidity import LiquidityEngine, LiquidityAnalysisResult
from app.analysis.price_action import PriceActionEngine, PriceActionResult
from app.analysis.momentum import MomentumEngine, MomentumAnalysisResult
from app.analysis.volatility import VolatilityEngine, VolatilityResult
from app.analysis.expiration import ExpirationEngine, ExpirationAnalysisResult
from app.analysis.confluence import ConfluenceEngine, ConfluenceScoreResult, SignalDecision
from app.logging_config import log_analysis_event


@dataclass
class MarketAnalysisSnapshot:
    asset: str
    timeframe: str
    expiration: str
    current_price: float
    decision: SignalDecision
    confidence: float
    quality: str
    structure_summary: str
    trend: str
    bos_confirmed: bool
    choch_detected: bool
    liquidity_summary: str
    nearest_support: Optional[float]
    nearest_resistance: Optional[float]
    momentum: str
    rsi: float
    volatility: str
    reasons: List[str]
    conflicts: List[str]
    execution_time_ms: float
    created_at: datetime


class AnalysisMasterEngine:
    """Core Trading & Quantitative Intelligence System."""

    def __init__(self):
        self.structure_engine = MarketStructureEngine()
        self.sr_engine = SupportResistanceEngine()
        self.liquidity_engine = LiquidityEngine()
        self.price_action_engine = PriceActionEngine()
        self.momentum_engine = MomentumEngine()
        self.volatility_engine = VolatilityEngine()
        self.expiration_engine = ExpirationEngine()
        self.confluence_engine = ConfluenceEngine()

    async def analyze_market(
        self,
        asset: str,
        timeframe: Timeframe = Timeframe.M1,
        expiration: str = "1m",
        user_id: Optional[int] = None,
        custom_ohlc: Optional[OHLCData] = None,
    ) -> MarketAnalysisSnapshot:
        start_time = time.perf_counter()

        # 1. Acquire Market Data
        if custom_ohlc:
            ohlc = custom_ohlc
        else:
            ohlc = await data_router.get_ohlc(asset=asset, timeframe=timeframe, limit=100)

        current_price = ohlc.latest_close

        # 2. Vectorized Indicators
        indicators = IndicatorsEngine.calculate_indicators(ohlc)
        atr = indicators.get("atr", 0.001)

        # 3. Market Structure (BOS, CHoCH, HH/HL/LH/LL)
        structure_res = self.structure_engine.analyze(ohlc, atr=atr)

        # 4. Support & Resistance (Key levels, Supply/Demand, Clearance)
        sr_res = self.sr_engine.analyze(ohlc, atr=atr)

        # 5. Liquidity Pools & Sweeps
        liquidity_res = self.liquidity_engine.analyze(ohlc, atr=atr)

        # 6. Price Action & Candlestick Confirmation
        pa_res = self.price_action_engine.analyze(ohlc, atr=atr)

        # 7. Momentum Acceleration & Exhaustion
        momentum_res = self.momentum_engine.analyze(ohlc, indicators)

        # 8. Volatility Condition
        volatility_res = self.volatility_engine.analyze(ohlc, current_atr=atr)

        # 9. Expiration Suitability
        opposing_dist = sr_res.distance_to_resistance_pips if structure_res.trend.name.startswith("BULL") else sr_res.distance_to_support_pips
        expiration_res = self.expiration_engine.analyze(
            timeframe=timeframe,
            expiration_str=expiration,
            atr=atr,
            momentum_state=momentum_res.state.value,
            distance_to_opposing_sr=opposing_dist,
        )

        # 10. Confluence Evaluation & Gating
        confluence_res = self.confluence_engine.evaluate(
            structure=structure_res,
            sr=sr_res,
            liquidity=liquidity_res,
            price_action=pa_res,
            momentum=momentum_res,
            volatility=volatility_res,
            expiration=expiration_res,
            indicators=indicators,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Log event
        log_analysis_event(
            user_id=user_id or 0,
            asset=asset,
            timeframe=timeframe.value,
            decision=confluence_res.decision.value,
            confidence=confluence_res.confidence,
            execution_time_ms=elapsed_ms,
        )

        return MarketAnalysisSnapshot(
            asset=asset.upper(),
            timeframe=timeframe.value,
            expiration=expiration,
            current_price=current_price,
            decision=confluence_res.decision,
            confidence=confluence_res.confidence,
            quality=confluence_res.quality.value,
            structure_summary=structure_res.structure_summary,
            trend=structure_res.trend.value,
            bos_confirmed=structure_res.bos_confirmed,
            choch_detected=structure_res.choch_detected,
            liquidity_summary=liquidity_res.sweep_type.value,
            nearest_support=sr_res.nearest_support.price if sr_res.nearest_support else None,
            nearest_resistance=sr_res.nearest_resistance.price if sr_res.nearest_resistance else None,
            momentum=momentum_res.state.value,
            rsi=indicators.get("rsi", 50.0),
            volatility=volatility_res.level.value,
            reasons=confluence_res.supporting_reasons,
            conflicts=confluence_res.conflicts,
            execution_time_ms=elapsed_ms,
            created_at=datetime.now(timezone.utc),
        )


# Global singleton master analysis engine
master_engine = AnalysisMasterEngine()
