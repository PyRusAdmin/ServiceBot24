# -*- coding: utf-8 -*-

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru
from yookassa import Payment

from db.settings_db import save_payment_info, add_user_if_not_exists, is_user_in_db
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import TelegramMaster
from keyboards.user_keyboards import start_menu
from messages.messages import message_payment, message_check_payment
from system.dispatcher import bot, dp, ADMIN_CHAT_ID

# Оплата TelegramMaster 2.0

product = "TelegramMaster 2.0"


@dp.callback_query(F.data.startswith("payment_yookassa_program"))
async def payment_url_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster 2.0"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"Оплата: {product}",  # Текст описания товара
        product_price=TelegramMaster  # Цена товара в рублях
    )
    # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Проверить оплату (Юкасса)', callback_data=f"checsk_payment_{payment_id}")],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ])
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=message_payment(product, payment_url),
                           reply_markup=keyboard, parse_mode="HTML")


@dp.callback_query(F.data.startswith("checsk_payment"))
async def check_payment(callback_query: types.CallbackQuery, state: FSMContext):
    """"Проверка платежа TelegramMaster 2.0"""
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    payment_info = Payment.find_one(split_data[2])  # Проверьте статус платежа с помощью API yookassa
    logger.info(payment_info)
    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                          callback_query.from_user.last_name, callback_query.from_user.username, payment_info.id,
                          product, payment_info.captured_at, "succeeded")
        # Создайте файл, который вы хотите отправить
        await bot.send_document(
            chat_id=callback_query.from_user.id,
            document=FSInputFile("setting/password/TelegramMaster/password.txt"),
            caption=message_check_payment(product_price=TelegramMaster, product=product),
            reply_markup=start_menu()  # Отправляемся в главное меню
        )
        result = is_user_in_db(callback_query.from_user.id)
        if result is None:
            add_user_if_not_exists(callback_query.from_user.id)
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                               f"ID {callback_query.from_user.id},\n"
                                                               f"Username: @{callback_query.from_user.username},\n"
                                                               f"Имя: {callback_query.from_user.first_name},\n"
                                                               f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                               f"Приобрел TelegramMaster 2.0")
    else:
        await bot.send_message(callback_query.message.chat.id, "Payment failed.")


def register_yookassa_program():
    """Регистрируем handlers для бота"""
    # Оплата TelegramMaster
    dp.message.register(check_payment)
    dp.callback_query.register(payment_url_handler)
