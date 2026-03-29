# -*- coding: utf-8 -*-
import base64
import datetime  # Дата
import hashlib
import json
import uuid
from aiogram import F, Router, types
import aiohttp
from aiogram import types, F
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru
from aiogram import F, Router, types
from db.settings_db import save_payment_info_user
from handlers.payments.products_goods_services import TelegramMaster_Search_GPT
from keyboards.user_keyboards import start_menu
from messages.messages import message_check_payment
from system.dispatcher import bot, dp

router = Router(name=__name__)

# Оплата TelegramMaster-Search-GPT

product = "TelegramMaster-Search-GPT"


async def make_request(url: str, invoice_data: dict):
    encoded_data = base64.b64encode(json.dumps(invoice_data).encode("utf-8")).decode("utf-8")
    signature = hashlib.md5(f"{encoded_data}{settings.CRYPTOMUS_API_KEY}".encode("utf-8")).hexdigest()

    async with aiohttp.ClientSession(headers={
        "merchant": settings.CRYPTOMUS_MERCHANT_ID,
        "sign": signature,
    }) as session:
        async with session.post(url=url, json=invoice_data) as response:
            if not response.ok:
                raise ValueError(response.reason)

            return await response.json()


@dp.callback_query(F.data == "payment_crypta_Search_GPT")
async def payment_crypta_pas_program_handler_com(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster-Search-GPT"""
    try:
        invoice_data = await make_request(
            url="https://api.cryptomus.com/v1/payment",
            invoice_data={
                "amount": f"{TelegramMaster_Search_GPT}",  # Сумма оплаты в криптовалюте за TelegramMaster_Commentator
                "currency": "RUB",
                "order_id": str(uuid.uuid4())
            },
        )
        logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")

        # Создаем кнопку "Проверить оплату"
        check_payment_button = InlineKeyboardButton(
            text="Проверить оплату",
            callback_data=f"CheckPayTMSearchGPTCrypta_{invoice_data['result']['uuid']}"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
                                    f"🌐 Вы собираетесь приобрести <b>TelegramMaster-Search-GPT</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
                                    f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
                                    f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
                                    f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
                                    f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
                               reply_markup=keyboard,
                               parse_mode="HTML")
    except Exception as e:
        logger.exception(f"Ошибка в обработке оплаты TelegramMaster_Commentator: {e}")


# Обработчик для кнопки "Проверить оплату TelegramMaster-Search-GPT"
@dp.callback_query(F.data.startswith("CheckPayTMSearchGPTCrypta"))
async def check_invoice_paid_program_com_tm_search_gpt_crypta(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты TelegramMaster-Search-GPT"""
    invoice_uuid = callback_query.data.split("_")[1]  # Извлекаем UUID счета из callback_data
    logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты

    try:
        invoice_data = await make_request(
            url="https://api.cryptomus.com/v1/payment/info",
            invoice_data={"uuid": invoice_uuid},
        )
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON
            # Запись в базу данных пользователя, который оплатил счет в рублях
            save_payment_info_user(
                table_name="users_pay_search", user_id=callback_query.from_user.id,
                first_name=callback_query.from_user.first_name, last_name=callback_query.from_user.last_name,
                username=callback_query.from_user.username, invoice_json=invoice_json, product=product,
                date=datetime.datetime.now().strftime("%Y-%m-%d"), status="succeeded", price=TelegramMaster_Search_GPT
            )
            # Отправка пароля в Telegram пользователю
            await bot.send_document(
                chat_id=callback_query.from_user.id,
                document=FSInputFile("setting/password/TelegramMaster_Search_GPT/password.txt"),
                caption=message_check_payment(product_price=TelegramMaster_Search_GPT, product=product),
                reply_markup=start_menu()  # Отправляемся в главное меню
            )
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



