"""KworkClient — главная точка входа в библиотеку."""

from __future__ import annotations

from types import TracebackType

from kworkapi.auth import Auth, Session
from kworkapi.exceptions import KworkAuthError
from kworkapi.resources.account import AccountResource
from kworkapi.resources.catalog import CatalogResource
from kworkapi.resources.exchange import ExchangeResource
from kworkapi.resources.messages import MessagesResource
from kworkapi.resources.orders import OrdersResource
from kworkapi.resources.search import SearchResource
from kworkapi.resources.users import UsersResource
from kworkapi.transport import Transport


class KworkClient:
    """Асинхронный клиент приватного API kwork.ru.

    Примеры::

        async with KworkClient() as kw:
            await kw.login("user@example.com", "secret")
            me = await kw.account.me()

        # восстановление ранее сохранённой сессии:
        async with KworkClient.from_session(saved_session) as kw:
            ...
    """

    def __init__(
        self,
        *,
        session: Session | None = None,
        transport: Transport | None = None,
        **transport_kwargs,
    ) -> None:
        # uad сессии имеет приоритет: запросы должны идти с тем же идентификатором.
        if session and transport is None and "uad" not in transport_kwargs:
            transport_kwargs["uad"] = session.uad
        self._transport = transport or Transport(**transport_kwargs)
        self._auth = Auth(self._transport)
        self.session = session
        if session and session.slrememberme:
            # вернём cookie, чтобы авторизованные запросы её отправляли
            self._transport._client.cookies.set("slrememberme", session.slrememberme)

        # Группы методов (ресурсы).
        self.account = AccountResource(self)
        self.catalog = CatalogResource(self)
        self.search = SearchResource(self)
        self.exchange = ExchangeResource(self)
        self.users = UsersResource(self)
        self.orders = OrdersResource(self)
        self.messages = MessagesResource(self)

    @classmethod
    def from_session(cls, session: Session, **kwargs) -> "KworkClient":
        """Создать клиент из сохранённой сессии (token + uad + slrememberme)."""
        return cls(session=session, **kwargs)

    # --- авторизация -----------------------------------------------------

    async def login(
        self,
        login: str,
        password: str,
        *,
        recaptcha_pass_token: str = "",
    ) -> Session:
        """Войти по логину/паролю и сохранить сессию в клиенте."""
        self.session = await self._auth.sign_in(
            login, password, recaptcha_pass_token=recaptcha_pass_token
        )
        return self.session

    async def logout(self, *, push_token: str = "") -> bool:
        """Выйти на сервере и очистить локальную сессию."""
        ok = await self._auth.logout(push_token=push_token)
        self.session = None
        return ok

    @property
    def token(self) -> str | None:
        return self.session.token if self.session else None

    @property
    def is_authenticated(self) -> bool:
        return bool(self.session and self.session.is_authenticated)

    # --- низкоуровневый вызов (используется ресурсами) -------------------

    async def call(self, method: str, *, data: dict | None = None, auth: bool = True) -> dict:
        """Вызвать метод API. При ``auth=True`` требуется активная сессия."""
        token = None
        if auth:
            if not self.is_authenticated:
                raise KworkAuthError(f"Метод {method} требует авторизации — сначала login()")
            token = self.session.token
        return await self._transport.call(method, data=data, token=token, auth=auth)

    # --- управление жизненным циклом ------------------------------------

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> "KworkClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()
