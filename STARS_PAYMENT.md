# 💰 Оплата Telegram Stars

## Описание

Telegram Stars (звезды) — это внутренняя валюта Telegram для оплаты цифровых товаров и услуг.

## Как это работает

1. Пользователь выбирает товар/услугу
2. Бот выставляет счет в звездах (XTR)
3. Пользователь оплачивает через Telegram
4. Бот автоматически отправляет товар/пароль

## Конвертация рублей в звезды

Курс: **1 звезда = 1.5 рубля** (актуально на 2026 год)

Для изменения курса отредактируйте константу в файле:

```
handlers/payments/telegram_stars_payments.py
```

```python
STARS_TO_RUB_RATE = 1.5  # Измените на актуальный курс
```

## Доступные товары для оплаты звездами

| Товар                             | Цена (₽) | Примерно (⭐️) |
|-----------------------------------|----------|---------------|
| TelegramMaster-PRO                | 1600     | 1067 ⭐️       |
| TelegramMaster_Commentator        | 1300     | 867 ⭐️        |
| Пароль TelegramMaster-PRO         | 300      | 50 ⭐️         |
| Пароль TelegramMaster_Commentator | 300      | 50 ⭐️         |
| Настройка ПО                      | 800      | 533 ⭐️        |
| TelegramMaster_Search_GPT         | 1000     | 667 ⭐️        |

## Структура файлов

```
handlers/payments/
├── telegram_stars_payments.py    # Основной файл оплаты звездами
└── products_goods_services.py    # Цены на товары

keyboards/
└── payments_keyboards.py         # Клавиатуры с кнопками Stars
```

## Как добавить новый товар

1. Добавьте цену в `products_goods_services.py`:

         ```python
         Новый_Товар = 500.00
         ```

2. Добавьте обработчик в `telegram_stars_payments.py`:

       ```python
       @router.callback_query(F.data == "payment_stars_new_product")
       async def payment_stars_new_product_handler(callback_query: types.CallbackQuery):
           rub_price = Новый_Товар
           stars_amount = get_stars_amount(rub_price)
       
           await bot.send_invoice(
               chat_id=callback_query.message.chat.id,
               title="Новый Товар",
               description="Описание товара",
               payload=f"stars_new_{datetime.datetime.now().timestamp()}",
               provider_token="",
               currency="XTR",
               prices=[{"label": "Новый Товар", "amount": stars_amount}],
               start_parameter="stars_new",
               need_name=True,
               need_email=False,
               need_phone_number=False,
               need_shipping_address=False,
           )
       ```

3. Добавьте кнопку в `payments_keyboards.py`

4. Добавьте обработку в `process_successful_payment()`:

   ```python
   elif payload.startswith("stars_new_"):
   product_name = "Новый Товар"
   price = Новый_Товар
   password_file = "setting/password/Новый_Товар/password.txt"
   ```

## Автоматическая обработка платежей

Бот автоматически:

- ✅ Создает счет в звездах
- ✅ Обрабатывает успешную оплату
- ✅ Отправляет пароль пользователю
- ✅ Сохраняет информацию о платеже в БД
- ✅ Уведомляет администратора

## Тестирование

Для тестирования используйте тестовые аккаунты Telegram. Telegram не поддерживает тестовый режим для звезд в тестовых
ботах.

## Важные замечания

⚠️ **Минимальная сумма**: 50 звезд (требование Telegram)

⚠️ **Комиссия Telegram**: При оплате звездами Telegram удерживает комиссию

⚠️ **Вывод звезд**: Звезды можно конвертировать в TON или использовать для рекламы в Telegram

## Обновление курса

При изменении курса звезд:

1. Обновите `STARS_TO_RUB_RATE` в `telegram_stars_payments.py`
2. Перезапустите бота
3. Проверьте актуальность цен для пользователей

## Ссылки

- [Документация Telegram Stars](https://core.telegram.org/bots/payments#telegram-stars)
- [Telegram Stars FAQ](https://telegram.org/faq/stars)
