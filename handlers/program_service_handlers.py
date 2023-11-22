import json
import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger  # Логирование с помощью loguru
from yookassa import Configuration, Payment

from keyboards.pay_keyboards import purchasing_a_program_setup_service
from system.dispatcher import bot, dp, ACCOUNT_ID, SECRET_KEY


# 2200000000000004 - проверочная карта

class PaymentStates_program_setup_service:  # Define your FSM states if needed
    PROCESSING = "processing"


def payment_yookassa_program_setup_service():
    """Оплата Юкасса"""
    logger.info(f"ACCOUNT_ID: {ACCOUNT_ID}, SECRET_KEY {SECRET_KEY}")
    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY

    payment = Payment.create(
        {"amount": {"value": 1.00, "currency": "RUB"},"capture": True,
         "confirmation": {"type": "redirect", "return_url": "https://t.me/h24service_bot"},
         "description": "Помощь в настройке ПО (консультация)",
         "metadata": {'order_number': '1'},
         "receipt": {"customer": {"email": "zh.vitaliy92@yandex.ru"},
                     "items": [
                         {
                             "description": "Помощь в настройке ПО (консультация)",  # Название товара
                             "quantity": "1",
                             "amount": {"value": 1.00, "currency": "RUB"},  # Сумма и валюта
                             "vat_code": "1"}]}})

    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = (payment_data['confirmation'])['confirmation_url']
    logger.info(f"Ссылка для оплаты: {payment_url}, ID оплаты {payment_id}")
    return payment_url, payment_id


@dp.callback_query_handler(lambda c: c.data.startswith("check_payment"))
async def check_payment_program_setup_service(callback_query: types.CallbackQuery, state: FSMContext):
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    # Check the payment status using the YooKassa API
    payment_info = Payment.find_one(split_data[2])
    logger.info(payment_info)
    product = "Помощь в настройке ПО (консультация)"
    if payment_info.status == "succeeded":# Process the payment status
        payment_status = "succeeded"
        date = payment_info.captured_at
        logger.info(date)
        conn = sqlite3.connect('setting/user_data.db')
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users_pay (user_id,
                                                     first_name,
                                                     last_name,
                                                     username,
                                                     payment_info,
                                                     product,
                                                     date,
                                                     payment_status)''')
        cursor.execute(
            '''INSERT INTO users_pay (user_id, 
                                           first_name, 
                                           last_name, 
                                           username, 
                                           payment_info, 
                                           product, 
                                           date, 
                                           payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (callback_query.from_user.id,
             callback_query.from_user.first_name,
             callback_query.from_user.last_name,
             callback_query.from_user.username, payment_info.id, product, date, payment_status))
        conn.commit()
        await bot.send_message(callback_query.from_user.id, "Оплата прошла успешно‼️ \nДля согласования даты и времени , свяжитесь с администратором через личные сообщения, используя указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                                                            "Для возврата в начальное меню, нажмите: /start")
    else:
        await bot.send_message(callback_query.message.chat.id, "Payment failed.")


@dp.callback_query_handler(lambda c: c.data == "purchasing_a_program_setup_service")
async def buy_program_setup_service(callback_query: types.CallbackQuery, state: FSMContext):
    url, payment = payment_yookassa_program_setup_service()
    payment_keyboard_key = purchasing_a_program_setup_service(url, payment)
    payment_mes = ("Оплатите услуги по настройке и консультации. \n\n"
                   "После завершения процесса оплаты, свяжитесь с администратором через личные сообщения, используя указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)


def buy_handler_program_setup_service():
    """Регистрируем handlers для бота"""
    dp.register_message_handler(buy_program_setup_service)
