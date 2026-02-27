"""Авторизация и состояние сессии.

Подтверждено живым трафиком:
  POST /signIn  (login, password, recaptcha_pass_token?, uad, device) + заголовок Authorization
  → {"success": true, "response": {"token": "...", "expired": 31536000, "need_2fa": false}}

`slrememberme` приходит в Set-Cookie ответа и подхватывается cookie-jar транспорта;
для авторизованных запросов токена `token` достаточно.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, cast

from kworkapi.exceptions import KworkAuthError

if TYPE_CHECKING:
    from kworkapi.transport import Transport


@dataclass
class Session:
    """Состояние авторизованной сессии (сериализуемо для хранения)."""

    token: str
    uad: str
    slrememberme: str = ""
    expired: int | None = None
    user_id: int | None = None
    need_2fa: bool = False

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        fields = {"token", "uad", "slrememberme", "expired", "user_id", "need_2fa"}
        return cls(**{k: v for k, v in data.items() if k in fields})


class Auth:
    """Логика входа. Хранение сессии — задача вызывающего кода/клиента."""

    def __init__(self, transport: "Transport") -> None:
        self._transport = transport

    async def sign_in(
        self,
        login: str,
        password: str,
        *,
        recaptcha_pass_token: str = "",
    ) -> Session:
        """Войти по логину/паролю. Возвращает Session с токеном.

        :raises KworkAuthError: если вход не удался или токен не найден.
        """
        body = await self._transport.call(
            "signIn",
            data={
                "login": login,
                "password": password,
                "recaptcha_pass_token": recaptcha_pass_token,
            },
            auth=False,
        )

        resp: Any = body.get("response")
        if not isinstance(resp, dict):
            raise KworkAuthError("В ответе /signIn не найден token", payload=body)
        data = cast("dict[str, Any]", resp)
        if not data.get("token"):
            raise KworkAuthError("В ответе /signIn не найден token", payload=body)
        return Session(
            token=data["token"],
            uad=self._transport.uad,
            slrememberme=self._transport.current_slrememberme(),
            expired=data.get("expired"),
            need_2fa=bool(data.get("need_2fa", False)),
        )

    async def sign_up(
        self,
        username: str,
        email: str,
        password: str,
        *,
        type: str = "worker",
        promocode: str = "",
        recaptcha_response: str = "",
        is_subscribed: int = 0,
    ) -> Session:
        """Зарегистрироваться (`/signUp`). Возвращает Session с токеном."""
        body = await self._transport.call(
            "signUp",
            data={
                "username": username,
                "email": email,
                "password": password,
                "type": type,
                "promocode": promocode,
                "g-recaptcha-response": recaptcha_response,
                "is_subscribed": is_subscribed,
            },
            auth=False,
        )
        resp: Any = body.get("response")
        if not isinstance(resp, dict):
            raise KworkAuthError("В ответе /signUp не найден token", payload=body)
        data = cast("dict[str, Any]", resp)
        if not data.get("token"):
            raise KworkAuthError("В ответе /signUp не найден token", payload=body)
        return Session(
            token=data["token"],
            uad=self._transport.uad,
            slrememberme=self._transport.current_slrememberme(),
            expired=data.get("expired"),
            need_2fa=bool(data.get("need_2fa", False)),
        )

    async def reset_password(self, email: str, *, recaptcha_response: str = "") -> dict[str, Any]:
        """Запросить сброс пароля письмом (`/resetPassword`)."""
        return await self._transport.call(
            "resetPassword",
            data={"email": email, "g-recaptcha-response": recaptcha_response},
            auth=False,
        )

    async def logout(self, *, push_token: str = "") -> bool:
        """Выйти на сервере (инвалидировать сессию)."""
        body = await self._transport.call("logout", data={"pushToken": push_token})
        return bool(body.get("success", True))
