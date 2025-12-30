"""Сериализация ответов библиотеки (pydantic-модели → dict) для FastAPI."""

from __future__ import annotations

from typing import Any


def dump(obj: Any) -> Any:
    """Привести модель/список моделей/dict к JSON-совместимому виду."""
    if isinstance(obj, list):
        return [dump(x) for x in obj]
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj
