"""Прочее: правовые страницы и in-app уведомления."""

from __future__ import annotations

from kworkapi.resources.base import Resource


class MiscResource(Resource):
    async def tos(self) -> dict:
        """Условия использования (`/tos`)."""
        return self._payload(await self._call("tos", auth=False))

    async def terms(self) -> dict:
        """Правила (`/terms`)."""
        return self._payload(await self._call("terms", auth=False))

    async def terms_of_service(self) -> dict:
        """Пользовательское соглашение (`/termsOfService`)."""
        return self._payload(await self._call("termsOfService", auth=False))

    async def privacy(self) -> dict:
        """Политика конфиденциальности (`/privacy`)."""
        return self._payload(await self._call("privacy", auth=False))

    async def resolution(self) -> dict:
        """Разрешение споров (`/resolution`)."""
        return self._payload(await self._call("resolution", auth=False))

    async def in_app_notification(self, *, app_version: str = "", os_type: str = "android") -> dict:
        """In-app уведомление (`/getInAppNotification`)."""
        data = {"app_version": app_version, "os_type": os_type}
        return self._payload(await self._call("getInAppNotification", data=data))
