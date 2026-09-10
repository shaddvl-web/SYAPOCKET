"""
Technical Indicators Engine.
Pure vectorized computation of RSI, MACD, ATR, EMA, SMA, and Bollinger Bands.
Indicators are supporting evidence, not standalone triggers.
"""

from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from app.market.models import OHLCData


class IndicatorsEngine:
    """Calculates all essential technical indicators."""

    @staticmethod
    def calculate_indicators(ohlc: OHLCData) -> Dict[str, any]:
        """
        Computes all indicators over the OHLC series.
        Returns latest values and status summary.
        """
        df = ohlc.to_dataframe()
        if len(df) < 20:
            return {}

        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values

        # 1. RSI (14)
        rsi_series = IndicatorsEngine._compute_rsi(closes, period=14)
        latest_rsi = round(float(rsi_series[-1]), 2) if len(rsi_series) > 0 else 50.0

        # 2. MACD (12, 26, 9)
        macd_line, signal_line, histogram = IndicatorsEngine._compute_macd(closes)
        latest_macd = round(float(macd_line[-1]), 5)
        latest_signal = round(float(signal_line[-1]), 5)
        latest_hist = round(float(histogram[-1]), 5)
        hist_expanding = len(histogram) > 2 and abs(histogram[-1]) > abs(histogram[-2])

        # 3. ATR (14)
        atr_series = IndicatorsEngine._compute_atr(highs, lows, closes, period=14)
        latest_atr = round(float(atr_series[-1]), 5) if len(atr_series) > 0 else 0.001

        # 4. EMAs (9, 21, 50, 200 if sufficient data)
        ema_9 = IndicatorsEngine._compute_ema(closes, 9)[-1]
        ema_21 = IndicatorsEngine._compute_ema(closes, 21)[-1]
        ema_50 = IndicatorsEngine._compute_ema(closes, min(50, len(closes)))[-1]

        # 5. Bollinger Bands (20, 2.0)
        bb_upper, bb_mid, bb_lower = IndicatorsEngine._compute_bollinger(closes, period=20, std_dev=2.0)

        curr_close = closes[-1]
        bb_width = (bb_upper[-1] - bb_lower[-1]) / max(bb_mid[-1], 1e-6)
        bb_percent_b = (curr_close - bb_lower[-1]) / max(bb_upper[-1] - bb_lower[-1], 1e-6)

        return {
            "rsi": latest_rsi,
            "rsi_status": "OVERSOLD" if latest_rsi < 30 else ("OVERBOUGHT" if latest_rsi > 70 else "NEUTRAL"),
            "macd": latest_macd,
            "macd_signal": latest_signal,
            "macd_histogram": latest_hist,
            "macd_bullish": latest_hist > 0 and latest_macd > latest_signal,
            "macd_expanding": hist_expanding,
            "atr": latest_atr,
            "ema_9": round(float(ema_9), 5),
            "ema_21": round(float(ema_21), 5),
            "ema_50": round(float(ema_50), 5),
            "ema_trend": "BULLISH" if ema_9 > ema_21 > ema_50 else ("BEARISH" if ema_9 < ema_21 < ema_50 else "MIXED"),
            "bb_upper": round(float(bb_upper[-1]), 5),
            "bb_middle": round(float(bb_mid[-1]), 5),
            "bb_lower": round(float(bb_lower[-1]), 5),
            "bb_squeeze": bb_width < 0.002,
            "bb_percent_b": round(float(bb_percent_b), 3),
        }

    @staticmethod
    def _compute_rsi(closes: np.ndarray, period: int = 14) -> np.ndarray:
        if len(closes) < period + 1:
            return np.full(len(closes), 50.0)
        deltas = np.diff(closes)
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(closes)
        rsi[:period] = 50.0
        rsi[period] = 100.0 - 100.0 / (1.0 + rs) if down != 0 else 100.0

        up_val = up
        down_val = down
        for i in range(period + 1, len(closes)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.0
            else:
                upval = 0.0
                downval = -delta
            up_val = (up_val * (period - 1) + upval) / period
            down_val = (down_val * (period - 1) + downval) / period
            rs = up_val / down_val if down_val != 0 else 0
            rsi[i] = 100.0 - 100.0 / (1.0 + rs) if down_val != 0 else 100.0
        return rsi

    @staticmethod
    def _compute_ema(series: np.ndarray, period: int) -> np.ndarray:
        if len(series) < period:
            return series
        alpha = 2.0 / (period + 1)
        ema = np.zeros_like(series)
        ema[0] = series[0]
        for i in range(1, len(series)):
            ema[i] = alpha * series[i] + (1 - alpha) * ema[i - 1]
        return ema

    @staticmethod
    def _compute_macd(
        closes: np.ndarray,
        fast: int = 12,
        slow: int = 26,
        signal_period: int = 9
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        ema_fast = IndicatorsEngine._compute_ema(closes, fast)
        ema_slow = IndicatorsEngine._compute_ema(closes, slow)
        macd_line = ema_fast - ema_slow
        signal_line = IndicatorsEngine._compute_ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def _compute_atr(
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        if len(closes) < 2:
            return np.array([0.001])
        tr = np.zeros(len(closes))
        tr[0] = highs[0] - lows[0]
        for i in range(1, len(closes)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i - 1])
            tr3 = abs(lows[i] - closes[i - 1])
            tr[i] = max(tr1, tr2, tr3)
        return IndicatorsEngine._compute_ema(tr, period)

    @staticmethod
    def _compute_bollinger(
        closes: np.ndarray,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        s = pd.Series(closes)
        mid = s.rolling(window=period, min_periods=1).mean().values
        std = s.rolling(window=period, min_periods=1).std().fillna(0).values
        upper = mid + std_dev * std
        lower = mid - std_dev * std
        return upper, mid, lower
