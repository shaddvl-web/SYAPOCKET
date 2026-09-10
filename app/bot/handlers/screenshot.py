"""
Screenshot / Chart Vision handler.
Receives user uploaded chart images, feeds them to the VisionAnalyzer,
and outputs technical SMC breakdowns.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.utils.vision import vision_analyzer
from app.bot.middleware.rate_limit import rate_limiter
from app.bot.keyboards.inline import get_main_menu_keyboard
from app.logging_config import logger


async def photo_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos uploaded by the user."""
    message = update.effective_message
    user = update.effective_user
    if not message or not message.photo or not user:
        return

    allowed, msg = rate_limiter.is_allowed(user.id)
    if not allowed:
        await message.reply_text(msg)
        return

    # Acknowledge immediately
    status_msg = await message.reply_text(
        "🔍 *ANALYZING CHART...*\n"
        "• Examining market structure & swings\n"
        "• Detecting support & resistance zones\n"
        "• Identifying candlestick patterns...",
        parse_mode=ParseMode.MARKDOWN,
    )

    try:
        # Fetch largest available photo file
        photo_obj = message.photo[-1]
        file = await photo_obj.get_file()
        photo_bytes = await file.download_as_bytearray()

        # Run vision analysis
        result = await vision_analyzer.analyze_image_bytes(bytes(photo_bytes))

        if not result.is_valid_chart:
            await status_msg.edit_text(
                "❌ *IMAGE QUALITY TOO LOW / NOT A RECOGNIZED CHART*\n\n"
                "Please upload a clean, uncropped screenshot of your trading chart with candles and price axis clearly visible.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard(),
            )
            return

        formatted_report = (
            "━━━━━━━━━━━━━━━━━━\n"
            "📷 *VISION AI CHART ANALYSIS*\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 *Trend:* {result.trend}\n"
            f"📈 *Structure:* {result.structure}\n"
            f"📍 *Support:* {result.detected_support or 'N/A'}\n"
            f"📍 *Resistance:* {result.detected_resistance or 'N/A'}\n"
            f"💧 *Liquidity:* {result.liquidity_notes}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 *VERDICT:* *{result.setup_verdict}*\n"
            f"Confidence: {result.confidence:.0f}%\n\n"
            f"{result.analysis_text}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "⚠️ _Vision AI provides decision support only. Confirm on your live terminal._\n"
            "━━━━━━━━━━━━━━━━━━"
        )

        await status_msg.edit_text(
            formatted_report,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    except Exception as e:
        logger.error(f"Error analyzing chart screenshot: {e}")
        await status_msg.edit_text(
            f"❌ *Error analyzing chart:* {str(e)}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )
