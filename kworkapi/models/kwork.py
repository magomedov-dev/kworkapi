"""Модели kwork (услуг) каталога и поиска."""

from __future__ import annotations

from kworkapi.models.base import KworkModel
from kworkapi.models.common import Cover, Worker


class Kwork(KworkModel):
    """Карточка kwork в каталоге/поиске (ответ `/kworks`, `/search`)."""

    id: int
    category_id: int | None = None
    category_name: str | None = None
    status_id: int | None = None
    status_name: str | None = None
    title: str | None = None
    url: str | None = None
    share_url: str | None = None
    image_url: str | None = None
    cover: Cover | None = None
    price: float | None = None
    is_price_from: bool | None = None
    is_best: bool | None = None
    is_hidden: bool | None = None
    is_favorite: bool | None = None
    is_viewed: bool | None = None
    lang: str | None = None
    classifier_id: int | None = None
    worker: Worker | None = None
    badges: list = []


class KworksResult(KworkModel):
    """Список kwork с общим числом (ответ `/kworks`, `/search` в поле response)."""

    kworks_count: int = 0
    kworks: list[Kwork] = []
