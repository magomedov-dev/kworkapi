"""Аккаунт: профиль, баланс, уведомления, безопасность, оплата."""

from __future__ import annotations

from kworkapi.models.user import Actor
from kworkapi.resources.base import Resource


class AccountResource(Resource):
    async def me(self) -> Actor:
        """Профиль и состояние текущего пользователя (`/actor`)."""
        return self._model(await self._call("actor"), Actor)

    async def notifications(self, *, page: int = 1) -> dict:
        """Лента уведомлений (`/notificationsFetch`)."""
        return self._payload(await self._call("notificationsFetch", data={"page": page}))

    async def security_data(self) -> dict:
        """Данные безопасности аккаунта (`/getSecurityUserData`)."""
        return self._payload(await self._call("getSecurityUserData"))

    async def payment_methods(self, *, with_company: int = 0) -> dict:
        """Доступные способы оплаты и комиссии (`/getPaymentMethods`)."""
        return self._payload(
            await self._call("getPaymentMethods", data={"withCompany": with_company})
        )

    async def available_features(self) -> dict:
        """Доступные фичи аккаунта (`/getAvailableFeatures`)."""
        return self._payload(await self._call("getAvailableFeatures"))

    async def badges(self) -> dict:
        """Бейджи/счётчики (`/getBadgesInfo`)."""
        return self._payload(await self._call("getBadgesInfo", data={"makeOnline": 0}))
