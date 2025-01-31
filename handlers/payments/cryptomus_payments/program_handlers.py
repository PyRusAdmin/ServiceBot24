import base64
import datetime  # Дата
import hashlib
import json
import sqlite3
import uuid

import aiohttp
from aiogram import types, F
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru

from db.settings_db import checking_for_presence_in_the_user_database
from handlers.payments.products_goods_services import TelegramMaster
from keyboards.user_keyboards import start_menu
from setting import settings
from system.dispatcher import bot, dp, ADMIN_CHAT_ID


async def make_request(url: str, invoice_data: dict):
    encoded_data = base64.b64encode(
        json.dumps(invoice_data).encode("utf-8")
    ).decode("utf-8")
    signature = hashlib.md5(f"{encoded_data}{settings.CRYPTOMUS_API_KEY}".
                            encode("utf-8")).hexdigest()

    async with aiohttp.ClientSession(headers={
        "merchant": settings.CRYPTOMUS_MERCHANT_ID,
        "sign": signature,
    }) as session:
        async with session.post(url=url, json=invoice_data) as response:
            if not response.ok:
                raise ValueError(response.reason)

            return await response.json()


@dp.callback_query(F.data == "payment_crypta_pas_program")
async def payment_crypta_pas_program_handler(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster 2.0 криптой"""

    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{TelegramMaster}",
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )
    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")

    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_payment_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
                                f"🌐 Вы собираетесь приобрести <b>TelegramMaster 2.0</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
                                f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
                                f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
                                f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
                                f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
                           reply_markup=keyboard,
                           parse_mode="HTML")


# Обработчик для кнопки "Проверить оплату TelegramMaster 2.0"
@dp.callback_query(F.data.startswith("check_payment_"))
async def check_invoice_paid_program(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    invoice_uuid = callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
    logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты

    try:
        invoice_data = await make_request(
            url="https://api.cryptomus.com/v1/payment/info",
            invoice_data={"uuid": invoice_uuid},
        )

        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            logger.info(date)

            conn = sqlite3.connect('setting/user_data.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users_pay (user_id, first_name, last_name, username, payment_info,
                                                                            product, date, payment_status)''')
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON
            cursor.execute('''INSERT INTO users_pay (user_id, first_name, last_name, username, payment_info, 
                                                                  product, date, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (callback_query.from_user.id,
                            callback_query.from_user.first_name,
                            callback_query.from_user.last_name,
                            callback_query.from_user.username, invoice_json, "TelegramaMaster 2.0", date, "succeeded"))
            conn.commit()

            # Создайте файл, который вы хотите отправить
            caption = (f"Платеж на сумму {TelegramMaster} руб прошел успешно‼️ \n\n"
                       f"Вы можете скачать программу TelegramaMaster 2.0\n\n"
                       f"Для возврата в начальное меню нажмите /start")

            inline_keyboard_markup = start_menu()  # Отправляемся в главное меню
            document = FSInputFile("setting/password/TelegramMaster/password.txt")

            await bot.send_document(chat_id=callback_query.from_user.id, document=document, caption=caption,
                                    reply_markup=inline_keyboard_markup)

            result = checking_for_presence_in_the_user_database(callback_query.from_user.id)

            if result is None:
                cursor.execute('INSERT INTO users (id) VALUES (?)', (callback_query.from_user.id,))
                conn.commit()

                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback_query.from_user.id},\n"
                                                                   f"Username: @{callback_query.from_user.username},\n"
                                                                   f"Имя: {callback_query.from_user.first_name},\n"
                                                                   f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                                   f"Приобрел TelegramMaster 2.0 (криптой)")

        else:
            # Если оплата еще не прошла
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ Платеж еще не оплачен. Пожалуйста, завершите оплату и нажмите кнопку 'Проверить оплату' еще раз."
            )

    except Exception as e:
        # Обработка ошибок
        logger.error(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )


def program_cry_register_message_handler():
    """Регистрируем handlers для бота"""
    dp.message.register(payment_crypta_pas_program_handler)
