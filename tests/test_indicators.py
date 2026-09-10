"""
Unit tests for Vectorized Technical Indicators.
"""

import pytest
from datetime import datetime, timezone
from app.market.models import Candle, OHLCData, Timeframe
from app.analysis.indicators import IndicatorsEngine


@pytest.fixture
def sample_ohlc() -> OHLCData:
    """Generate 50 synthetic test candles with known properties."""
    candles = []
    base_price = 100.0
    for i in range(50):
        o = base_price + i * 0.1
        h = o + 0.5
        l = o - 0.3
        c = o + 0.2
        candles.append(
            Candle(
                timestamp=datetime.fromtimestamp(1700000000 + i * 60, tz=timezone.utc),
                open=o,
                high=h,
                low=l,
                close=c,
                volume=1000.0,
            )
        )
    return OHLCData(asset="TEST", timeframe=Timeframe.M1, candles=candles)


def test_indicators_calculation(sample_ohlc):
    res = IndicatorsEngine.calculate_indicators(sample_ohlc)

    assert "rsi" in res
    assert "macd" in res
    assert "macd_signal" in res
    assert "macd_histogram" in res
    assert "atr" in res
    assert "ema_9" in res
    assert "ema_21" in res
    assert "bb_upper" in res
    assert "bb_lower" in res

    assert 0.0 <= res["rsi"] <= 100.0
    assert res["atr"] > 0.0
    assert res["bb_upper"] > res["bb_lower"]


def test_rsi_overbought_oversold():
    # Construct aggressive monotonic uptrend
    candles = []
    for i in range(30):
        o = 100.0 + i * 2.0
        candles.append(Candle(
            timestamp=datetime.fromtimestamp(1700000000 + i * 60, tz=timezone.utc),
            open=o,
            high=o + 1.5,
            low=o - 0.1,
            close=o + 1.0,
            volume=500.0,
        ))
    ohlc = OHLCData(asset="UP", timeframe=Timeframe.M1, candles=candles)
    res = IndicatorsEngine.calculate_indicators(ohlc)
    assert res["rsi"] > 70.0
