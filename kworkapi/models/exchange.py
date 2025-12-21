"""Модели биржи: проекты (заказы покупателей) и отклики исполнителя."""

from __future__ import annotations

from kworkapi.models.base import KworkModel


class Project(KworkModel):
    """Проект на бирже — заказ покупателя (вложен в Offer, ответы `/projects`)."""

    id: int
    status: str | None = None
    user_id: int | None = None
    username: str | None = None
    profile_picture: str | None = None
    price: float | None = None
    title: str | None = None
    description: str | None = None
    date_create: int | None = None
    offers_count: int | None = None
    category_id: int | None = None


class Offer(KworkModel):
    """Отклик исполнителя на проект (ответ `/offers`)."""

    id: int
    status: str | None = None
    title: str | None = None
    comment: str | None = None
    price: float | None = None
    duration: int | None = None
    date_create: int | None = None
    is_actual: bool | None = None
    is_read: bool | None = None
    want_id: int | None = None
    order_id: int | None = None
    kwork_id: int | None = None
    project: Project | None = None


class ExchangeInfo(KworkModel):
    """Сводка по бирже (ответ `/exchangeInfo`, без обёртки success)."""

    archived_count: int | None = None
    exchange_response_count: int | None = None
