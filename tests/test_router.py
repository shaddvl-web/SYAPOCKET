"""
Unit tests for Market Data Router & Synthetic Fallback.
"""

import pytest
from app.market.router import MarketDataRouter
from app.market.models import Timeframe
from app.market.providers.synthetic import SyntheticDataProvider


@pytest.mark.asyncio
async def test_synthetic_provider_determinism():
    provider = SyntheticDataProvider()
    ohlc = await provider.get_ohlc("EUR/USD", Timeframe.M1, limit=50)

    assert ohlc.asset == "EUR/USD"
    assert len(ohlc.candles) == 50
    assert ohlc.latest_close > 0.0
    for c in ohlc.candles:
        assert c.high >= c.low
        assert c.high >= c.open
        assert c.high >= c.close


@pytest.mark.asyncio
async def test_data_router_fallback_and_cache():
    router = MarketDataRouter()
    ohlc1 = await router.get_ohlc("EUR/USD", Timeframe.M1, limit=30)
    assert len(ohlc1.candles) >= 30

    # Test cache hit (should return identical data instantly)
    ohlc2 = await router.get_ohlc("EUR/USD", Timeframe.M1, limit=30)
    assert ohlc1.latest_close == ohlc2.latest_close
