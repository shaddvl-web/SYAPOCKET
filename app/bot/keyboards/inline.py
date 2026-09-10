"""
Telegram Inline Keyboard Layouts.
Constructs professional responsive button grids for navigation,
asset selection, timeframes, and expirations.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Main Navigation Menu as specified in Section 18.
    ┌──────────────────────────┐
    │ 📊 ANALYZE MARKET        │
    │ 🎯 SIGNAL                │
    ├──────────────────────────┤
    │ 📈 STRUCTURE             │
    │ 💧 LIQUIDITY             │
    ├──────────────────────────┤
    │ 📉 INDICATORS            │
    │ ⏱ EXPIRATION             │
    ├──────────────────────────┤
    │ 📊 STATISTICS            │
    │ ⚙️ SETTINGS              │
    └──────────────────────────┘
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 ANALYZE MARKET", callback_data="menu:analyze"),
            InlineKeyboardButton("🎯 SIGNAL", callback_data="menu:signal"),
        ],
        [
            InlineKeyboardButton("📈 STRUCTURE", callback_data="menu:structure"),
            InlineKeyboardButton("💧 LIQUIDITY", callback_data="menu:liquidity"),
        ],
        [
            InlineKeyboardButton("📉 INDICATORS", callback_data="menu:indicators"),
            InlineKeyboardButton("⏱ EXPIRATION", callback_data="menu:expiration"),
        ],
        [
            InlineKeyboardButton("📊 STATISTICS", callback_data="menu:stats"),
            InlineKeyboardButton("⚙️ SETTINGS", callback_data="menu:settings"),
        ],
        [
            InlineKeyboardButton("📝 DEMO JOURNAL", callback_data="menu:journal"),
            InlineKeyboardButton("❓ HELP", callback_data="menu:help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_asset_selection_keyboard() -> InlineKeyboardMarkup:
    """Selector for common Forex, Crypto, and Pocket Option Assets."""
    keyboard = [
        [
            InlineKeyboardButton("EUR/USD", callback_data="asset:EUR/USD"),
            InlineKeyboardButton("GBP/USD", callback_data="asset:GBP/USD"),
            InlineKeyboardButton("USD/JPY", callback_data="asset:USD/JPY"),
        ],
        [
            InlineKeyboardButton("AUD/USD", callback_data="asset:AUD/USD"),
            InlineKeyboardButton("USD/CAD", callback_data="asset:USD/CAD"),
            InlineKeyboardButton("EUR/JPY", callback_data="asset:EUR/JPY"),
        ],
        [
            InlineKeyboardButton("BTC/USDT", callback_data="asset:BTC/USDT"),
            InlineKeyboardButton("ETH/USDT", callback_data="asset:ETH/USDT"),
            InlineKeyboardButton("SOL/USDT", callback_data="asset:SOL/USDT"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav:main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_timeframe_keyboard(asset: str) -> InlineKeyboardMarkup:
    """Selector for Timeframes (M1, M5, M15, M30, H1)."""
    keyboard = [
        [
            InlineKeyboardButton("M1 (1 Min)", callback_data=f"tf:{asset}:M1"),
            InlineKeyboardButton("M5 (5 Min)", callback_data=f"tf:{asset}:M5"),
        ],
        [
            InlineKeyboardButton("M15 (15 Min)", callback_data=f"tf:{asset}:M15"),
            InlineKeyboardButton("M30 (30 Min)", callback_data=f"tf:{asset}:M30"),
        ],
        [
            InlineKeyboardButton("H1 (1 Hour)", callback_data=f"tf:{asset}:H1"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Assets", callback_data="menu:analyze"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_expiration_keyboard(asset: str, tf: str) -> InlineKeyboardMarkup:
    """Selector for Pocket Option Expiration Periods."""
    keyboard = [
        [
            InlineKeyboardButton("⏱ 1 Minute", callback_data=f"run:{asset}:{tf}:1m"),
            InlineKeyboardButton("⏱ 2 Minutes", callback_data=f"run:{asset}:{tf}:2m"),
        ],
        [
            InlineKeyboardButton("⏱ 3 Minutes", callback_data=f"run:{asset}:{tf}:3m"),
            InlineKeyboardButton("⏱ 5 Minutes", callback_data=f"run:{asset}:{tf}:5m"),
        ],
        [
            InlineKeyboardButton("⏱ 15 Minutes", callback_data=f"run:{asset}:{tf}:15m"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Timeframes", callback_data=f"asset:{asset}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_analysis_result_keyboard(asset: str, tf: str, exp: str, decision: str) -> InlineKeyboardMarkup:
    """Action buttons after an analysis is completed (re-analyze or demo record)."""
    buttons = []
    if decision in ["CALL", "PUT"]:
        buttons.append([
            InlineKeyboardButton(f"📝 Log Demo {decision}", callback_data=f"demo_trade:{asset}:{decision}:{exp}")
        ])

    buttons.append([
        InlineKeyboardButton("🔄 Re-Analyze", callback_data=f"run:{asset}:{tf}:{exp}"),
        InlineKeyboardButton("💱 Change Asset", callback_data="menu:analyze"),
    ])
    buttons.append([
        InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main_menu")
    ])
    return InlineKeyboardMarkup(buttons)
