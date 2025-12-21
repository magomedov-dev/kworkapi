"""Общие модели: пагинация, обложка, продавец, контейнер страницы."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

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


class Page(BaseModel, Generic[T]):
    """Страница результатов: элементы + пагинация (+ опц. общее число)."""

    items: list[T]
    paging: Paging | None = None
    total: int | None = None

    def __iter__(self):  # удобный обход элементов
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)
