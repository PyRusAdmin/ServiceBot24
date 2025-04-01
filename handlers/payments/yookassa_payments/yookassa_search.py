# -*- coding: utf-8 -*-
from aiogram import types, F
from aiogram.types import FSInputFile
from loguru import logger  # Логирование с помощью loguru
from yookassa import Payment

from db.settings_db import save_payment_info_user
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import TelegramMaster_Search_GPT
from keyboards.payments_keyboards import payment_keyboard_telegram_master_search_gpt
from keyboards.user_keyboards import start_menu
from messages.messages import message_payment, message_check_payment
from system.dispatcher import bot, dp

# Оплата TelegramMaster-Search-GPT

product = "TelegramMaster-Search-GPT"


@dp.callback_query(F.data == "payment_yookassa_Search_GPT")
async def payment_yookassa_telegram_master_search_gpt(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster_Commentator"""
    try:
        payment_url, payment_id = payment_yookassa_com(
            description_text=f"Оплата: {product}",  # Текст описания товара
            product_price=TelegramMaster_Search_GPT  # Цена товара в рублях
        )
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=message_payment(product, payment_url),
                               reply_markup=payment_keyboard_telegram_master_search_gpt(payment_id),
                               parse_mode="HTML")
    except Exception as e:
        logger.exception(e)


@dp.callback_query(F.data.startswith("CheckPayTMSearchGPT"))
async def check_pay_telegram_master_search_gpt(callback_query: types.CallbackQuery):
    """"Проверка платежа TelegramMaster_Commentator"""
    try:
        split_data = callback_query.data.split("_")
        payment_info = Payment.find_one(split_data[1])  # Проверьте статус платежа с помощью API yookassa
        if payment_info.status == "succeeded":  # Обработка статуса платежа

            # Запись в базу данных пользователя, который оплатил счет в рублях
            save_payment_info_user(
                table_name="users_pay_search", user_id=callback_query.from_user.id,
                first_name=callback_query.from_user.first_name, last_name=callback_query.from_user.last_name,
                username=callback_query.from_user.username, invoice_json=payment_info.id, product=product,
                date=payment_info.captured_at, status="succeeded", price=TelegramMaster_Search_GPT
            )

            # Отправка пароля в Telegram пользователю
            await bot.send_document(
                chat_id=callback_query.from_user.id,
                document=FSInputFile("setting/password/TelegramMaster_Search_GPT/password.txt"),
                caption=message_check_payment(product_price=TelegramMaster_Search_GPT, product=product),
                reply_markup=start_menu()  # Отправляемся в главное меню
            )
        else:
            await bot.send_message(callback_query.message.chat.id, "Ошибка оплаты")
    except Exception as e:
        logger.exception(e)


def register_yookassa_telegram_master_search_gpt():
    """Регистрируем handlers для бота для оплаты TelegramMaster_Search_GPT"""
    dp.callback_query.register(check_pay_telegram_master_search_gpt)
    dp.callback_query.register(payment_yookassa_telegram_master_search_gpt)
