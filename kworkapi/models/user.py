"""Модели пользователя: Actor (текущий) и User (чужой профиль)."""

from __future__ import annotations

from kworkapi.models.base import KworkModel


class Achievement(KworkModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    image_url: str | None = None


class Actor(KworkModel):
    """Профиль и состояние текущего пользователя (ответ `/actor`).

    Поля сверены с живым трафиком; неизвестные поля сохраняются (extra=allow).
    """

    id: int
    username: str | None = None
    status: str | None = None
    email: str | None = None
    type: str | None = None  # "worker" | "payer"
    verified: bool | None = None
    profilepicture: str | None = None
    fullname: str | None = None
    description: str | None = None
    location: str | None = None
    rating: float | str | None = None
    rating_count: int | None = None
    good_reviews: int | None = None
    bad_reviews: int | None = None
    # баланс/кошелёк
    hold_amount: float | None = None
    free_amount: float | None = None
    total_amount: float | None = None
    currency: str | None = None
    # счётчики
    unread_dialog_count: int | None = None
    unread_messages_count: int | None = None
    notify_unread_count: int | None = None
    app_notify_count: int | None = None
    kworks_count: int | None = None
    completed_orders_count: int | None = None
    wants_count: int | None = None
    offers_count: int | None = None
    # прочее
    country_id: int | None = None
    city_id: int | None = None
    timezone_id: int | None = None
    addtime: int | None = None
    achievments_list: list[Achievement] | None = None


class User(KworkModel):
    """Публичный профиль пользователя (ответ `/user`, `/userByUsername`)."""

    id: int
    username: str | None = None
    status: str | None = None
    fullname: str | None = None
    profilepicture: str | None = None
    description: str | None = None
    slogan: str | None = None
    location: str | None = None
    rating: float | str | None = None
    rating_count: int | None = None
    reviews_count: int | None = None
    good_reviews: int | None = None
    bad_reviews: int | None = None
    level_description: str | None = None
    online: bool | None = None
    live_date: int | None = None
    cover: str | None = None
    addtime: int | None = None
    completed_orders_count: int | None = None
    kworks_count: int | None = None
    allowedDialog: bool | None = None
    blocked_by_user: bool | None = None
    achievments_list: list[Achievement] | None = None
