import datetime  # Дата
import json
import sqlite3

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from loguru import logger  # Логирование с помощью loguru
from yookassa import Configuration, Payment

from handlers.user_handlers.user_handlers import checking_for_presence_in_the_user_database
from keyboards.user_keyboards import payment_keyboard
from system.dispatcher import bot, dp, ACCOUNT_ID, SECRET_KEY, ADMIN_CHAT_ID


class PaymentStates:  # Define your FSM states if needed
    PROCESSING = "processing"


def payment_yookassa():
    """Оплата Юкасса"""

    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY

    payment = Payment.create(
        {"amount": {"value": 1.00, "currency": "RUB"}, "capture": True,
         "confirmation": {"type": "redirect", "return_url": "https://t.me/h24service_bot"},
         "description": "Покупка программы: ТelegramMaster",
         "metadata": {'order_number': '1'},
         "receipt": {"customer": {"email": "zh.vitaliy92@yandex.ru"},
                     "items": [
                         {
                             "description": "Покупка программы: ТelegramMaster",  # Название товара
                             "quantity": "1",
                             "amount": {"value": 1.00, "currency": "RUB"},  # Сумма и валюта
                             "vat_code": "1"}]}})

    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = (payment_data['confirmation'])['confirmation_url']
    logger.info(f"Ссылка для оплаты: {payment_url}, ID оплаты {payment_id}")
    return payment_url, payment_id


@dp.callback_query(F.data.startswith("check_payment"))
async def check_payment(callback_query: types.CallbackQuery, state: FSMContext):
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    # Check the payment status using the YooKassa API
    payment_info = Payment.find_one(split_data[2])
    logger.info(payment_info)
    product = "TelegramaMaster"
    # Process the payment status
    if payment_info.status == "succeeded":
        payment_status = "succeeded"
        date = payment_info.captured_at
        logger.info(date)
        conn = sqlite3.connect('setting/user_data.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_pay (user_id, first_name, last_name, username, payment_info,
                                                                product, date, payment_status)''')
        cursor.execute('''INSERT INTO users_pay (user_id, first_name, last_name, username, payment_info, 
                                                      product, date, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (callback_query.from_user.id,
                        callback_query.from_user.first_name,
                        callback_query.from_user.last_name,
                        callback_query.from_user.username, payment_info.id, product, date, payment_status))
        conn.commit()
        # Создайте файл, который вы хотите отправить
        # document_path = "setting/password/Telegram_SMM_BOT/password.txt"  # Укажите путь к вашему файлу
        caption = (f"Платеж на сумму 1000 руб прошел успешно‼️ \n\n"
                   f"Вы можете скачать программу https://t.me/master_tg_d/286\n\n"
                   f"Для возврата в начальное меню нажмите /start")
        document = FSInputFile("setting/password/Telegram_SMM_BOT/password.txt")
        await bot.send_document(chat_id=callback_query.from_user.id, document=document, caption=caption)

        result = checking_for_presence_in_the_user_database(callback_query.from_user.id)

        if result is None:
            cursor.execute('INSERT INTO users (id) VALUES (?)', (callback_query.from_user.id,))
            conn.commit()

            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                               f"ID {callback_query.from_user.id},\n"
                                                               f"Username: @{callback_query.from_user.username},\n"
                                                               f"Имя: {callback_query.from_user.first_name},\n"
                                                               f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                               f"Приобрел TelegramMaster")  # ID пользователя нет в базе данных
    else:
        await bot.send_message(callback_query.message.chat.id, "Payment failed.")


def database(user_id):
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    # Проверка наличия записей для данного пользователя с определенным статусом заказа
    cursor.execute("SELECT * FROM users_pay WHERE user_id=? AND payment_status=?", (user_id, "succeeded"))
    result = cursor.fetchone()
    return result


@dp.callback_query(F.data == "delivery")
async def buy(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    result = database(user_id)
    if result:
        # Пользователь уже делал покупку
        # Создайте файл, который вы хотите отправить
        document = FSInputFile('setting/password/Telegram_SMM_BOT/password.txt')
        caption = (f"Вы можете скачать программу https://t.me/master_tg_d/292\n\n"
                   f"Для возврата в начальное меню нажмите /start")  # Отправка ссылки на программу
        # Отправка файла
        await bot.send_document(chat_id=user_id, document=document, caption=caption)
    else:  # Пользователь не делал покупку
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        url, payment = payment_yookassa()
        payment_keyboard_key = payment_keyboard(url, payment)
        payment_mes = ("Купить ТelegramMaster. \n\n"
                       f"Цена на {current_date} — 1000 рублей.\n\n"
                       "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                       "@PyAdminRU. 🤖🔒\n\n"
                       "Для возврата в начальное меню, нажмите: /start")
        await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)


def buy_handler():
    """Регистрируем handlers для бота"""
    dp.message.register(buy)
    dp.message.register(check_payment)

