# Changelog

Все заметные изменения проекта. Формат основан на
[Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версионирование — [SemVer](https://semver.org/lang/ru/).

## [0.3.0] — 2026-06-21

Завершение работы с заказами: аватар, полный поток отмены, пресеты опций.

### Добавлено

- **Аватар**: `account.update_avatar` (multipart `/updateAvatar`).
- **Полный поток отмены заказа**: `cancel_by_payer`/`cancel_by_worker`
  (с `reason_type`/`message`/`hide_kworks`), `cancellation_reasons`,
  `cancel_awaiting_payment`/`pay_awaiting_payment`, ответ встречной стороны
  (`confirm_cancel_*`/`reject_cancel_*`/`delete_cancel_*` для payer/worker).
- **Пресеты опций**: `orders.custom_options_presets`, `orders.offer_options`.

### Изменено

- Уточнены реальные поля `cancel_by_payer`/`cancel_by_worker` (были best-effort
  `orderId` → стали подтверждённые `order_id`/`reason_type`/`message`).

## [0.2.0] — 2026-06-21

Расширение покрытия: заказы, детали kwork, файлы, голосовые (Фаза 4b).

### Добавлено

- **Заказы** (`orders`): детали/шапка/файлы, приём (`approve`/`approve_stages`),
  отправка на проверку/доработку/требования, повтор, бонус, отмена, отзывы
  (`create_review`/`edit_review`/`delete_review`) и ответы на них.
- **Экстры заказа**: доступные/заказанные, покупка, приём/отклонение/удаление.
- **Стадии заказа**: приём/отклонение предложения, оплата стадии, прогресс.
- **Арбитраж и отчёты**: `rate_arbitration`, `send_report`.
- **Детали kwork** (`kworks`): `details`, `reviews`, `portfolios`.
- **Файлы** (`files`): `upload`, `upload_voice` (multipart с файловой частью).
- **Голосовые сообщения**: транскрипция, отметка прослушанным, статус конвертации.
- **FastAPI**: эндпоинты деталей/приёма заказа и загрузки файла (UploadFile).

### Примечания

- Часть методов отмены заказа и ответов помечены best-effort (точные поля не были
  в захвате трафика).

## [0.1.0] — 2026-06-21

Первый релиз: рабочая библиотека и REST-сервис над приватным API kwork.ru.

### Добавлено

- **Реверс-инжиниринг API** (декомпиляция `ru.kwork.app` + перехват трафика):
  base URL `https://api.kwork.ru/`, схема авторизации, 192 эндпоинта, из них
  63 подтверждены живым трафиком. Полная документация в `docs/`.
- **Ядро клиента** (`KworkClient`, async): транспорт с общими полями
  (`token`/`uad`/`slrememberme`/`device`), статичный `Authorization`, cookie-jar,
  ретраи/бэкофф, троттлинг, разбор обёрток и типизированные ошибки.
- **Авторизация**: `login` (`signIn`), `Session` (token/uad/slrememberme/expired),
  восстановление сессии (`from_session`), `logout`.
- **Ресурсы чтения**: `account`, `catalog`, `search`, `exchange`, `users`, `orders`.
- **Ресурсы действий**: `messages` (отправка/редактирование/удаление/звезда/блок),
  `exchange` (отклики, multipart `/api/offer/*`), `account` (настройки),
  `kworks` (избранное/скрытие/пауза/старт/удаление).
- **Pydantic-модели** ответов (Actor, User, Kwork, Dialog, Offer, Project и др.).
- **FastAPI-сервис**: REST на все группы ресурсов, авторизация по `X-Kwork-Token`,
  маппинг ошибок в HTTP, Swagger/ReDoc.
- **Качество**: тесты (моки + опциональные живые), покрытие 88%, ruff, mypy, CI.

### Известные ограничения

- Детали kwork открываются в приложении через webview (`getWebAuthToken`) — нативного
  JSON-эндпоинта нет.
- Частые входы `/signIn` с одного IP ловят анти-бот (HTTP 403) — переиспользуйте
  сессию и `uad`, включайте троттлинг.
- Не покрыты (план 4b): детальные операции с заказами (approve/cancel/стадии/отзывы),
  загрузка файлов/аватара, голосовые сообщения.

[0.3.0]: https://example.com/kworkapi/releases/tag/v0.3.0
[0.2.0]: https://example.com/kworkapi/releases/tag/v0.2.0
[0.1.0]: https://example.com/kworkapi/releases/tag/v0.1.0
