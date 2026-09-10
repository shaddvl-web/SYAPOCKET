"""Bot middleware package."""
from app.bot.middleware.rate_limit import rate_limiter

__all__ = ["rate_limiter"]
