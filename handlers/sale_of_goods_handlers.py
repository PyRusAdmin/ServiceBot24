from aiogram import types

from system.dispatcher import bot, dp

yoomoney_wallet = '381764678:TEST:71453'  # Инициализация Юмани
PRICE = types.LabeledPrice(label='Telegram_BOT_SMM', amount=1000 * 100)  # Цена товара


# Тестовая карта
# 1111 1111 1111 1026, 12/22, CVC 000

@dp.callback_query_handler(lambda c: c.data == "delivery")
async def buy(callback_query: types.CallbackQuery):
    yoomoney_wallet.split(':')[1]

    await bot.send_invoice(callback_query.message.chat.id,
                           title="Теlegram_BOT_SMM",  # Заголовок
                           description="Теlegram_BOT_SMM - программа для автоматизации действий в Telegram. Автоматизируй свой бизнес.",  # Описание
                           provider_token=yoomoney_wallet,
                           currency="rub",  # Валюта
                           photo_url='https://telegra.ph/file/8e89afa5a11de76d87359.png',
                           photo_width=435,
                           photo_height=333,
                           photo_size=435,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# Ваш обработчик успешной оплаты
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    # Создайте файл, который вы хотите отправить
    document_path = "setting/password/Telegram_SMM_BOT/password.txt"  # Укажите путь к вашему файлу
    caption = f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!"

    # Отправка файла
    with open(document_path, 'rb') as document:
        await bot.send_document(message.chat.id, document, caption=caption)

    # Отправка ссылки на программу
    await bot.send_message(message.chat.id, "Вы можете скачать программу https://t.me/master_tg_d/286")


def buy_handler():
    """Регистрируем handlers для бота"""
    dp.register_message_handler(buy)
