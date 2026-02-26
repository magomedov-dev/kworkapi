"""KworkAPI — неофициальный клиент приватного API kwork.ru."""

from kworkapi.client import KworkClient
from kworkapi.exceptions import (
    KworkAPIError,
    KworkAuthError,
    KworkError,
    KworkRateLimitError,
)

__all__ = [
    "KworkClient",
    "KworkError",
    "KworkAPIError",
    "KworkAuthError",
    "KworkRateLimitError",
]

__version__ = "0.4.0"
