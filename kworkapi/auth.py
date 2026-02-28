"""Авторизация, состояние сессии и капча-челлендж.

Подтверждено реверсом и живым трафиком:
  POST /signIn (login, password, recaptcha_pass_token?, uad, device) + заголовок Authorization
    success → {"success": true, "response": {"token", "expired", "need_2fa"}, "recaptcha_pass_token"?}
    капча  → {"success": false, "error": "Подтвердите, что вы не робот", "error_code": 118}

При error_code 118 нужна Google reCAPTCHA v2 (sitekey ниже, страница /captcha_only).
Решение (`g-recaptcha-response`) отправляется методом /signInWithCaptcha; в ответе
приходит `recaptcha_pass_token`, который переиспользуется в /signIn, чтобы капчу
больше не спрашивали.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, cast

from kworkapi.exceptions import KworkAPIError, KworkAuthError

if TYPE_CHECKING:
    from kworkapi.transport import Transport

# Код ответа /signIn «нужна капча» (подтверждено живым трафиком).
CAPTCHA_REQUIRED_CODE = 118

# Google reCAPTCHA v2 sitekey kwork (со страницы /captcha_only, одинаков для .ru/.com).
RECAPTCHA_SITEKEY = "6LdX9CATAAAAAARb0rBU8FXXdUBajy3IlVjZ2qHS"


@dataclass
class Session:
    """Состояние авторизованной сессии (сериализуемо для хранения)."""

    token: str
    uad: str
    slrememberme: str = ""
    expired: int | None = None
    user_id: int | None = None
    need_2fa: bool = False
    # «пропуск капчи» — переиспользуется при следующих входах, чтобы не решать капчу.
    recaptcha_pass_token: str = ""

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        fields = {
            "token", "uad", "slrememberme", "expired",
            "user_id", "need_2fa", "recaptcha_pass_token",
        }
        return cls(**{k: v for k, v in data.items() if k in fields})


@dataclass
class LoginChallenge:
    """Челлендж, который нужно решить, чтобы завершить вход (обычно капча).

    Возвращается из ``login()``/``register()`` вместо исключения. Потребитель
    решает капчу любым способом (виджет reCAPTCHA / решалка / SMS) и передаёт
    результат в ``solve_captcha``.
    """

    kind: str = "recaptcha"               # "recaptcha" | "image" | "phone"
    provider: str | None = None           # "recaptcha"
    sitekey: str | None = None            # для токен-капчи (reCAPTCHA)
    page_url: str | None = None           # страница с виджетом (для WebView/решалки)
    image: str | None = None              # base64 — для картиночной капчи
    captcha_sid: str | None = None        # id картиночной капчи
    phone_mask: str | None = None         # маска телефона — для SMS-подтверждения
    raw: dict[str, Any] | None = None     # исходный ответ API
    # учётные данные для продолжения входа (тот же контекст: клиент/uad/cookies)
    login: str = ""
    password: str = field(default="", repr=False)


class Auth:
    """Логика входа. Хранение сессии — задача вызывающего кода/клиента."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def sign_in(
        self,
        login: str,
        password: str,
        *,
        recaptcha_pass_token: str = "",
    ) -> Session | LoginChallenge:
        """Войти по логину/паролю.

        :returns: ``Session`` при успехе или ``LoginChallenge`` если нужна капча.
        :raises KworkAuthError: при иной ошибке входа.
        """
        try:
            body = await self._transport.call(
                "signIn",
                data={
                    "login": login,
                    "password": password,
                    "recaptcha_pass_token": recaptcha_pass_token,
                },
                auth=False,
            )
        except KworkAPIError as exc:
            if exc.code == CAPTCHA_REQUIRED_CODE:
                return self._captcha_challenge(login, password, exc.payload)
            raise
        return self._session_from(body, "/signIn")

    async def solve_captcha(self, challenge: LoginChallenge, solution: str) -> Session:
        """Завершить вход, отправив решение капчи (``g-recaptcha-response``).

        :param challenge: челлендж из ``sign_in``.
        :param solution: токен reCAPTCHA (``g-recaptcha-response``).
        """
        body = await self._transport.call(
            "signInWithCaptcha",
            data={
                "login": challenge.login,
                "password": challenge.password,
                "g-recaptcha-response": solution,
                "recaptcha_pass_token": "",
                "phone_last": "",
            },
            auth=False,
        )
        return self._session_from(body, "/signInWithCaptcha")

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
    ) -> Session | LoginChallenge:
        """Зарегистрироваться (`/signUp`)."""
        try:
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
        except KworkAPIError as exc:
            if exc.code == CAPTCHA_REQUIRED_CODE:
                return self._captcha_challenge(email, password, exc.payload)
            raise
        return self._session_from(body, "/signUp")

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

    # --- внутреннее ----------------------------------------------------

    def _session_from(self, body: dict[str, Any], method: str) -> Session:
        resp: Any = body.get("response")
        if not isinstance(resp, dict):
            raise KworkAuthError(f"В ответе {method} не найден token", payload=body)
        data = cast("dict[str, Any]", resp)
        if not data.get("token"):
            raise KworkAuthError(f"В ответе {method} не найден token", payload=body)
        return Session(
            token=data["token"],
            uad=self._transport.uad,
            slrememberme=self._transport.current_slrememberme(),
            expired=data.get("expired"),
            need_2fa=bool(data.get("need_2fa", False)),
            recaptcha_pass_token=str(body.get("recaptcha_pass_token") or ""),
        )

    def _captcha_challenge(self, login: str, password: str, payload: Any) -> LoginChallenge:
        web = self._transport.base_url.replace("//api.", "//").rstrip("/")
        return LoginChallenge(
            kind="recaptcha",
            provider="recaptcha",
            sitekey=RECAPTCHA_SITEKEY,
            page_url=f"{web}/captcha_only",
            login=login,
            password=password,
            raw=cast("dict[str, Any]", payload) if isinstance(payload, dict) else None,
        )
