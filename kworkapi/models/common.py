"""Общие модели: пагинация, обложка, продавец, контейнер страницы."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from kworkapi.models.base import KworkModel

T = TypeVar("T")


class Paging(KworkModel):
    """Пагинация (api/common/PagingAPI)."""

    page: int = 1
    total: int = 0
    limit: int = 0
    pages: int = 1


class Cover(KworkModel):
    """Обложка kwork (разные размеры)."""

    phone: str | None = None
    tablet: str | None = None


class Worker(KworkModel):
    """Краткая карточка продавца внутри списков kwork."""

    id: int
    username: str | None = None
    fullname: str | None = None
    profilepicture: str | None = None
    rating: float | str | None = None
    reviews_count: int | None = None
    rating_count: int | None = None
    is_online: bool | None = None
    level_description: str | None = None


@dataclass
class Page(Generic[T]):
    """Страница результатов: элементы + пагинация (+ опц. общее число).

    Поддерживает итерацию (``for x in page``) и ``len(page)``.
    """

    items: list[T]
    paging: Paging | None = None
    total: int | None = None

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def model_dump(self) -> dict[str, Any]:
        """Сериализовать страницу в обычный словарь (для JSON-ответов)."""
        dumped: list[Any] = []
        for item in self.items:
            dump = getattr(item, "model_dump", None)
            dumped.append(dump() if callable(dump) else item)
        return {
            "items": dumped,
            "paging": self.paging.model_dump() if self.paging is not None else None,
            "total": self.total,
        }
