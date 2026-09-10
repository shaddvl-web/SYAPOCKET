"""
Unit tests for Market Structure Engine (SMC, Swing detection, BOS, CHoCH).
"""

from datetime import datetime, timezone
from app.market.models import Candle, OHLCData, Timeframe
from app.analysis.structure import MarketStructureEngine, TrendState


def test_structure_close_based_bos_bullish():
    engine = MarketStructureEngine(swing_window=2)
    now = datetime.now(timezone.utc)

    candles = [
        # Base swing high around 105.0
        Candle(timestamp=now, open=100.0, high=102.0, low=99.0, close=101.0, volume=100.0),
        Candle(timestamp=now, open=101.0, high=102.5, low=100.0, close=102.0, volume=100.0),
        Candle(timestamp=now, open=102.0, high=105.0, low=101.0, close=103.0, volume=100.0),
        Candle(timestamp=now, open=103.0, high=103.5, low=98.0, close=99.0, volume=100.0),
        Candle(timestamp=now, open=99.0, high=100.0, low=98.0, close=99.5, volume=100.0),
        # Candle only wicking above 105.0 to 105.5 but closing at 104.0 -> NOT A BOS
        Candle(timestamp=now, open=99.5, high=105.5, low=98.5, close=104.0, volume=100.0),
    ]
    ohlc = OHLCData(asset="EUR/USD", timeframe=Timeframe.M1, candles=candles)
    res = engine.analyze(ohlc, atr=0.5)
    # Wick alone must NOT confirm BOS
    assert not res.bos_confirmed

    # Now add candle that actually CLOSES clearly above 105.0 + buffer
    candles.append(Candle(
        timestamp=now, open=104.0, high=107.0, low=103.5, close=106.8, volume=200.0
    ))
    ohlc2 = OHLCData(asset="EUR/USD", timeframe=Timeframe.M1, candles=candles)
    res2 = engine.analyze(ohlc2, atr=0.5)
    assert res2.bos_confirmed
    assert res2.bos_direction == "BULLISH"
