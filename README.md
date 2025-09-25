# nsgifts (Unofficial NS.Gifts API Client)

[🇷🇺 Русский](#русская-версия) | [🇺🇸 English](#english-version)

---

## English Version

Asynchronous Python client for [NS.Gifts API](https://api.ns.gifts/docs).  
❗ I do not collaborate and am not affiliated with [NS.Gifts](https://wholesale.ns.gifts/). This client is written solely for convenience when working with the API.

### 🚀 Installation

```bash
pip install nsgifts
```

### 📌 Quick Start

```python
import asyncio
from nsgifts_api import NSGiftsClient

async def main():
    async with NSGiftsClient() as client:
        # Authentication
        await client.user.login("your_login", "your_password")

        # Check balance
        balance = await client.user.check_balance()
        print(balance)

        # Get categories
        categories = await client.services.get_categories()
        print(categories)

asyncio.run(main())
```

### 📂 Main Features

#### 🔑 User Management (`client.user`)
- `login(login, password)` - Authenticate and get access token
- `signup(login, password, bybit_deposit)` - Create new account
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
- Steam gift calculations and ordering
- Steam package price lookups

#### 🌐 IP Whitelist (`client.ip_whitelist`)
- IP address whitelist management

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
            print(f"Logged in, token valid until: {login_result['valid_thru']}")
            
            # Get user info
            user_info = await client.user.get_user_info()
            print(f"User Info: {user_info}")
            
            # Check balance
            balance = await client.user.check_balance()
            print(f"Balance: {balance}")

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
            print(f"Order created: {order}")
            
            # Pay for the order
            payment = await client.orders.pay_order("my_order_001")
            print(f"Payment result: {payment}")
            
            # Check order status
            order_info = await client.orders.get_order_info("my_order_001")
            print(f"Order info: {order_info}")
            
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
- Use at your own risk.

### 📜 License

[MIT](LICENSE)

---

## Русская версия

Асинхронный Python-клиент для [NS.Gifts API](https://api.ns.gifts/docs).  
❗ Я не сотрудничаю и никак не связан с [NS.Gifts](https://wholesale.ns.gifts/). Этот клиент написан исключительно для удобства работы с API.

---

## 🚀 Установка

```bash
pip install nsgifts
```

---

## 📌 Быстрый старт

```python
import asyncio
from nsgifts_api import NSGiftsClient

async def main():
    async with NSGiftsClient() as client:
        # Авторизация
        await client.user.login("your_login", "your_password")

        # Проверка баланса
        balance = await client.user.check_balance()
        print(balance)

        # Получение категорий
        categories = await client.services.get_categories()
        print(categories)

asyncio.run(main())
```

---

## 📂 Основные возможности

#### 🔑 Управление пользователем (`client.user`)
- `login(login, password)` - Авторизация и получение токена доступа
- `signup(login, password, bybit_deposit)` - Создание нового аккаунта
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
- Расчеты и заказ Steam подарков
- Поиск цен Steam пакетов

#### 🌐 IP Whitelist (`client.ip_whitelist`)
- Управление whitelist IP-адресов

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
            print(f"Авторизован, токен действует до: {login_result['valid_thru']}")
            
            # Получение информации о пользователе
            user_info = await client.user.get_user_info()
            print(f"Информация о пользователе: {user_info}")
            
            # Проверка баланса
            balance = await client.user.check_balance()
            print(f"Баланс: {balance}")

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
            print(f"Заказ создан: {order}")
            
            # Оплата заказа
            payment = await client.orders.pay_order("my_order_001")
            print(f"Результат платежа: {payment}")
            
            # Проверка статуса заказа
            order_info = await client.orders.get_order_info("my_order_001")
            print(f"Информация о заказе: {order_info}")
            
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
- Используйте на свой страх и риск.

---

## 📜 Лицензия

[MIT](LICENSE)