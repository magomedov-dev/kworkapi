"""HTTP-транспорт: единая точка общения с api.kwork.ru.

Все значения подтверждены статическим анализом APK и живым трафиком (см.
docs/01..06). Транспорт:
  * шлёт POST form-urlencoded на {base_url}{method};
  * на каждый запрос ставит заголовок Authorization (статичный ключ приложения);
  * подставляет общие поля token/uad/slrememberme/device;
  * ведёт cookie-jar (slrememberme приходит в Set-Cookie на /signIn);
  * ретраит сеть и 429, разбирает обёртки и поднимает типизированные исключения.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from kworkapi._device import generate_uad
from kworkapi.exceptions import (
    KworkAPIError,
    KworkAuthError,
    KworkError,
    KworkRateLimitError,
)

logger = logging.getLogger("kworkapi.transport")

# Подтверждено: cy/d.java (ServerManager). Для англоязычного сервера — api.kwork.com.
DEFAULT_BASE_URL = "https://api.kwork.ru/"

# Подтверждено: nr/d.java — "Basic " + base64("mobile_api:qFvfRl7w").
# Это статичный ключ клиента-приложения, одинаковый для всех (не пользователь).
APP_AUTHORIZATION = "Basic bW9iaWxlX2FwaTpxRnZmUmw3dw=="

# Метка устройства (поле device). В оригинале — модель телефона; для нас любой ярлык.
DEFAULT_DEVICE = "KworkAPI"

DEFAULT_USER_AGENT = "Apache-HttpClient/UNAVAILABLE (java 1.4)"


class Transport:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        uad: str | None = None,
        device: str = DEFAULT_DEVICE,
        app_authorization: str = APP_AUTHORIZATION,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 20.0,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        min_request_interval: float = 0.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url
        self.uad = uad or generate_uad()
        self.device = device
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        # Минимальный интервал между запросами (троттлинг против анти-бота).
        # 0 = выключено; для боевого использования рекомендуется 0.3–1.0с.
        self.min_request_interval = min_request_interval
        self._throttle_lock = asyncio.Lock()
        self._last_request_at: float | None = None

        headers = {
            "Authorization": app_authorization,
            "User-Agent": user_agent,
        }
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    # --- публичное ------------------------------------------------------

    def current_slrememberme(self) -> str:
        """Текущее значение cookie slrememberme (после /signIn), либо пустая строка."""
        return self._client.cookies.get("slrememberme", "") or ""

    async def call(
        self,
        method: str,
        *,
        data: dict[str, Any] | None = None,
        token: str | None = None,
        auth: bool = True,
        multipart: bool = False,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Вызвать метод API. Возвращает распарсенный JSON-ответ целиком.

        :param method: имя метода (например "signIn") или путь ("api/offer/createoffer").
        :param data: специфичные поля формы.
        :param token: пользовательский токен (для авторизованных запросов).
        :param auth: добавлять ли общие поля авторизации (token/slrememberme).
        :param multipart: слать ли тело как multipart/form-data (нужно части REST-методов).
        :param files: файловые части для загрузки (httpx-формат), включают multipart.
        """
        payload: dict[str, Any] = {k: v for k, v in (data or {}).items() if v is not None}
        payload.setdefault("uad", self.uad)
        payload.setdefault("device", self.device)
        if auth:
            if token:
                payload.setdefault("token", token)
            slr = self.current_slrememberme()
            if slr:
                payload.setdefault("slrememberme", slr)

        # multipart: поля без файлов передаём как части (None, value); реальные файлы — как есть
        post_kwargs: dict[str, Any]
        if files:
            parts = {k: (None, str(v)) for k, v in payload.items()}
            parts.update(files)
            post_kwargs = {"files": parts}
        elif multipart:
            post_kwargs = {"files": {k: (None, str(v)) for k, v in payload.items()}}
        else:
            post_kwargs = {"data": payload}

        path = method.lstrip("/")
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                await self._await_throttle()
                response = await self._client.post(path, **post_kwargs)
            except httpx.TransportError as exc:
                last_exc = exc
                logger.warning("Сеть (%s/%s) %s: %s", attempt, self.max_retries, method, exc)
                await asyncio.sleep(self.retry_backoff * attempt)
                continue

            if response.status_code == 429:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_backoff * attempt * 2)
                    continue
                raise KworkRateLimitError("Превышен лимит запросов (HTTP 429)", code=429)

            if response.status_code == 403:
                # Подтверждено на практике: частые /signIn с одного IP ловят анти-бот.
                raise KworkRateLimitError(
                    "Доступ запрещён (HTTP 403) — вероятно сработал анти-бот/лимит "
                    "(частые входы). Переиспользуйте сессию и uad, добавьте паузу.",
                    code=403,
                )

            return self._parse(method, response)

        raise KworkError(f"Не удалось выполнить запрос {method}: {last_exc}")

    async def _await_throttle(self) -> None:
        """Выдержать минимальный интервал между запросами, если задан."""
        if self.min_request_interval <= 0:
            return
        async with self._throttle_lock:
            now = asyncio.get_running_loop().time()
            if self._last_request_at is not None:
                wait = self.min_request_interval - (now - self._last_request_at)
                if wait > 0:
                    await asyncio.sleep(wait)
                    now = asyncio.get_running_loop().time()
            self._last_request_at = now

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    # --- разбор ответа --------------------------------------------------

    def _parse(self, method: str, response: httpx.Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError as exc:
            raise KworkAPIError(
                f"Не-JSON ответ от {method} (HTTP {response.status_code})",
                code=response.status_code,
                payload=response.text[:500],
            ) from exc

        # Признак ошибки — success=false (часть эндпоинтов поле не возвращает вовсе).
        if isinstance(body, dict) and body.get("success") is False:
            message = str(body.get("error") or body.get("message") or "Ошибка API")
            code = body.get("error_code") or body.get("code")
            if self._looks_like_auth_error(message, code):
                raise KworkAuthError(message, code=code, payload=body)
            raise KworkAPIError(message, code=code, payload=body)

        if response.status_code >= 400:
            raise KworkAPIError(
                f"HTTP {response.status_code} от {method}",
                code=response.status_code,
                payload=body,
            )

        return body

    @staticmethod
    def _looks_like_auth_error(message: str, code: Any) -> bool:
        low = message.lower()
        return any(w in low for w in ("token", "auth", "авториз", "не авторизован", "log in"))
