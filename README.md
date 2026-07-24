# nsgifts-api 2.0

Unofficial asynchronous Python client for
[NS.Gifts API v2](https://api.ns.gifts/api-docs).

[English](#english) · [Русский](#русский)

> This project is not affiliated with NS.Gifts. API access, credentials,
> account support, and IP whitelist changes are handled by NS.Gifts support.

## English

### What changed in 2.0

Version 2.0 is a breaking migration from API v1 to API v2:

- two-layer authentication with API secret and a two-hour session token;
- HMAC-SHA256 signatures for every request;
- partner `user_id` and replay-protected timestamps;
- one live `/stock` catalog with dynamic order fields;
- one order flow for codes, Steam top-ups, and Steam gifts;
- typed Pydantic request and response models;
- safe retry rules that never duplicate a payment automatically.

API v1 methods and models are not included.

### Requirements

- Python 3.10 or newer;
- existing NS.Gifts account login and password;
- numeric `user_id`;
- Base64 API secret issued by NS.Gifts support;
- the device or server public IP added to the API IP whitelist.

Never commit a real `.env` file or paste credentials into source code.

### Installation

Install a wheel downloaded from the GitHub Release:

```bash
python -m pip install nsgifts_api-2.0.0-py3-none-any.whl
```

Install the tagged source directly:

```bash
python -m pip install \
  "git+https://github.com/lfyzer/nsgifts.git@v2.0.0"
```

### Environment

Copy `.env.example` to `.env` and replace every placeholder:

```dotenv
NSGIFTS_USER_ID=1234
NSGIFTS_LOGIN=your_login
NSGIFTS_PASSWORD=your_password
NSGIFTS_API_SECRET=PASTE-YOUR-BASE64-SECRET
NSGIFTS_BASE_URL=https://api.ns.gifts
```

`.env` is ignored by Git. Password, API secret, token, signature, and
`totp_code` values are masked in representations and diagnostics.

### Quick start

```python
import asyncio

from nsgifts_api import NSGiftsClient


async def main() -> None:
    async with NSGiftsClient() as client:
        balance = await client.account.get_balance()
        stock = await client.catalog.get_stock()
        print("Balance:", balance.balance)
        print("Categories:", len(stock.categories))


asyncio.run(main())
```

Protected methods authenticate lazily. Explicit authentication is also
available:

```python
async with NSGiftsClient() as client:
    session = await client.authenticate()
    print(session.user_id, session.expires_in)
```

The token is a masked `SecretStr` and normally does not need to be read.

### Stock and dynamic fields

Always read `/stock` before selecting a service. Prices, stock, service IDs,
and required order fields may change.

```python
async with NSGiftsClient() as client:
    stock = await client.catalog.get_stock()

    for category in stock.categories:
        print(category.category_name)
        for service in category.services:
            print(
                service.service_id,
                service.service_name,
                service.price,
                service.currency,
                service.in_stock,
            )
        for field in category.fields:
            print(field.key, field.type, field.required)
```

The library validates the `fields` structure. The server remains the source
of truth for category-specific limits, enums, and regular expressions.

### Create an order

Every order uses the same endpoint and a UUID4 `custom_id`. The client
generates the UUID when it is omitted.

```python
from nsgifts_api import OrderField


async with NSGiftsClient() as client:
    order = await client.orders.create(
        service_id=449,
        fields=[
            OrderField(key="quantity", value=1),
        ],
    )
    print(order.custom_id)
    print(order.total_to_pay)
```

Service IDs above are documentation examples, not permanent constants. Find
the current service and field schema through `catalog.get_stock()`.

Steam top-up uses the same method:

```python
order = await client.orders.create(
    service_id=1,
    fields=[
        OrderField(key="account", value="steam_login"),
        OrderField(key="amount", value=10.0),
    ],
)
```

Steam Gift also uses the common order flow:

```python
order = await client.orders.create(
    service_id=394,
    fields=[
        OrderField(key="region", value="ru"),
        OrderField(key="sub_id", value=12345),
        OrderField(
            key="friendLink",
            value="https://s.team/p/abc-defg/12345678",
        ),
        OrderField(key="giftName", value="Gift"),
        OrderField(key="giftDescription", value="Enjoy!"),
    ],
)
```

### Pay once, then reconcile

```python
payment = await client.orders.pay(order.custom_id)
print(payment.status, payment.balance, payment.pins)
```

If purchase 2FA is enabled, the server may return HTTP `428`:

```python
from nsgifts_api import APITotpRequiredError


try:
    payment = await client.orders.pay(order.custom_id)
except APITotpRequiredError:
    payment = await client.orders.pay(
        order.custom_id,
        totp_code="123456",
    )
```

The library does not generate or store TOTP codes.

`pay_order` is not replay-idempotent. A repeated payment returns `409`. If a
network failure makes the outcome uncertain, the client raises
`APIRequestOutcomeUnknownError` and does not call payment again:

```python
from nsgifts_api import APIRequestOutcomeUnknownError


try:
    payment = await client.orders.pay(order.custom_id)
except APIRequestOutcomeUnknownError as error:
    info = await client.orders.get(error.custom_id)
    print(info.status, info.status_message)
```

### Asynchronous order state

Steam Gift delivery may return `in_progress`. Poll `order_info` until a
terminal status:

```python
import asyncio

from nsgifts_api import OrderStatus


while True:
    info = await client.orders.get(order.custom_id)
    if info.status is not OrderStatus.IN_PROGRESS:
        break
    await asyncio.sleep(5)
```

Documented order status values:

- `CREATED = 0`;
- `IN_PROGRESS = 10`;
- `COMPLETED = 2`;
- `REFUNDED = 7`;
- `CANCELLED = 5`.

### Steam helpers

```python
rates = await client.steam.get_exchange_rate(service_id=1)
apps = await client.steam.get_apps()
account = await client.steam.check_user("steam_login")

print(rates.rates.rub)
print(len(apps.apps))
print(account.account_status)
```

### Errors and retries

Important exceptions:

- `APIConfigurationError`;
- `APIAuthenticationError`;
- `APIClockSkewError`;
- `APIIPNotAllowedError`;
- `APITotpRequiredError`;
- `APIValidationError`;
- `APIInsufficientFundsError`;
- `APIConflictError`;
- `APIRateLimitError`;
- `APIServerError`;
- `APIRequestOutcomeUnknownError`.

Read-only operations may retry transient network, rate-limit, and server
errors. `create_order` and `pay_order` are never repeated automatically after
an uncertain outcome. Every retry receives a fresh timestamp and signature.

### Migration from v1

| API v1 | API v2 client |
| --- | --- |
| Bearer JWT | API secret + HMAC + `X-Token` |
| `user.login()` | `client.authenticate()` |
| `user.check_balance()` | `account.get_balance()` |
| three products methods | `catalog.get_stock()` |
| fixed `quantity` and `data` | dynamic `list[OrderField]` |
| `orders.create_order()` | `orders.create()` |
| `orders.pay_order()` | `orders.pay()` |
| POST `order_info` body | `orders.get(custom_id)` |
| Steam Gift methods | common `orders` flow |
| IP whitelist methods | NS.Gifts support |
| `signup()` and user info | removed from API v2 |

### Development

```bash
python -m pip install -e ".[dev]"
python -m ruff format --check .
python -m ruff check .
python -m mypy nsgifts_api
python -m pytest --cov=nsgifts_api
python -m build
```

Live purchase and payment tests are intentionally excluded.

## Русский

### Что изменилось в 2.0

Версия 2.0 — это несовместимый переход с API v1 на API v2:

- двухслойная авторизация через API-secret и двухчасовой session token;
- HMAC-SHA256-подпись каждого запроса;
- обязательные `user_id` и timestamp с replay-защитой;
- единый каталог `/stock` с динамическими полями заказа;
- общий поток заказов для кодов, Steam-пополнений и Steam Gift;
- типизированные Pydantic-модели запросов и ответов;
- безопасные повторы без автоматического дублирования оплаты.

Методы и модели API v1 в релиз не входят.

### Требования

- Python 3.10 или новее;
- существующие логин и пароль NS.Gifts;
- числовой `user_id`;
- API-secret в Base64, полученный у поддержки NS.Gifts;
- публичный IP сервера или устройства в IP whitelist.

Никогда не добавляйте настоящий `.env` в Git и не храните секреты в коде.

### Установка

Установите wheel из GitHub Release:

```bash
python -m pip install nsgifts_api-2.0.0-py3-none-any.whl
```

Или установите исходники по тегу:

```bash
python -m pip install \
  "git+https://github.com/lfyzer/nsgifts.git@v2.0.0"
```

### Настройка `.env`

Скопируйте `.env.example` в `.env` и замените шаблонные значения:

```dotenv
NSGIFTS_USER_ID=1234
NSGIFTS_LOGIN=your_login
NSGIFTS_PASSWORD=your_password
NSGIFTS_API_SECRET=PASTE-YOUR-BASE64-SECRET
NSGIFTS_BASE_URL=https://api.ns.gifts
```

Настоящий `.env` игнорируется Git. Пароль, API-secret, token, подпись и
`totp_code` маскируются в представлениях и диагностике.

### Быстрый старт

```python
import asyncio

from nsgifts_api import NSGiftsClient


async def main() -> None:
    async with NSGiftsClient() as client:
        balance = await client.account.get_balance()
        stock = await client.catalog.get_stock()
        print("Баланс:", balance.balance)
        print("Категорий:", len(stock.categories))


asyncio.run(main())
```

Авторизация выполняется лениво перед первым защищённым запросом. Её также
можно вызвать явно:

```python
async with NSGiftsClient() as client:
    session = await client.authenticate()
    print(session.user_id, session.expires_in)
```

### Каталог и динамические поля

Перед выбором услуги всегда запрашивайте `/stock`. Цены, остатки, service ID и
схемы полей могут измениться.

```python
async with NSGiftsClient() as client:
    stock = await client.catalog.get_stock()

    for category in stock.categories:
        print(category.category_name)
        for service in category.services:
            print(
                service.service_id,
                service.service_name,
                service.price,
                service.in_stock,
            )
        for field in category.fields:
            print(field.key, field.type, field.required)
```

Клиент проверяет структуру `fields`, но актуальные ограничения, enum и regex
всегда определяет сервер.

### Создание заказа

Все типы заказов используют единый метод и UUID4 `custom_id`. Если ID не
передан, клиент создаст его автоматически.

```python
from nsgifts_api import OrderField


async with NSGiftsClient() as client:
    order = await client.orders.create(
        service_id=449,
        fields=[
            OrderField(key="quantity", value=1),
        ],
    )
    print(order.custom_id)
    print(order.total_to_pay)
```

Service ID в примерах взяты из документации и не являются постоянными.
Получайте актуальные значения через `catalog.get_stock()`.

Пополнение Steam:

```python
order = await client.orders.create(
    service_id=1,
    fields=[
        OrderField(key="account", value="steam_login"),
        OrderField(key="amount", value=10.0),
    ],
)
```

Steam Gift:

```python
order = await client.orders.create(
    service_id=394,
    fields=[
        OrderField(key="region", value="ru"),
        OrderField(key="sub_id", value=12345),
        OrderField(
            key="friendLink",
            value="https://s.team/p/abc-defg/12345678",
        ),
        OrderField(key="giftName", value="Подарок"),
        OrderField(key="giftDescription", value="Приятной игры!"),
    ],
)
```

### Оплата, TOTP и восстановление

```python
payment = await client.orders.pay(order.custom_id)
print(payment.status, payment.balance, payment.pins)
```

Если для покупок включена 2FA, сервер может вернуть HTTP `428`:

```python
from nsgifts_api import APITotpRequiredError


try:
    payment = await client.orders.pay(order.custom_id)
except APITotpRequiredError:
    payment = await client.orders.pay(
        order.custom_id,
        totp_code="123456",
    )
```

Библиотека не генерирует и не хранит TOTP-коды.

Повторный `pay_order` не воспроизводит первый ответ и возвращает `409`. Если
результат оплаты неизвестен из-за сетевой ошибки, клиент выбрасывает
`APIRequestOutcomeUnknownError` и не повторяет оплату:

```python
from nsgifts_api import APIRequestOutcomeUnknownError


try:
    payment = await client.orders.pay(order.custom_id)
except APIRequestOutcomeUnknownError as error:
    info = await client.orders.get(error.custom_id)
    print(info.status, info.status_message)
```

Для асинхронной доставки проверяйте статус:

```python
import asyncio

from nsgifts_api import OrderStatus


while True:
    info = await client.orders.get(order.custom_id)
    if info.status is not OrderStatus.IN_PROGRESS:
        break
    await asyncio.sleep(5)
```

### Steam-методы

```python
rates = await client.steam.get_exchange_rate(service_id=1)
apps = await client.steam.get_apps()
account = await client.steam.check_user("steam_login")

print(rates.rates.rub)
print(len(apps.apps))
print(account.account_status)
```

### Ошибки и повторы

Основные исключения:

- `APIConfigurationError`;
- `APIAuthenticationError`;
- `APIClockSkewError`;
- `APIIPNotAllowedError`;
- `APITotpRequiredError`;
- `APIValidationError`;
- `APIInsufficientFundsError`;
- `APIConflictError`;
- `APIRateLimitError`;
- `APIServerError`;
- `APIRequestOutcomeUnknownError`.

Read-only операции могут повторяться при временных сетевых ошибках, `429` и
`5xx`. `create_order` и `pay_order` после неопределённого результата
автоматически не повторяются. Каждый повтор подписывается новым timestamp.

### Миграция с v1

| API v1 | Клиент API v2 |
| --- | --- |
| Bearer JWT | API-secret + HMAC + `X-Token` |
| `user.login()` | `client.authenticate()` |
| `user.check_balance()` | `account.get_balance()` |
| три метода products | `catalog.get_stock()` |
| фиксированные `quantity` и `data` | `list[OrderField]` |
| `orders.create_order()` | `orders.create()` |
| `orders.pay_order()` | `orders.pay()` |
| POST `order_info` с body | `orders.get(custom_id)` |
| отдельные Steam Gift методы | общий поток `orders` |
| методы IP whitelist | обращение в поддержку |
| `signup()` и user info | удалены из API v2 |

### Разработка

```bash
python -m pip install -e ".[dev]"
python -m ruff format --check .
python -m ruff check .
python -m mypy nsgifts_api
python -m pytest --cov=nsgifts_api
python -m build
```

Live-тесты создания и оплаты заказов намеренно отсутствуют.

## License

[MIT](LICENSE)
