"""REST: авторизация (с поддержкой капчи)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.deps import get_anon_client
from kworkapi import KworkClient, LoginChallenge

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    login: str
    password: str
    recaptcha_pass_token: str = ""


class LoginResponse(BaseModel):
    status: str  # "ok" | "captcha"
    token: str | None = None
    expired: int | None = None
    need_2fa: bool = False
    recaptcha_pass_token: str | None = None
    # поля капчи (status == "captcha")
    provider: str | None = None
    sitekey: str | None = None
    page_url: str | None = None


class CaptchaRequest(BaseModel):
    login: str
    password: str
    solution: str  # g-recaptcha-response


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    client: Annotated[KworkClient, Depends(get_anon_client)],
) -> LoginResponse:
    """Войти. Если нужна капча — вернёт `status="captcha"` с sitekey и страницей.

    Решите reCAPTCHA (sitekey/page_url) и завершите вход через `POST /auth/login/captcha`.
    """
    result = await client.login(
        body.login, body.password, recaptcha_pass_token=body.recaptcha_pass_token
    )
    if isinstance(result, LoginChallenge):
        return LoginResponse(
            status="captcha",
            provider=result.provider,
            sitekey=result.sitekey,
            page_url=result.page_url,
        )
    return LoginResponse(
        status="ok",
        token=result.token,
        expired=result.expired,
        need_2fa=result.need_2fa,
        recaptcha_pass_token=result.recaptcha_pass_token,
    )


@router.post("/login/captcha", response_model=LoginResponse)
async def login_captcha(
    body: CaptchaRequest,
    client: Annotated[KworkClient, Depends(get_anon_client)],
) -> LoginResponse:
    """Завершить вход решением капчи (`g-recaptcha-response`).

    Передайте те же логин/пароль и токен reCAPTCHA. В ответе — `token` и
    `recaptcha_pass_token` (сохраните его, чтобы при следующих входах не решать капчу).
    """
    challenge = LoginChallenge(login=body.login, password=body.password)
    session = await client.solve_captcha(challenge, body.solution)
    return LoginResponse(
        status="ok",
        token=session.token,
        expired=session.expired,
        need_2fa=session.need_2fa,
        recaptcha_pass_token=session.recaptcha_pass_token,
    )
