# Карта эндпоинтов api.kwork.ru

Полный каталог (192 эндпоинта, 14 сервисов) генерируется из декомпилированного
приложения и лежит в **[../docs/03-endpoints.md](../docs/03-endpoints.md)**.

Перегенерировать после обновления APK:

```bash
python research/extract_endpoints.py > docs/03-endpoints.md
```

Подтверждённые базовые факты (см. [../docs/02-kwork-api-reference.md](../docs/02-kwork-api-reference.md)):

| Параметр | Значение | Статус |
|---|---|---|
| Base URL | `https://api.kwork.ru/` | ✅ из `cy/d.java` |
| `Authorization` (app) | `Basic bW9iaWxlX2FwaTpxRnZmUmw3dw==` | ✅ из `nr/d.java` |
| Токен пользователя | поле `token` | ✅ ответ `/signIn` |
| `uad` | SHA-1 device id | ✅ из `nr/d.java` |
| Cookie | `slrememberme=<value>` | ✅ из `nr/d.java` |
| Формы ответов | `DataResponse`/`PagedResponse`/`BooleanResponse` | ✅ из моделей |

Осталось подтвердить живым трафиком (mitmproxy): точные формы JSON-ответов и `User-Agent`.
