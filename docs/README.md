# Документация KworkAPI

Полная документация проекта: как устроен приватный API kwork.ru, как мы его
получили и как реализуем библиотеку поверх него.

## Содержание

1. **[01-reverse-engineering.md](01-reverse-engineering.md)** — методология реверс-инжиниринга:
   инструменты, декомпиляция APK, что и где найдено в коде приложения.
2. **[02-kwork-api-reference.md](02-kwork-api-reference.md)** — справочник по API kwork:
   базовый URL, схема авторизации (`Authorization`, `token`, `uad`, `slrememberme`),
   формат запросов и ответов, обработка ошибок.
3. **[03-endpoints.md](03-endpoints.md)** — полный каталог из 192 эндпоинтов (14 сервисов),
   генерируется автоматически из декомпилированного кода.
4. **[04-architecture.md](04-architecture.md)** — архитектура нашей библиотеки и FastAPI-сервиса.
5. **[05-roadmap.md](05-roadmap.md)** — поэтапный план реализации до качественной библиотеки.
6. **[06-captured-responses.md](06-captured-responses.md)** — схемы реальных ответов 63 эндпоинтов
   (по живому трафику через mitmproxy, санитизировано).
7. **[07-usage.md](07-usage.md)** — руководство пользователя: установка, авторизация,
   все ресурсы с примерами, обработка ошибок, REST-сервис.

## TL;DR что уже известно

| Параметр | Значение | Источник |
|---|---|---|
| Базовый URL | `https://api.kwork.ru/` | `cy/d.java` (ServerManager) |
| Авторизация приложения | `Authorization: Basic bW9iaWxlX2FwaTpxRnZmUmw3dw==` | `nr/d.java` (`mobile_api:qFvfRl7w`) |
| Токен пользователя | поле `token` в теле каждого запроса | ответ `/signIn` |
| ID устройства | поле `uad` (SHA-1 от build-props + android_id + time) | `nr/d.java` |
| Сессионная cookie | `Cookie: slrememberme=<value>` | `nr/d.java` |
| Формат запроса | `application/x-www-form-urlencoded`, в основном POST | Retrofit-аннотации |
| Эндпоинтов | **192** в 14 сервисах | `research/extract_endpoints.py` |

> Все находки получены статическим анализом APK. Динамическую проверку (живой
> трафик через mitmproxy) проводим на этапе валидации — см. roadmap.
