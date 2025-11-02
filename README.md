# nsgifts (Unofficial NS.Gifts API Client)

[🇷🇺 Русский](#русская-версия) | [🇺🇸 English](#english-version)

---

## English Version

Asynchronous Python client for [NS.Gifts API](https://api.ns.gifts/docs).  
❗ I do not collaborate and am not affiliated with [NS.Gifts](https://wholesale.ns.gifts/). This client is written solely for convenience when working with the API.

### 📌 Quick Start

#### Basic Usage
```python
import asyncio
from nsgifts_api import NSGiftsClient

async def main():
    async with NSGiftsClient() as client:
        # Authentication
        login_result = await client.user.login("your_login", "your_password")
        print(f"Token: {login_result.access_token}")

        # Check balance
        balance = await client.user.check_balance()
        print(f"Balance: {balance}")

        # Get categories
        categories = await client.services.get_categories()
        print(categories)

asyncio.run(main())
```

#### Using Configuration (Recommended)
```python
import asyncio
from nsgifts_api import NSGiftsClient, ClientConfig

async def main():
    # Create configuration with credentials
    config = ClientConfig(
        email="your_login",
        password="your_password",
        enable_logging=True
    )
    
    async with NSGiftsClient(config=config) as client:
        # Client is already authenticated!
        balance = await client.user.check_balance()
        print(f"Balance: {balance}")
        
        user_info = await client.user.get_user_info()
        print(f"Username: {user_info.username}")

asyncio.run(main())
```

**Check library version:**
```python
import nsgifts_api
print(nsgifts_api.__version__)
```

### 📂 Main Features

#### 🔑 User Management (`client.user`)
- `login(email, password)` - Authenticate and get access token
- `signup(username, email, password)` - Create new account
- `check_balance()` - Get current account balance
- `get_user_info()` - Get user profile information

#### 📦 Services (`client.services`)
- `get_all_services()` - Get complete service catalog
- `get_categories()` - Get all available categories
- `get_services_by_category(category_id)` - Get services by category

#### 📋 Order Management (`client.orders`)
- `create_order(service_id, quantity, custom_id, data)` - Create new order
- `pay_order(custom_id)` - Process payment for existing order
- `get_order_info(custom_id)` - Get detailed order information

#### 🎮 Steam Operations (`client.steam`)
- `calculate_steam_amount(amount)` - Calculate Steam amount from rubles
- `get_steam_currency_rate()` - Get current Steam exchange rates
- `calculate_steam_gift(sub_id, region)` - Calculate Steam gift price
- `create_steam_gift_order(friend_link, sub_id, region, gift_name, gift_description)` - Create Steam gift order
- `pay_steam_gift_order(custom_id)` - Pay for Steam gift order
- `get_steam_apps()` - Get all available Steam apps with pricing

#### 🌐 IP Whitelist (`client.ip_whitelist`)
- `add_ip_to_whitelist(ip)` - Add IP to whitelist
- `remove_ip_from_whitelist(ip)` - Remove IP from whitelist
- `list_whitelist_ips()` - Get all whitelisted IPs

### ⚙️ Configuration

The `ClientConfig` class provides a convenient way to configure the client with all necessary parameters:

```python
from nsgifts_api import ClientConfig

config = ClientConfig(
    base_url="https://api.ns.gifts",          # API base URL
    email="your_login",                       # Your email/login
    password="your_password",                 # Your password
    auto_auth=True,                           # Auto-authenticate on client start
    max_retries=3,                            # Max retry attempts
    request_timeout=30,                       # Request timeout (seconds)
    server_error_cooldown=300,                # Cooldown after server error
    token_refresh_buffer=300,                 # Token refresh buffer (seconds)
    enable_logging=True,                      # Enable logging
    log_level="INFO"                          # Log level
)
```

**Loading configuration from dict/JSON:**
```python
import json
from nsgifts_api import ClientConfig

# From JSON file
with open('config.json') as f:
    config_dict = json.load(f)
    
config = ClientConfig.from_dict(config_dict)
```

### 📘 Usage Examples

#### Authentication and User Info
```python
import asyncio
from nsgifts_api import NSGiftsClient, APIError

async def main():
    try:
        async with NSGiftsClient() as client:
            # Login
            login_result = await client.user.login("your_login", "your_password")
            print(f"Logged in, token valid until: {login_result.valid_thru}")
            print(f"User ID: {login_result.user_id}")
            
            # Get user info
            user_info = await client.user.get_user_info()
            print(f"Login: {user_info.login}")
            print(f"Balance: {user_info.balance}")
            
            # Check balance
            balance = await client.user.check_balance()
            print(f"Current balance: {balance}")

    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(main())
```

#### Working with Services and Orders
```python
import asyncio
from nsgifts_api import NSGiftsClient, APIAuthenticationError

async def order_example():
    try:
        async with NSGiftsClient() as client:
            # Authenticate
            await client.user.login("your_login", "your_password")
            
            # Get available categories
            categories = await client.services.get_categories()
            print(f"Categories: {categories}")
            
            # Get services in a category (example: category_id=1)
            services = await client.services.get_services_by_category(1)
            print(f"Services: {services}")
            
            # Create an order
            order = await client.orders.create_order(
                service_id=123,
                quantity=1.0,
                custom_id="my_order_001",
                data="additional_info"
            )
            print(f"Order created with ID: {order.custom_id}")
            print(f"Order status: {order.status}")
            print(f"Total price: {order.total}")
            
            # Pay for the order
            payment = await client.orders.pay_order("my_order_001")
            print(f"Payment status: {payment.status}")
            print(f"New balance: {payment.new_balance}")
            
            # Check order status
            order_info = await client.orders.get_order_info("my_order_001")
            print(f"Order status: {order_info.status}")
            print(f"Status message: {order_info.status_message}")
            
    except APIAuthenticationError:
        print("Authentication failed. Check your credentials.")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(order_example())
```

#### Error Handling
```python
from nsgifts_api import (
    NSGiftsClient, 
    APIError, 
    APIAuthenticationError, 
    APIConnectionError,
    APITimeoutError,
    APIServerError,
    APIClientError
)

async def robust_example():
    try:
        async with NSGiftsClient() as client:
            await client.user.login("login", "password")
            balance = await client.user.check_balance()
            print(f"Balance: {balance}")
            
    except APIAuthenticationError:
        print("Authentication failed - check credentials")
    except APIConnectionError:
        print("Connection error - check internet")
    except APITimeoutError:
        print("Request timed out - try again")
    except APIServerError:
        print("Server error - NS.Gifts API is having issues")
    except APIClientError:
        print("Client error - check your request")
    except APIError as e:
        print(f"General API error: {e}")
```

### ⚠️ Disclaimer

- This is an **unofficial library**. This client is not an official NS.Gifts product.
- I **do not collaborate** with NS.Gifts and have no relation to their service or company.
- The author **is not responsible** for any problems, losses, or damages arising from the use of this library.
- The library may stop working at any time due to changes in the NS.Gifts API.
- This library is provided "AS IS", without any warranties, express or implied.

### 📜 License

[MIT](LICENSE)

---

## Русская версия

Асинхронный Python-клиент для [NS.Gifts API](https://api.ns.gifts/docs).  
❗ Я не сотрудничаю и никак не связан с [NS.Gifts](https://wholesale.ns.gifts/). Этот клиент написан исключительно для удобства работы с API.

## 📌 Быстрый старт

#### Базовое использование
```python
import asyncio
from nsgifts_api import NSGiftsClient

async def main():
    async with NSGiftsClient() as client:
        # Авторизация
        login_result = await client.user.login("your_login", "your_password")
        print(f"Токен: {login_result.access_token}")

        # Проверка баланса
        balance = await client.user.check_balance()
        print(f"Баланс: {balance}")

        # Получение категорий
        categories = await client.services.get_categories()
        print(categories)

asyncio.run(main())
```

#### Использование конфигурации (Рекомендуется)
```python
import asyncio
from nsgifts_api import NSGiftsClient, ClientConfig

async def main():
    # Создание конфигурации с учетными данными
    config = ClientConfig(
        email="your_login",
        password="your_password",
        enable_logging=True
    )
    
    async with NSGiftsClient(config=config) as client:
        # Клиент уже авторизован!
        balance = await client.user.check_balance()
        print(f"Баланс: {balance}")
        
        user_info = await client.user.get_user_info()
        print(f"Имя пользователя: {user_info.username}")

asyncio.run(main())
```

**Проверка версии библиотеки:**
```python
import nsgifts_api
print(nsgifts_api.__version__)
```

---

## 📂 Основные возможности

#### 🔑 Управление пользователем (`client.user`)
- `login(email, password)` - Авторизация и получение токена доступа
- `signup(username, email, password)` - Создание нового аккаунта
- `check_balance()` - Получение текущего баланса аккаунта
- `get_user_info()` - Получение информации о профиле пользователя

#### 📦 Услуги (`client.services`)
- `get_all_services()` - Получение полного каталога услуг
- `get_categories()` - Получение всех доступных категорий
- `get_services_by_category(category_id)` - Получение услуг по категории

#### 📋 Управление заказами (`client.orders`)
- `create_order(service_id, quantity, custom_id, data)` - Создание нового заказа
- `pay_order(custom_id)` - Обработка платежа за существующий заказ
- `get_order_info(custom_id)` - Получение детальной информации о заказе

#### 🎮 Steam операции (`client.steam`)
- `calculate_steam_amount(amount)` - Расчет суммы Steam из рублей
- `get_steam_currency_rate()` - Получение текущих курсов обмена Steam
- `calculate_steam_gift(sub_id, region)` - Расчет цены подарка Steam
- `create_steam_gift_order(friend_link, sub_id, region, gift_name, gift_description)` - Создание заказа подарка Steam
- `pay_steam_gift_order(custom_id)` - Оплата заказа подарка Steam
- `get_steam_apps()` - Получение всех доступных приложений Steam с ценами

#### 🌐 IP Whitelist (`client.ip_whitelist`)
- `add_ip_to_whitelist(ip)` - Добавление IP в whitelist
- `remove_ip_from_whitelist(ip)` - Удаление IP из whitelist
- `list_whitelist_ips()` - Получение всех IP-адресов из whitelist

---

## ⚙️ Конфигурация

Класс `ClientConfig` предоставляет удобный способ настройки клиента со всеми необходимыми параметрами:

```python
from nsgifts_api import ClientConfig

config = ClientConfig(
    base_url="https://api.ns.gifts",          # Базовый URL API
    email="your_login",                       # Ваш email/логин
    password="your_password",                 # Ваш пароль
    auto_auth=True,                           # Автоматическая авторизация при запуске
    max_retries=3,                            # Максимальное количество попыток
    request_timeout=30,                       # Таймаут запроса (секунды)
    server_error_cooldown=300,                # Охлаждение после ошибки сервера
    token_refresh_buffer=300,                 # Буфер обновления токена (секунды)
    enable_logging=True,                      # Включить логирование
    log_level="INFO"                          # Уровень логирования
)
```

**Загрузка конфигурации из dict/JSON:**
```python
import json
from nsgifts_api import ClientConfig

# Из JSON файла
with open('config.json') as f:
    config_dict = json.load(f)
    
config = ClientConfig.from_dict(config_dict)
```

---

## 📘 Примеры использования

### Авторизация и информация о пользователе
```python
import asyncio
from nsgifts_api import NSGiftsClient, APIError

async def main():
    try:
        async with NSGiftsClient() as client:
            # Вход в систему
            login_result = await client.user.login("your_login", "your_password")
            print(f"Авторизован, токен действует до: {login_result.valid_thru}")
            print(f"ID пользователя: {login_result.user_id}")
            
            # Получение информации о пользователе
            user_info = await client.user.get_user_info()
            print(f"Имя пользователя: {user_info.username}")
            print(f"Баланс: {user_info.balance}")
            
            # Проверка баланса
            balance = await client.user.check_balance()
            print(f"Текущий баланс: {balance}")

    except APIError as e:
        print(f"Ошибка API: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

asyncio.run(main())
```

### Работа с услугами и заказами
```python
import asyncio
from nsgifts_api import NSGiftsClient, APIAuthenticationError

async def order_example():
    try:
        async with NSGiftsClient() as client:
            # Авторизация
            await client.user.login("your_login", "your_password")
            
            # Получение доступных категорий
            categories = await client.services.get_categories()
            print(f"Категории: {categories}")
            
            # Получение услуг в категории (пример: category_id=1)
            services = await client.services.get_services_by_category(1)
            print(f"Услуги: {services}")
            
            # Создание заказа
            order = await client.orders.create_order(
                service_id=123,
                quantity=1.0,
                custom_id="my_order_001",
                data="дополнительная_информация"
            )
            print(f"Заказ создан с ID: {order.custom_id}")
            print(f"Статус заказа: {order.status}")
            print(f"Общая цена: {order.total}")
            
            # Оплата заказа
            payment = await client.orders.pay_order("my_order_001")
            print(f"Статус платежа: {payment.status}")
            print(f"Новый баланс: {payment.new_balance}")
            
            # Проверка статуса заказа
            order_info = await client.orders.get_order_info("my_order_001")
            print(f"Статус заказа: {order_info.status}")
            print(f"Сообщение статуса: {order_info.status_message}")
            
    except APIAuthenticationError:
        print("Ошибка авторизации. Проверьте учетные данные.")
    except Exception as e:
        print(f"Ошибка: {e}")

asyncio.run(order_example())
```

### Обработка ошибок
```python
from nsgifts_api import (
    NSGiftsClient, 
    APIError, 
    APIAuthenticationError, 
    APIConnectionError,
    APITimeoutError,
    APIServerError,
    APIClientError
)

async def robust_example():
    try:
        async with NSGiftsClient() as client:
            await client.user.login("login", "password")
            balance = await client.user.check_balance()
            print(f"Баланс: {balance}")
            
    except APIAuthenticationError:
        print("Ошибка авторизации - проверьте учетные данные")
    except APIConnectionError:
        print("Ошибка соединения - проверьте интернет")
    except APITimeoutError:
        print("Время ожидания истекло - попробуйте еще раз")
    except APIServerError:
        print("Ошибка сервера - проблемы с NS.Gifts API")
    except APIClientError:
        print("Ошибка клиента - проверьте ваш запрос")
    except APIError as e:
        print(f"Общая ошибка API: {e}")
```
---

## ⚠️ Отказ от ответственности (Disclaimer)

- Это **неофициальная библиотека**. Данный клиент не является официальным продуктом NS.Gifts.
- Я **не сотрудничаю** с NS.Gifts и не имею отношения к их сервису или компании.
- Автор **не несет ответственности** за любые проблемы, убытки или ущерб, возникшие в результате использования данной библиотеки.
- Библиотека может перестать работать в любой момент из-за изменений в API NS.Gifts.
- Данная библиотека предоставляется "КАК ЕСТЬ", без каких-либо гарантий, явных или подразумеваемых.

---

## 📜 Лицензия

[MIT](LICENSE)
