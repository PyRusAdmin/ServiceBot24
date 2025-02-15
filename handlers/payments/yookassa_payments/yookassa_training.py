import json

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru
from yookassa import Configuration, Payment

from db.settings_db import save_payment_info
from handlers.payments.products_goods_services import payment_installation
from system.dispatcher import bot, dp, ACCOUNT_ID, SECRET_KEY, ADMIN_CHAT_ID


def payment_yookassa_program_setup_service():
    """Оплата yookassa"""
    logger.info(f"ACCOUNT_ID: {ACCOUNT_ID}, SECRET_KEY {SECRET_KEY}")
    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY

    payment = Payment.create(
        {"amount": {"value": payment_installation,  # Сумма за установку ПО
                    "currency": "RUB"}, "capture": True,
         "confirmation": {"type": "redirect", "return_url": "https://t.me/h24service_bot"},
         "description": "Помощь в настройке ПО (консультация)",
         "metadata": {'order_number': '1'},
         "receipt": {"customer": {"email": "zh.vitaliy92@yandex.ru"},
                     "items": [
                         {
                             "description": "Помощь в настройке ПО (консультация)",  # Название товара
                             "quantity": "1",
                             "amount": {"value": payment_installation,
                                        "currency": "RUB"},  # Сумма и валюта
                             "vat_code": "1"}]}})

    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = (payment_data['confirmation'])['confirmation_url']
    logger.info(f"Ссылка для оплаты: {payment_url}, ID оплаты {payment_id}")
    return payment_url, payment_id


@dp.callback_query(F.data.startswith("payment_yookassa_training"))
async def payment_url_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster 2.0"""
    payment_url, payment_id = payment_yookassa_program_setup_service()

    messages = (
        "💳 <b>Оплата установки и настройки ПО:</b>\n\n"
        f"Для оплаты перейдите по ссылке: {payment_url}\n\n"
        "🔔 <b>Важно:</b>\n"
        "1. Ссылка действительна <b>9 минут</b>. Если время истекло, зайдите в это меню заново.\n"
        "2. Оплата осуществляется через безопасную платежную систему <b>Юкасса</b>.\n"
        "3. После завершения процесса оплаты, свяжитесь с администратором через личные сообщения, используя "
        "указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
        "🔄 После оплаты нажмите кнопку <b>«Проверить оплату»</b>, чтобы убедится, что оплата прошла успешно."
    )

    # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Проверить оплату (Юкасса)', callback_data=f"csheck_service_{payment_id}")],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ])

    await bot.send_message(chat_id=callback_query.from_user.id, text=messages, reply_markup=keyboard, parse_mode="HTML")


@dp.callback_query(F.data.startswith("csheck_service"))
async def check_payment_program_setup_service(callback_query: types.CallbackQuery, state: FSMContext):
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    # Проверьте статус платежа с помощью API yookassa
    payment_info = Payment.find_one(split_data[2])
    logger.info(payment_info)
    product = "Помощь в настройке ПО (консультация)"
    if payment_info.status == "succeeded":  # Обработка статуса платежа
        payment_status = "succeeded"
        date = payment_info.captured_at
        logger.info(date)

        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                          callback_query.from_user.last_name, callback_query.from_user.username, payment_info.id,
                          product, date, payment_status)

        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                           f"ID {callback_query.from_user.id},\n"
                                                           f"Username: @{callback_query.from_user.username},\n"
                                                           f"Имя: {callback_query.from_user.first_name},\n"
                                                           f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                           f"Приобрел 'Помощь в настройке ПО (консультация)'")

        await bot.send_message(callback_query.from_user.id,
                               "Оплата прошла успешно‼️ \nДля согласования даты и времени , свяжитесь с администратором"
                               " через личные сообщения, используя указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                               "Для возврата в начальное меню, нажмите: /start")
    else:
        await bot.send_message(callback_query.message.chat.id, "Payment failed.")


def register_yookassa_training():
    """Регистрируем handlers для бота"""
    dp.message.register(check_payment_program_setup_service)
    dp.message.register(payment_url_handler)
