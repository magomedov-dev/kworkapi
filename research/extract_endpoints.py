#!/usr/bin/env python3
"""Парсер декомпилированных Retrofit-сервисов kwork → markdown-каталог эндпоинтов.

Читает research/captures/kwork-src/.../data/remote/*Service.java и извлекает по
каждому методу: HTTP-глагол, путь, имя, поля формы (@c), карты полей (@d),
заголовки (@i), тело (@a), multipart-части (@q).

Запуск:  python research/extract_endpoints.py > docs/03-endpoints.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REMOTE = Path("research/captures/kwork-src/sources/ru/kwork/app/data/remote")

PATH_RE = re.compile(r'@(?:hr\.)?([of])\("([^"]+)"\)')
METHOD_RE = re.compile(r"\bObject\s+([A-Za-z0-9_]+)\(")
FIELD_RE = re.compile(r'@(?:hr\.)?c\((?:encoded\s*=\s*\w+,\s*value\s*=\s*)?"([^"]+)"\)')
HEADER_RE = re.compile(r'@(?:hr\.)?i\("([^"]+)"\)')
HAS_FIELDMAP = re.compile(r"@(?:hr\.)?d\b")
HAS_BODY = re.compile(r"@(?:hr\.|nr\.)?a\s")
HAS_PART = re.compile(r"@q\b")

VERB = {"o": "POST", "f": "GET"}


def parse_service(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[dict] = []
    pending: tuple[str, str] | None = None
    for line in lines:
        m = PATH_RE.search(line)
        if m:
            pending = (VERB.get(m.group(1), m.group(1)), m.group(2))
            continue
        if pending and "Object " in line and METHOD_RE.search(line):
            name = METHOD_RE.search(line).group(1)
            verb, route = pending
            fields = FIELD_RE.findall(line)
            headers = HEADER_RE.findall(line)
            out.append(
                {
                    "name": name,
                    "verb": verb,
                    "route": route,
                    "fields": fields,
                    "headers": headers,
                    "fieldmap": bool(HAS_FIELDMAP.search(line)),
                    "body": bool(HAS_BODY.search(line)),
                    "part": bool(HAS_PART.search(line)),
                }
            )
            pending = None
    return out


def main() -> None:
    services = sorted(REMOTE.glob("*Service.java"))
    total = 0
    print("# Каталог эндпоинтов kwork API\n")
    print("> Сгенерировано автоматически из декомпилированного приложения "
          "`research/extract_endpoints.py`. Базовый URL: `https://api.kwork.ru/`.\n")
    print("Все методы — `application/x-www-form-urlencoded`. Общие поля у "
          "большинства: `token`, `uad`, `slrememberme`, `device`; заголовки "
          "`Authorization` (статичный) и `Cookie`.\n")
    for svc in services:
        eps = parse_service(svc)
        if not eps:
            continue
        total += len(eps)
        print(f"\n## {svc.stem} ({len(eps)})\n")
        print("| Метод | HTTP | Путь | Поля формы | Особое |")
        print("|---|---|---|---|---|")
        for e in eps:
            extra = []
            if e["fieldmap"]:
                extra.append("FieldMap")
            if e["body"]:
                extra.append("Body(JSON)")
            if e["part"]:
                extra.append("Multipart")
            # убираем общие поля из вывода для читаемости
            common = {"token", "uad", "slrememberme", "device"}
            specific = [f for f in e["fields"] if f not in common]
            fields = ", ".join(f"`{f}`" for f in specific) or "—"
            print(f"| `{e['name']}` | {e['verb']} | `{e['route']}` | {fields} | "
                  f"{', '.join(extra) or '—'} |")
    print(f"\n---\n\n**Всего эндпоинтов: {total}** в {len(services)} сервисах.")


if __name__ == "__main__":
    if not REMOTE.exists():
        sys.exit(f"Не найден декомпилированный код: {REMOTE}")
    main()
