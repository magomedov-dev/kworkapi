"""Загрузка файлов (вложения, голосовые).

multipart с файловой частью (FileService.fileUpload/voiceUpload). Имя файловой
части на сервере точно не подтверждено — по умолчанию "file", можно переопределить.
"""

from __future__ import annotations

from kworkapi.resources.base import Resource


class FilesResource(Resource):
    async def upload(
        self,
        content: bytes,
        filename: str,
        *,
        field: str = "file",
        content_type: str = "application/octet-stream",
    ) -> dict:
        """Загрузить файл-вложение (`/fileUpload`)."""
        files = {field: (filename, content, content_type)}
        return await self._call("fileUpload", files=files)

    async def upload_voice(
        self,
        content: bytes,
        filename: str = "voice.ogg",
        *,
        field: str = "file",
        content_type: str = "audio/ogg",
    ) -> dict:
        """Загрузить голосовое сообщение (`/voiceUpload`)."""
        files = {field: (filename, content, content_type)}
        return await self._call("voiceUpload", files=files)
