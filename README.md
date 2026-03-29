# ServiceBot24 — Бот для продаж услуг и поддержки пользователей

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)](https://docs.aiogram.dev/)

Бот для автоматизации продаж цифровых товаров, приёма платежей и поддержки пользователей.

## 📋 Возможности

- ✅ **Продажа цифровых товаров** (пароли, лицензии, доступы)
- ✅ **Приём платежей** через 3 системы:
    - 💳 **ЮKassa** (банковские карты РФ)
    - ₿ **Cryptomus** (криптовалюта)
    - ⭐ **Telegram Stars** (звезды Telegram)
- ✅ **Автоматическая выдача товара** после оплаты
- ✅ **ИИ-обработка пожеланий** (Groq API)
- ✅ **Админ-панель** с рассылкой и статистикой
- ✅ **Работа с группами** (удаление системных сообщений)
- ✅ **База данных пользователей** и история платежей
- ✅ **Логирование** действий

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

Или запустите файл `Установка.bat` (Windows)

### 2. Настройка окружения

Создайте файл `.env` в корне проекта:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=ваш_токен_бота

# Admin
ADMIN_CHAT_ID=ваш_chat_id

# Proxy (опционально, оставить пустым если не используется)
PROXY_USER=
PROXY_PASSWORD=
PROXY_PORT=
PROXY_IP=

# YooKassa
ACCOUNT_ID=ваш_account_id
SECRET_KEY=ваш_secret_key

# Cryptomus
CRYPTOMUS_API_KEY=ваш_api_key
CRYPTOMUS_MERCHANT_ID=ваш_merchant_id

# Groq AI (для обработки пожеланий)
GROQ_API_KEY=ваш_groq_api_key
```

### 3. Запуск бота

```bash
python main.py
```

Или запустите файл `Запуск.bat` (Windows)

## 📁 Структура проекта

```
ServiceBot24/
├── db/                         # Работа с базой данных
│   └── settings_db.py          # Функции для работы с SQLite
├── handlers/                   # Обработчики бота
│   ├── admin/                  # Админские команды
│   │   └── admin_handlers.py   # Рассылка, статистика, справка
│   ├── payments/               # Платежи
│   │   ├── cryptomus_payments/ # Оплата криптовалютой
│   │   ├── yookassa_payments/  # Оплата через ЮKassa
│   │   ├── telegram_stars_payments.py  # Оплата звездами
│   │   ├── payments.py         # Главное меню оплат
│   │   └── products_goods_services.py  # Цены на товары
│   ├── user/                   # Пользовательские команды
│   │   ├── ai_handlers.py      # ИИ-обработчик пожеланий
│   │   ├── user_handlers.py    # Команда /start
│   │   ├── user_account.py     # Личный кабинет
│   │   ├── fag_handlers.py     # FAQ
│   │   └── reference_handlers.py # Справочная информация
│   └── group_handlers.py       # Работа с группами
├── keyboards/                  # Клавиатуры
│   ├── user_keyboards.py       # Пользовательские клавиатуры
│   └── payments_keyboards.py   # Платежные клавиатуры
├── messages/                   # Тексты сообщений
├── setting/                    # Настройки
│   └── password/               # Пароли от продуктов
├── states/                     # FSM состояния
├── system/                     # Системные файлы
│   └── dispatcher.py           # Диспетчер бота
├── logs/                       # Логи бота
├── main.py                     # Точка входа
├── requirements.txt            # Зависимости
├── setup.py                    # Установка зависимостей
├── README.md                   # Документация
├── STARS_PAYMENT.md            # Документация по Stars
├── Запуск.bat                  # Скрипт запуска (Windows)
└── Установка.bat               # Скрипт установки (Windows)
```

## 👥 Команды для пользователей

| Команда  | Описание                  |
|----------|---------------------------|
| `/start` | Запуск бота, главное меню |
| `/id`    | Узнать ID пользователя    |

## 🔧 Админские команды

| Команда       | Описание                              | Доступ               |
|---------------|---------------------------------------|----------------------|
| `/admin_help` | Справка по админским командам         | Только ADMIN_CHAT_ID |
| `/broadcast`  | Рассылка сообщений всем пользователям | Только ADMIN_CHAT_ID |
| `/stats`      | Статистика пользователей бота         | Только ADMIN_CHAT_ID |

### Как использовать рассылку

1. Отправьте `/broadcast`
2. Введите текст сообщения (поддерживается HTML)
3. Бот отправит сообщение всем пользователям из базы `users_run`
4. Получите отчет о доставке

## 💰 Платежные системы

### 1. ЮKassa (банковские карты)

- Рубли РФ
- Автоматическая проверка оплаты
- Поддержка всех товаров

### 2. Cryptomus (криптовалюта)

- USDT, TON, BTC и др.
- Конвертация по курсу
- Автоматическая выдача товара

### 3. Telegram Stars (звезды)

- Внутренняя валюта Telegram
- **Курс:** 1 ⭐️ = 1.5 ₽ (настраивается)
- Мгновенная выдача товара

**Документация:** [STARS_PAYMENT.md](STARS_PAYMENT.md)

## 📦 Товары и услуги

| Товар                             | Цена (₽) | Stars (⭐️) |
|-----------------------------------|----------|------------|
| TelegramMaster-PRO                | 1600     | ~1067      |
| TelegramMaster_Commentator        | 1300     | ~867       |
| Пароль TelegramMaster-PRO         | 300      | ~50        |
| Пароль TelegramMaster_Commentator | 300      | ~50        |
| Настройка ПО                      | 800      | ~533       |
| TelegramMaster_Search_GPT         | 1000     | ~667       |

Цены настраиваются в `handlers/payments/products_goods_services.py`

## 🤖 ИИ-функции

Бот использует **Groq API** для:

- Обработки пожеланий пользователей
- Формирования структурированных запросов разработчикам

## 📊 База данных

SQLite база данных (`setting/user_data.db`) хранит:

- `users_run` — пользователи, запускавшие бота
- `users_pay` — история платежей
- `user_wishes` — пожелания пользователей
- `group_members` — участники групп

## 🔐 Безопасность

- Доступ к админским командам только для `ADMIN_CHAT_ID`
- Проверка подписки на канал перед выдачей пароля
- Логирование всех действий
- Валидация платежей

## 🛠️ Требования

- Python 3.10+
- aiogram 3.x
- SQLite
- Переменные окружения (через `.env`)

## 📝 Логи

Логи сохраняются в папку `logs/`:

- `log.log` — общая информация
- `log_ERROR.log` — ошибки

Ротация логов: 1 МБ, сжатие в ZIP

## 🔗 Ссылки

- [Документация Telegram Stars](https://core.telegram.org/bots/payments#telegram-stars)
- [ЮKassa API](https://yookassa.ru/developers/api)
- [Cryptomus API](https://developers.cryptomus.com/)
- [Groq API](https://console.groq.com/docs)

## 📞 Поддержка

- Telegram: [@PyAdminRU](https://t.me/PyAdminRU)
- Канал: [@master_tg_d](https://t.me/master_tg_d)

## 📄 Лицензия

Проект создан для внутреннего использования.

---

**Дата обновления:** 29 марта 2026 г.  
**Версия:** 2.0
