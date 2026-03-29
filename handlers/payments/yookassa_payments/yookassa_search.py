# -*- coding: utf-8 -*-
from aiogram import F, Router, types
from loguru import logger  # Логирование с помощью loguru
from yookassa import Payment

from db.settings_db import save_payment_info_user, get_product_password
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import TelegramMaster_Search_GPT
from keyboards.payments_keyboards import payment_keyboard_telegram_master_search_gpt
from keyboards.user_keyboards import start_menu
from messages.messages import message_payment, message_check_payment
from system.dispatcher import bot

router = Router(name=__name__)


@router.callback_query(F.data == "payment_yookassa_Search_GPT")
async def payment_yookassa_telegram_master_search_gpt(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster-Search-GPT"""
    try:
        payment_url, payment_id = payment_yookassa_com(
            description_text=f"Оплата: TelegramMaster-Search-GPT",  # Текст описания товара
            product_price=TelegramMaster_Search_GPT  # Цена товара в рублях
        )
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=message_payment(product="TelegramMaster-Search-GPT", payment_url=payment_url),
                               reply_markup=payment_keyboard_telegram_master_search_gpt(payment_id),
                               parse_mode="HTML")
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data.startswith("CheckPayTMSearchGPT"))
async def check_pay_telegram_master_search_gpt(callback_query: types.CallbackQuery):
    """"Проверка платежа TelegramMaster-Search-GPT"""
    try:
        split_data = callback_query.data.split("_")
        payment_info = Payment.find_one(split_data[1])  # Проверьте статус платежа с помощью API yookassa

        if payment_info.status == "succeeded":  # Обработка статуса платежа
            # Запись в базу данных пользователя, который оплатил счет в рублях
            save_payment_info_user(
                table_name="users_pay_search", user_id=callback_query.from_user.id,
                first_name=callback_query.from_user.first_name, last_name=callback_query.from_user.last_name,
                username=callback_query.from_user.username, invoice_json=payment_info.id,
                product="TelegramMaster-Search-GPT",
                date=payment_info.captured_at, status="succeeded", price=TelegramMaster_Search_GPT
            )

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster_Search_GPT")

            if password:
                caption = (f"✅ <b>Платеж на сумму {TelegramMaster_Search_GPT} руб прошел успешно‼️</b>\n\n"
                           f"📦 Продукт: <b>TelegramMaster-Search-GPT</b>\n\n"
                           f"🔑 <b>Ваш пароль:</b>\n"
                           f"<code>{password}</code>\n\n"
                           f"{message_check_payment(product_price=TelegramMaster_Search_GPT, product="TelegramMaster-Search-GPT")}")
            else:
                caption = (f"✅ <b>Платеж на сумму {TelegramMaster_Search_GPT} руб прошел успешно‼️</b>\n\n"
                           f"⚠️ <b>Внимание!</b> Пароль еще не установлен администратором.\n\n"
                           f"Пожалуйста, обратитесь к @PyAdminRU")

            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=caption,
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )
        else:
            await bot.send_message(callback_query.message.chat.id,
                                   "❌ Платеж еще не оплачен. Пожалуйста, завершите оплату и нажмите кнопку 'Проверить оплату' еще раз.")
    except Exception as e:
        logger.exception(e)
