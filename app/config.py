"""
Application configuration module.
Loads environment variables and validates with Pydantic.
Never exposes sensitive credentials in logs or output.
"""

from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App info
    APP_NAME: str = "Pocket Option AI Analyzer Bot"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"

    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN: str = Field(
        default="MOCK_DEV_TOKEN",
        description="Bot token obtained from @BotFather"
    )

    # Execution Mode: polling | webhook
    BOT_MODE: str = Field(
        default="polling",
        description="'polling' for local development, 'webhook' for production"
    )
    WEBHOOK_URL: str = Field(
        default="",
        description="Public webhook URL when running in webhook mode"
    )
    HOST: str = "0.0.0.0"
    PORT: int = 3000

    # Admin IDs (Telegram chat IDs permitted to run admin commands)
    ADMIN_IDS: str = ""

    # Database
    DATABASE_PATH: str = "data/bot.db"

    # Market Data
    DEFAULT_MARKET_PROVIDER: str = "binance"
    TWELVE_DATA_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MIN: int = 20
    ANALYSIS_COOLDOWN_SECONDS: int = 5

    # Logging
    LOG_LEVEL: str = "INFO"

    # Vision / AI Engine
    GEMINI_API_KEY: str = ""

    @property
    def admin_id_list(self) -> List[int]:
        """Parse comma-separated admin IDs into integer list."""
        if not self.ADMIN_IDS.strip():
            return []
        ids = []
        for item in self.ADMIN_IDS.split(","):
            cleaned = item.strip()
            if cleaned.isdigit():
                ids.append(int(cleaned))
        return ids

    @property
    def db_dir(self) -> Path:
        """Ensure database directory exists."""
        db_path = Path(self.DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path.parent


# Global singleton settings instance
settings = Settings()
