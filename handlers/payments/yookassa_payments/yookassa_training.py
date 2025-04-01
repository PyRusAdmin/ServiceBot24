# -*- coding: utf-8 -*-
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru
from yookassa import Payment

from db.settings_db import save_payment_info
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import payment_installation
from messages.messages import message_payment
from system.dispatcher import bot, dp, ADMIN_CHAT_ID

product = "Помощь в настройке ПО (консультация)"


@dp.callback_query(F.data.startswith("payment_yookassa_training"))
async def payment_url_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster 2.0"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"{product}",  # Текст описания товара
        product_price=payment_installation  # Цена товара в рублях
    )
    # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Проверить оплату (Юкасса)', callback_data=f"csheck_service_{payment_id}")],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ])
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=message_payment(product, payment_url),
                           reply_markup=keyboard, parse_mode="HTML")


@dp.callback_query(F.data.startswith("csheck_service"))
async def check_payment_program_setup_service(callback_query: types.CallbackQuery, state: FSMContext):
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    # Проверьте статус платежа с помощью API yookassa
    payment_info = Payment.find_one(split_data[2])
    logger.info(payment_info)
    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                          callback_query.from_user.last_name, callback_query.from_user.username, payment_info.id,
                          product, payment_info.captured_at, "succeeded")
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
