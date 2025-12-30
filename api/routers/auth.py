"""REST: авторизация."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.deps import get_anon_client
from kworkapi import KworkClient

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    login: str
    password: str
    recaptcha_pass_token: str = ""


class LoginResponse(BaseModel):
    token: str
    expired: int | None = None
    need_2fa: bool = False


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    client: Annotated[KworkClient, Depends(get_anon_client)],
) -> LoginResponse:
    """Войти по логину/паролю и получить токен сессии kwork.

    Полученный `token` передавайте в заголовке `X-Kwork-Token` остальным запросам.
    """
    session = await client.login(
        body.login, body.password, recaptcha_pass_token=body.recaptcha_pass_token
    )
    return LoginResponse(token=session.token, expired=session.expired, need_2fa=session.need_2fa)
