"""Модели каталога: дерево категорий."""

from __future__ import annotations

from kworkapi.models.base import KworkModel


class Category(KworkModel):
    """Категория каталога с вложенными подкатегориями (ответ `/categories`).

    Дерево до 3 уровней: рубрика → категория → подкатегория.
    """

    id: int
    name: str | None = None
    description: str | None = None
    subcategories: list["Category"] = []


Category.model_rebuild()
