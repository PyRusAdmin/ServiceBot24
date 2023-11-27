import sqlite3
import json
import datetime  # Дата
from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger  # Логирование с помощью loguru
from yookassa import Configuration, Payment
from system.dispatcher import bot, dp, ACCOUNT_ID, SECRET_KEY
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# 2200000000000004 - проверочная карта

class PaymentStates:  # Define your FSM states if needed
    PROCESSING = "processing"


def payment_yookassa():
    """Оплата Юкасса"""

    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY

    payment = Payment.create(
        {"amount": {"value": 500.00, "currency": "RUB"}, "capture": True,
         "confirmation": {"type": "redirect", "return_url": "https://t.me/h24service_bot"},
         "description": "Покупка программы: Тelegram_BOT_SMM",
         "metadata": {'order_number': '1'},
         "receipt": {"customer": {"email": "zh.vitaliy92@yandex.ru"},
                     "items": [
                         {
                             "description": "Покупка программы: Тelegram_BOT_SMM",  # Название товара
                             "quantity": "1",
                             "amount": {"value": 500.00, "currency": "RUB"},  # Сумма и валюта
                             "vat_code": "1"}]}})

    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = (payment_data['confirmation'])['confirmation_url']
    logger.info(f"Ссылка для оплаты: {payment_url}, ID оплаты {payment_id}")
    return payment_url, payment_id


def payment_keyboard(url, id_pay) -> InlineKeyboardMarkup:
    """Клавиатура оплаты"""
    payment_keyboard_key = InlineKeyboardMarkup()
    byy_baton = InlineKeyboardButton("💳 Оплатить 500 руб.", url=url)
    check_payment = InlineKeyboardButton('Проверить оплату', callback_data=f"check_payment_{id_pay}")
    payment_keyboard_key.row(byy_baton)
    payment_keyboard_key.row(check_payment)
    return payment_keyboard_key


@dp.callback_query_handler(lambda c: c.data.startswith("check_payment"))
async def check_payment(callback_query: types.CallbackQuery, state: FSMContext):
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    # Check the payment status using the YooKassa API
    payment_info = Payment.find_one(split_data[2])
    logger.info(payment_info)
    product = "Тelegram_BOT_SMM"
    # Process the payment status
    if payment_info.status == "succeeded":
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
        # Создайте файл, который вы хотите отправить
        document_path = "setting/password/Telegram_SMM_BOT/password.txt"  # Укажите путь к вашему файлу
        caption = (f"Платеж на сумму 500 руб прошел успешно‼️ \n\n"
                   f"Вы можете скачать программу https://t.me/master_tg_d/286\n\n"
                   f"Для возврата в начальное меню нажмите /start")
        # Отправка файла
        with open(document_path, 'rb') as document:
            await bot.send_document(callback_query.from_user.id, document, caption=caption)
        # Отправка ссылки на программу
    else:
        await bot.send_message(callback_query.message.chat.id, "Payment failed.")


@dp.callback_query_handler(lambda c: c.data == "delivery")
async def buy(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    # Проверка наличия записей для данного пользователя с определенным статусом заказа
    cursor.execute("SELECT * FROM users_pay WHERE user_id=? AND payment_status=?", (user_id, "succeeded"))
    result = cursor.fetchone()
    if result:
        # Пользователь уже делал покупку
        # Создайте файл, который вы хотите отправить
        document_path = "setting/password/Telegram_SMM_BOT/password.txt"  # Укажите путь к вашему файлу
        caption = (f"Вы можете скачать программу https://t.me/master_tg_d/292\n\n"
                   f"Для возврата в начальное меню нажмите /start")  # Отправка ссылки на программу
        # Отправка файла
        with open(document_path, 'rb') as document:
            await bot.send_document(callback_query.from_user.id, document, caption=caption)
    else:  # Пользователь не делал покупку
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        url, payment = payment_yookassa()
        payment_keyboard_key = payment_keyboard(url, payment)
        payment_mes = ("Купить Тelegram_BOT_SMM. \n\n"
                       "На момент тестирования автоматизирования платежей через Юкассу, скидка на программу 50%. \n\n"
                       f"Цена на {current_date} — 500 рублей. Скидка продлится до 30-11-2023. \n\n"
                       "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: @PyAdminRU. 🤖🔒\n\n"
                       "Для возврата в начальное меню, нажмите: /start")
        await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)


def buy_handler():
    """Регистрируем handlers для бота"""
    dp.register_message_handler(buy)
