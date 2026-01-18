"""REST: загрузка файлов."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from api.deps import get_client
from kworkapi import KworkClient

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload(
    file: UploadFile,
    client: Annotated[KworkClient, Depends(get_client)],
) -> dict:
    """Загрузить файл-вложение."""
    content = await file.read()
    return await client.files.upload(
        content,
        file.filename or "file",
        content_type=file.content_type or "application/octet-stream",
    )
