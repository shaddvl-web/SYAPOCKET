"""
Unit tests for Liquidity Engine (EQH, EQL, Sweeps, Wick Rejections).
"""

from datetime import datetime, timezone
from app.market.models import Candle, OHLCData, Timeframe
from app.analysis.liquidity import LiquidityEngine, SweepStatus


def test_liquidity_buy_side_sweep():
    engine = LiquidityEngine()
    now = datetime.now(timezone.utc)

    # 18 candles
    candles = []
    # Base candles around 1.1000
    for i in range(10):
        candles.append(Candle(
            timestamp=now,
            open=1.1000,
            high=1.1010,
            low=1.0990,
            close=1.1000,
            volume=100.0,
        ))

    # Candle 10: Swing high #1 at 1.1050
    candles.append(Candle(timestamp=now, open=1.1000, high=1.1050, low=1.0995, close=1.1020, volume=100))
    # Intervening candle 11 & 12 pullback
    candles.append(Candle(timestamp=now, open=1.1020, high=1.1025, low=1.1000, close=1.1005, volume=100))
    candles.append(Candle(timestamp=now, open=1.1005, high=1.1020, low=1.0998, close=1.1015, volume=100))
    # Candle 13: Swing high #2 at 1.1051 (forms EQH with index 10)
    candles.append(Candle(timestamp=now, open=1.1015, high=1.1051, low=1.1010, close=1.1030, volume=100))
    # Candle 14 pullback
    candles.append(Candle(timestamp=now, open=1.1030, high=1.1035, low=1.1015, close=1.1020, volume=100))
    # Candle 15 sweeps above 1.1050 to 1.1070 with huge upper wick, and closes down at 1.1030
    candles.append(Candle(timestamp=now, open=1.1020, high=1.1070, low=1.1015, close=1.1025, volume=250))

    ohlc = OHLCData(asset="EUR/USD", timeframe=Timeframe.M1, candles=candles)
    res = engine.analyze(ohlc, atr=0.0010)

    assert res.sweep_detected
    assert res.sweep_type == SweepStatus.BUY_SIDE_SWEEP
