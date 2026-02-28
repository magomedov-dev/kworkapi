# Changelog

Все заметные изменения проекта. Формат основан на
[Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версионирование — [SemVer](https://semver.org/lang/ru/).

## [0.6.0] — 2026-02-28

Обработка капчи при входе (challenge/response вместо исключения).

### Добавлено

- **`LoginChallenge`** — `login()`/`register()` возвращают `Session | LoginChallenge`.
  При `error_code 118` возвращается челлендж с `provider`, `sitekey`
  (`6LdX9CAT…`, Google reCAPTCHA v2) и `page_url` (`/captcha_only`) — без исключения.
- **`KworkClient.solve_captcha(challenge, g_recaptcha_response)`** → `Session`
  (через `/signInWithCaptcha`).
- **`recaptcha_pass_token`** сохраняется в `Session` и автоматически переиспользуется
  при следующих входах, чтобы капчу не спрашивали повторно.
- **FastAPI**: двухшаговый вход — `POST /auth/login` отдаёт `status:"captcha"` с
  sitekey/page_url, `POST /auth/login/captcha` принимает решение и выдаёт токен.

### Подтверждено живым трафиком

- Капча `/signIn` приходит как HTTP 200 `{"success":false,"error_code":118}`; провайдер —
  Google reCAPTCHA v2, sitekey со страницы `/captcha_only`. HTTP 403 от Qrator-WAF —
  отдельный механизм (не капча), поднимается как `KworkRateLimitError`.

## [0.5.0] — 2026-02-28

Подготовка к публикации: строгая типизация и упаковка для PyPI.

### Добавлено

- **Полная типизация**: пройден **pyright strict** (0 ошибок) и mypy; маркер
  `py.typed` (PEP 561) — потребители получают типы и автодополнение из коробки.
- **Метаданные пакета** для PyPI: classifiers, keywords, project-urls, SPDX-лицензия,
  включение `docs/` в sdist.
- `pyright` добавлен в dev-зависимости и в инструменты качества.

### Изменено

- `Page[T]` теперь generic-`dataclass` (итерация, `len()`, `model_dump()`) — убран
  конфликт с pydantic и обеспечена корректная типизация.
- Внутренние хелперы и транспорт строго типизированы (wire-JSON как `Any` + `cast`).

## [0.4.0] — 2026-02-26

Полное покрытие API: **12 ресурсов, 166 методов**.

### Добавлено

- **account**: телефон (привязка/подтверждение/WhatsApp), удаление аккаунта,
  компания/yescrow (ИНН, верификация), баланс (ссылка пополнения, уведомления),
  push-токены, голосовые настройки, роль/самозанятость/доступность по выходным,
  география (страны/города/часовые пояса), публичные фичи, капча, web-auth-токен.
- **auth**: регистрация (`register`) и сброс пароля (`reset_password`).
- **users**: категории/статусы kwork'ов пользователя, заблокированные диалоги.
- **exchange**: детали отклика, счётчик проектов по фильтрам, избранные категории.
- **kworks**: доп. детали, FAQ, таблица ссылок, категории жалоб, пополнение баланса.
- **messages**: получение сообщения, жалоба, отметка треков, скрытие диалога, статус.
- **orders**: взятие в работу, портфолио, правка ответа, чек, экстры исполнителя
  и поток удаления экстры.
- **Новые ресурсы**: `portfolio`, `tracks` (треки заказа), `misc` (правовые страницы,
  in-app уведомления).

### Примечания

- Сознательно не реализованы методы с JSON-телом (`@Body`), форму которых не дал
  захват трафика (управление «wants», покупка kwork, жалоба на kwork, соц-вход).

## [0.3.0] — 2026-02-24

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

## [0.2.0] — 2026-02-07

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

## [0.1.0] — 2026-01-10

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

[0.6.0]: https://github.com/magomedov-dev/kworkapi/releases/tag/v0.6.0
[0.5.0]: https://github.com/magomedov-dev/kworkapi/releases/tag/v0.5.0
[0.4.0]: https://github.com/magomedov-dev/kworkapi/releases/tag/v0.4.0
[0.3.0]: https://github.com/magomedov-dev/kworkapi/releases/tag/v0.3.0
[0.2.0]: https://github.com/magomedov-dev/kworkapi/releases/tag/v0.2.0
[0.1.0]: https://github.com/magomedov-dev/kworkapi/releases/tag/v0.1.0
