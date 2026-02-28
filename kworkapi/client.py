"""KworkClient — главная точка входа в библиотеку."""

from __future__ import annotations

from types import TracebackType
from typing import Any

from kworkapi.auth import Auth, LoginChallenge, Session
from kworkapi.exceptions import KworkAuthError
from kworkapi.resources.account import AccountResource
from kworkapi.resources.catalog import CatalogResource
from kworkapi.resources.exchange import ExchangeResource
from kworkapi.resources.files import FilesResource
from kworkapi.resources.kworks import KworksResource
from kworkapi.resources.messages import MessagesResource
from kworkapi.resources.misc import MiscResource
from kworkapi.resources.orders import OrdersResource
from kworkapi.resources.portfolio import PortfolioResource
from kworkapi.resources.search import SearchResource
from kworkapi.resources.tracks import TracksResource
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
        **transport_kwargs: Any,
    ) -> None:
        # uad сессии имеет приоритет: запросы должны идти с тем же идентификатором.
        if session and transport is None and "uad" not in transport_kwargs:
            transport_kwargs["uad"] = session.uad
        self._transport = transport or Transport(**transport_kwargs)
        self._auth = Auth(self._transport)
        self.session = session
        if session and session.slrememberme:
            # вернём cookie, чтобы авторизованные запросы её отправляли
            self._transport.set_cookie("slrememberme", session.slrememberme)

        # Группы методов (ресурсы).
        self.account = AccountResource(self)
        self.catalog = CatalogResource(self)
        self.search = SearchResource(self)
        self.exchange = ExchangeResource(self)
        self.users = UsersResource(self)
        self.kworks = KworksResource(self)
        self.orders = OrdersResource(self)
        self.messages = MessagesResource(self)
        self.files = FilesResource(self)
        self.portfolio = PortfolioResource(self)
        self.tracks = TracksResource(self)
        self.misc = MiscResource(self)

    @classmethod
    def from_session(cls, session: Session, **kwargs: Any) -> KworkClient:
        """Создать клиент из сохранённой сессии (token + uad + slrememberme)."""
        return cls(session=session, **kwargs)

    # --- авторизация -----------------------------------------------------

    async def login(
        self,
        login: str,
        password: str,
        *,
        recaptcha_pass_token: str = "",
    ) -> Session | LoginChallenge:
        """Войти по логину/паролю.

        Возвращает :class:`Session` при успехе или :class:`LoginChallenge`, если
        нужна капча — тогда решите её и вызовите :meth:`solve_captcha`.
        Сохранённый ранее ``recaptcha_pass_token`` подставляется автоматически.
        """
        if not recaptcha_pass_token and self.session:
            recaptcha_pass_token = self.session.recaptcha_pass_token
        result = await self._auth.sign_in(
            login, password, recaptcha_pass_token=recaptcha_pass_token
        )
        if isinstance(result, Session):
            self.session = result
        return result

    async def solve_captcha(self, challenge: LoginChallenge, solution: str) -> Session:
        """Завершить вход решением капчи (``g-recaptcha-response``) и сохранить сессию."""
        self.session = await self._auth.solve_captcha(challenge, solution)
        return self.session

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        *,
        type: str = "worker",
        promocode: str = "",
        recaptcha_response: str = "",
        is_subscribed: int = 0,
    ) -> Session | LoginChallenge:
        """Зарегистрироваться. Возвращает :class:`Session` или :class:`LoginChallenge`."""
        result = await self._auth.sign_up(
            username,
            email,
            password,
            type=type,
            promocode=promocode,
            recaptcha_response=recaptcha_response,
            is_subscribed=is_subscribed,
        )
        if isinstance(result, Session):
            self.session = result
        return result

    async def reset_password(self, email: str, *, recaptcha_response: str = "") -> dict[str, Any]:
        """Запросить сброс пароля письмом (без авторизации)."""
        return await self._auth.reset_password(email, recaptcha_response=recaptcha_response)

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

    async def call(
        self,
        method: str,
        *,
        data: dict[str, Any] | None = None,
        auth: bool = True,
        multipart: bool = False,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Вызвать метод API. При ``auth=True`` требуется активная сессия."""
        token = None
        if auth:
            if not self.is_authenticated:
                raise KworkAuthError(f"Метод {method} требует авторизации — сначала login()")
            assert self.session is not None  # гарантировано is_authenticated
            token = self.session.token
        return await self._transport.call(
            method, data=data, token=token, auth=auth, multipart=multipart, files=files
        )

    # --- управление жизненным циклом ------------------------------------

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> KworkClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()
