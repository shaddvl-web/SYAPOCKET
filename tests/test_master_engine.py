"""
Integration test for AnalysisMasterEngine.
Validates the full multi-engine pipeline from raw OHLC data to decision snapshot.
"""

import pytest
from app.market.models import Timeframe
from app.market.providers.synthetic import SyntheticDataProvider
from app.analysis.engine import AnalysisMasterEngine
from app.analysis.confluence import SignalDecision


@pytest.mark.asyncio
async def test_master_engine_full_pipeline_bullish():
    provider = SyntheticDataProvider(seed=101)
    # Fetch 60 candles with bullish confluence scenario
    ohlc = await provider.get_ohlc("EUR/USD", Timeframe.M1, limit=60, scenario="bullish_confluence")

    engine = AnalysisMasterEngine()
    snapshot = await engine.analyze_market(
        asset="EUR/USD",
        timeframe=Timeframe.M1,
        expiration="1m",
        custom_ohlc=ohlc,
    )

    assert snapshot.asset == "EUR/USD"
    assert snapshot.timeframe == "M1"
    assert snapshot.decision in [SignalDecision.CALL, SignalDecision.PUT, SignalDecision.NO_TRADE]
    assert 0.0 <= snapshot.confidence <= 100.0
    assert len(snapshot.reasons) > 0
    assert snapshot.trend != ""
    assert snapshot.execution_time_ms >= 0.0


@pytest.mark.asyncio
async def test_master_engine_conflict_forces_no_trade():
    provider = SyntheticDataProvider(seed=202)
    # Fetch candles with ranging conflict scenario
    ohlc = await provider.get_ohlc("GBP/USD", Timeframe.M1, limit=50, scenario="ranging_conflict")

    engine = AnalysisMasterEngine()
    snapshot = await engine.analyze_market(
        asset="GBP/USD",
        timeframe=Timeframe.M1,
        expiration="1m",
        custom_ohlc=ohlc,
    )

    # In ranging/conflicting conditions, the system must enforce NO TRADE
    assert snapshot.decision == SignalDecision.NO_TRADE
    assert snapshot.confidence < 70.0
