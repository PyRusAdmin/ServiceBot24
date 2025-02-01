import json
import sqlite3

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from loguru import logger  # Логирование с помощью loguru
from yookassa import Configuration, Payment

from handlers.payments.products_goods_services import payment_installation
from keyboards.pay_keyboards import purchasing_a_program_setup_service
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


@dp.callback_query(F.data.startswith("check_service"))
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
        conn = sqlite3.connect('setting/user_data.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_pay (user_id, first_name, last_name, username,
                                                                payment_info, product, date, payment_status)''')
        cursor.execute('''INSERT INTO users_pay (user_id, first_name, last_name, username, payment_info, 
                                                      product, date, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (callback_query.from_user.id,
                        callback_query.from_user.first_name,
                        callback_query.from_user.last_name,
                        callback_query.from_user.username, payment_info.id, product, date, payment_status))
        conn.commit()

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


@dp.callback_query(F.data == "purchasing_a_program_setup_service")
async def buy_program_setup_service(callback_query: types.CallbackQuery):
    url, payment = payment_yookassa_program_setup_service()
    payment_keyboard_key = purchasing_a_program_setup_service(url, payment)
    payment_mes = ("Оплатите услуги по настройке и консультации. \n\n"
                   "После завершения процесса оплаты, свяжитесь с администратором через личные сообщения, используя "
                   "указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=payment_mes,
                                reply_markup=payment_keyboard_key,
                                disable_web_page_preview=True)


def register_yookassa_training():
    """Регистрируем handlers для бота"""
    dp.message.register(buy_program_setup_service)
    dp.message.register(check_payment_program_setup_service)
