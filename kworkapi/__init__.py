"""KworkAPI — неофициальный клиент приватного API kwork.ru."""

from kworkapi.auth import LoginChallenge, Session
from kworkapi.client import KworkClient
from kworkapi.exceptions import (
    KworkAPIError,
    KworkAuthError,
    KworkError,
    KworkRateLimitError,
)

__all__ = [
    "KworkClient",
    "Session",
    "LoginChallenge",
    "KworkError",
    "KworkAPIError",
    "KworkAuthError",
    "KworkRateLimitError",
]

__version__ = "0.6.0"
