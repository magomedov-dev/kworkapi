"""Pydantic-модели ответов API.

Модели «мягкие» (extra="allow"): неизвестные поля сохраняются, чтобы клиент не
ломался на изменениях API. Ключевые поля сверены с живым трафиком (docs/06).
"""

from kworkapi.models.base import KworkModel
from kworkapi.models.catalog import Category
from kworkapi.models.common import Cover, Page, Paging, Worker
from kworkapi.models.dialog import Dialog, InboxMessage, LastMessage, SentMessage
from kworkapi.models.exchange import ExchangeInfo, Offer, Project
from kworkapi.models.kwork import Kwork, KworksResult
from kworkapi.models.user import Achievement, Actor, User

__all__ = [
    "KworkModel",
    "Paging",
    "Page",
    "Cover",
    "Worker",
    "Actor",
    "User",
    "Achievement",
    "Kwork",
    "KworksResult",
    "Category",
    "Dialog",
    "InboxMessage",
    "LastMessage",
    "SentMessage",
    "Project",
    "Offer",
    "ExchangeInfo",
]
