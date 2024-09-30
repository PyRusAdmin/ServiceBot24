import asyncio
import base64
import hashlib
import json
import uuid
import datetime  # Дата
import aiohttp
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from loguru import logger
import sqlite3
from db.settings_db import clear_amount, update_amount_db, read_amount_db
from keyboards.user_keyboards import start_menu
from setting import settings
from system.dispatcher import bot, ADMIN_CHAT_ID
from system.dispatcher import dp, form_router


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

@dp.callback_query(F.data == "payment_crypta_pas")
async def buy_handler(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster 2.0 криптой"""
    results = read_amount_db()
    logger.info(results)

    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{results}",
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )

    asyncio.create_task(check_invoice_paid(invoice_data['result']['uuid'], message=bot))

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f"Счет для оплаты: {invoice_data['result']['url']}",
                           reply_markup=start_menu())


async def check_invoice_paid(id: str, callback_query):
    """Проверка счета на оплаченность"""
    while True:
        invoice_data = await make_request(
            url="https://api.cryptomus.com/v1/payment/info",
            invoice_data={"uuid": id},
        )

        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):

            date = datetime.datetime.now().strftime("%Y-%m-%d")
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
            caption = (f"Платеж на сумму 150 руб прошел успешно‼️ \n\n"
                       f"Вы можете скачать программу TelegramaMaster 2.0\n\n"
                       f"Для возврата в начальное меню нажмите /start")

            inline_keyboard_markup = start_menu_keyboard()  # Отправляемся в главное меню
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
                                                                   f"Приобрел пароль от TelegramMaster 2.0")


            return
        else:
            logger.info("Счет еще не оплачен")

        await asyncio.sleep(10)


ADMIN_USER_IDS = [535185511]  # Список администраторов


class ServiceCreation(StatesGroup):
    enter_amount = State()


@form_router.message(Command("service_creation"))
async def service_creation_handler(message: Message, state: FSMContext):
    """Обработчик команды для создания услуги и написания цены (только для админа)"""
    logger.info(message.from_user.id)

    if message.from_user.id in ADMIN_USER_IDS:
        await message.reply("Введите сумму без копеек")
        await state.set_state(ServiceCreation.enter_amount)
    else:
        await message.reply("Вы не админ!")
        return


@form_router.message(ServiceCreation.enter_amount)
async def update_info(message: Message, state: FSMContext):
    """Обработчик текстовых сообщений для сохранения суммы в базу данных"""
    amount = message.text
    clear_amount() # Очистка базы данных
    update_amount_db(amount)  # Сохранение суммы в базу данных
    await message.reply("Сумма успешно обновлена в базе данных.")
    await state.clear()


def cry_register_message_handler():
    """Регистрируем handlers для бота"""
    dp.message.register(buy_handler)
    dp.message.register(service_creation_handler)