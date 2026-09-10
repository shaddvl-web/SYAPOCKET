"""
User Settings handlers.
Allows users to configure default trading asset, default timeframe, and default expiration.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.database.repositories import UserRepository
from app.bot.keyboards.inline import get_main_menu_keyboard


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    user = update.effective_user
    if not user:
        return

    settings_record = await UserRepository.get_settings(user.id)

    keyboard = [
        [
            InlineKeyboardButton("💱 Set Default Asset", callback_data="set:asset"),
            InlineKeyboardButton("⏱ Set Default Timeframe", callback_data="set:tf"),
        ],
        [
            InlineKeyboardButton("⌛ Set Default Expiration", callback_data="set:exp"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav:main_menu"),
        ],
    ]

    text = (
        "⚙️ *USER CONFIGURATION & PREFERENCES*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• *Default Asset:* `{settings_record.default_asset}`\n"
        f"• *Default Timeframe:* `{settings_record.default_timeframe}`\n"
        f"• *Default Expiration:* `{settings_record.default_expiration}`\n"
        f"• *Demo Balance:* `${settings_record.demo_balance:.2f}`\n"
        f"• *Risk Per Trade:* `${settings_record.risk_per_trade:.2f}`\n\n"
        "Select a parameter below to adjust:"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def settings_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings button interactions."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    if data == "menu:settings":
        await settings_command(update, context)

    elif data == "set:asset":
        # Quick asset selector
        kb = [
            [InlineKeyboardButton("EUR/USD", callback_data="save_asset:EUR/USD"),
             InlineKeyboardButton("GBP/USD", callback_data="save_asset:GBP/USD")],
            [InlineKeyboardButton("USD/JPY", callback_data="save_asset:USD/JPY"),
             InlineKeyboardButton("BTC/USDT", callback_data="save_asset:BTC/USDT")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu:settings")],
        ]
        await query.edit_message_text(
            "Select your new default asset:",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    elif data.startswith("save_asset:"):
        asset = data.split(":")[1]
        settings_record = await UserRepository.get_settings(user.id)
        await UserRepository.update_settings(
            user.id,
            asset=asset,
            timeframe=settings_record.default_timeframe,
            expiration=settings_record.default_expiration,
        )
        await query.edit_message_text(
            f"✅ Default asset saved as `{asset}`!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    elif data == "set:tf":
        kb = [
            [InlineKeyboardButton("M1", callback_data="save_tf:M1"),
             InlineKeyboardButton("M5", callback_data="save_tf:M5")],
            [InlineKeyboardButton("M15", callback_data="save_tf:M15"),
             InlineKeyboardButton("M30", callback_data="save_tf:M30")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu:settings")],
        ]
        await query.edit_message_text(
            "Select your new default timeframe:",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    elif data.startswith("save_tf:"):
        tf = data.split(":")[1]
        settings_record = await UserRepository.get_settings(user.id)
        await UserRepository.update_settings(
            user.id,
            asset=settings_record.default_asset,
            timeframe=tf,
            expiration=settings_record.default_expiration,
        )
        await query.edit_message_text(
            f"✅ Default timeframe saved as `{tf}`!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    elif data == "set:exp":
        kb = [
            [InlineKeyboardButton("1m", callback_data="save_exp:1m"),
             InlineKeyboardButton("2m", callback_data="save_exp:2m")],
            [InlineKeyboardButton("3m", callback_data="save_exp:3m"),
             InlineKeyboardButton("5m", callback_data="save_exp:5m")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu:settings")],
        ]
        await query.edit_message_text(
            "Select your new default expiration:",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    elif data.startswith("save_exp:"):
        exp = data.split(":")[1]
        settings_record = await UserRepository.get_settings(user.id)
        await UserRepository.update_settings(
            user.id,
            asset=settings_record.default_asset,
            timeframe=settings_record.default_timeframe,
            expiration=exp,
        )
        await query.edit_message_text(
            f"✅ Default expiration saved as `{exp}`!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )
