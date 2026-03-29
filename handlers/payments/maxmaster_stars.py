# -*- coding: utf-8 -*-
"""
Обработчики оплаты MaxMaster через Telegram Stars
"""
import datetime
import json

from aiogram import F, Router, types
from loguru import logger

from db.settings_db import get_maxmaster_password, add_maxmaster_sale
from handlers.payments.products_goods_services import MaxMaster
from handlers.payments.telegram_stars_payments import get_stars_amount
from keyboards.user_keyboards import start_menu
from messages.messages import message_check_payment
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)

product = "MaxMaster"


@router.callback_query(F.data == "payment_stars_maxmaster")
async def payment_stars_maxmaster_handler(callback_query: types.CallbackQuery):
    """Оплата MaxMaster звездами"""
    rub_price = MaxMaster
    stars_amount = get_stars_amount(rub_price)
    
    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="MaxMaster",
            description="Программа для перебора номеров на наличие регистрации в Max",
            payload=f"stars_maxmaster_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="MaxMaster", amount=stars_amount)],
            start_parameter="stars_maxmaster",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )
        
        logger.info(f"Создан инвойс для MaxMaster: {stars_amount} звезд, пользователь {callback_query.from_user.id}")
        
    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса MaxMaster: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )


@router.pre_checkout_query(F.data.source == "stars_maxmaster")
async def process_pre_checkout_query_maxmaster(pre_checkout_query: types.PreCheckoutQuery):
    """Обработка предоплаченного инвойса MaxMaster"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment_maxmaster(message: types.Message):
    """Обработка успешной оплаты MaxMaster звездами"""
    try:
        payment_data = message.successful_payment
        payload = payment_data.invoice_payload
        
        # Проверяем, что это оплата MaxMaster
        if not payload.startswith("stars_maxmaster_"):
            return
        
        logger.info(f"Успешная оплата MaxMaster звездами: {payload}, сумма: {payment_data.total_amount} звезд")
        
        # Сохраняем информацию о продаже
        add_maxmaster_sale(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            payment_amount=MaxMaster,
            payment_method="stars"
        )
        
        # Получаем пароль из БД
        password = get_maxmaster_password()
        
        if password:
            caption = (f"✅ <b>Оплата подтверждена!</b>\n\n"
                       f"📦 Продукт: <b>{product}</b>\n\n"
                       f"🔑 <b>Ваш пароль от архива:</b>\n"
                       f"<code>{password}</code>\n\n"
                       f"{message_check_payment(product_price=MaxMaster, product=product)}")
        else:
            caption = (f"✅ <b>Оплата подтверждена!</b>\n\n"
                       f"⚠️ <b>Внимание!</b> Пароль еще не установлен администратором.\n\n"
                       f"Пожалуйста, обратитесь к @PyAdminRU")
        
        await bot.send_message(
            chat_id=message.from_user.id,
            text=caption,
            reply_markup=start_menu(),
            parse_mode="HTML"
        )
        
        logger.info(f"Пароль MaxMaster отправлен пользователю {message.from_user.id}")
        
        # Уведомляем администратора
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"⭐️ <b>Новая оплата MaxMaster звездами!</b>\n\n"
                 f"👤 Пользователь:\n"
                 f"• ID: {message.from_user.id}\n"
                 f"• Username: @{message.from_user.username}\n"
                 f"• Имя: {message.from_user.first_name}\n"
                 f"• Фамилия: {message.from_user.last_name}\n\n"
                 f"📦 Продукт: {product}\n"
                 f"💰 Сумма: {payment_data.total_amount} ⭐️ ({MaxMaster} ₽)\n"
                 f"🕒 Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.exception(f"Ошибка при обработке оплаты MaxMaster звездами: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке платежа. Обратитесь к @PyAdminRU")
