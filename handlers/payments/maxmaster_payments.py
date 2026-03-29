# -*- coding: utf-8 -*-
"""
Обработчики оплаты для MaxMaster
"""
import datetime
import json

from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from yookassa import Payment

from db.settings_db import add_user_if_not_exists, is_user_in_db, get_maxmaster_password, add_maxmaster_sale
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import MaxMaster
from keyboards.user_keyboards import start_menu
from messages.messages import message_payment, message_check_payment
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)

product = "MaxMaster"


@router.callback_query(F.data == "payment_yookassa_maxmaster")
async def payment_yookassa_maxmaster_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты MaxMaster через YooKassa"""
    try:
        payment_url, payment_id = payment_yookassa_com(
            description_text=f"Оплата: {product}",
            product_price=MaxMaster
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Проверить оплату (ЮKassa)', callback_data=f"check_maxmaster_{payment_id}")],
            [InlineKeyboardButton(text='🏠 В главное меню', callback_data='start_menu_keyboard')],
        ])
        
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=message_payment(product, payment_url),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.exception(f"Ошибка при создании оплаты MaxMaster: {e}")
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data.startswith("check_maxmaster_"))
async def check_maxmaster_payment(callback_query: types.CallbackQuery):
    """Проверка платежа MaxMaster"""
    try:
        payment_id = callback_query.data.split("_")[2]
        payment_info = Payment.find_one(payment_id)
        
        if payment_info.status == "succeeded":
            # Запись в базу данных
            add_maxmaster_sale(
                user_id=callback_query.from_user.id,
                username=callback_query.from_user.username,
                first_name=callback_query.from_user.first_name,
                last_name=callback_query.from_user.last_name,
                payment_amount=MaxMaster,
                payment_method="yookassa"
            )
            
            # Получаем пароль из БД
            password = get_maxmaster_password()
            
            if password:
                caption = (f"✅ <b>Платеж на сумму {MaxMaster} руб прошел успешно‼️</b>\n\n"
                           f"📦 Продукт: <b>{product}</b>\n\n"
                           f"🔑 <b>Ваш пароль от архива:</b>\n"
                           f"<code>{password}</code>\n\n"
                           f"{message_check_payment(product_price=MaxMaster, product=product)}")
            else:
                caption = (f"✅ <b>Платеж на сумму {MaxMaster} руб прошел успешно‼️</b>\n\n"
                           f"⚠️ <b>Внимание!</b> Пароль еще не установлен администратором.\n\n"
                           f"Пожалуйста, обратитесь к @PyAdminRU")
            
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=caption,
                reply_markup=start_menu(),
                parse_mode="HTML"
            )
            
            # Уведомляем админа
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
            
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"📦 <b>Новая продажа MaxMaster!</b>\n\n"
                     f"👤 Пользователь:\n"
                     f"• ID: {callback_query.from_user.id}\n"
                     f"• Username: @{callback_query.from_user.username}\n"
                     f"• Имя: {callback_query.from_user.first_name}\n"
                     f"• Фамилия: {callback_query.from_user.last_name}\n\n"
                     f"💰 Сумма: {MaxMaster} ₽ (YooKassa)\n"
                     f"🕒 Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ Платеж еще не оплачен. Пожалуйста, завершите оплату и нажмите кнопку 'Проверить оплату' еще раз."
            )
    except Exception as e:
        logger.exception(f"Ошибка при проверке оплаты MaxMaster: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )
