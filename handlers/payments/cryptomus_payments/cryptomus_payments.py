# -*- coding: utf-8 -*-
import base64
import datetime  # Дата
import hashlib
import json
import uuid

import aiohttp
from aiogram import F, Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru

from db.settings_db import (
    save_payment_info, add_user_if_not_exists, is_user_in_db, get_product_password, save_payment_info_user
)
from handlers.payments.products_goods_services import (
    TelegramMaster_Commentator, TelegramMaster, TelegramMaster_Search_GPT
)
from handlers.payments.products_goods_services import password_TelegramMaster_Commentator, password_TelegramMaster
from keyboards.user_keyboards import start_menu
from messages.messages import message_check_payment
from system.dispatcher import CRYPTOMUS_API_KEY, CRYPTOMUS_MERCHANT_ID, bot, ADMIN_CHAT_ID

router = Router(name=__name__)


async def make_request(url, invoice_data):
    """Отправка запроса к API Cryptomus"""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=invoice_data) as response:
            return await response.json()


async def get_payment_info(callback_query):
    """Получение информации о счете для оплаты криптовалютой"""
    return await make_request(
        url="https://api.cryptomus.com/v1/payment/info",
        invoice_data={
            "uuid": callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
        },
    )


async def format_payment_info(payment_info):
    """Форматирование информации о счете для оплаты криптовалютой"""
    return await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{payment_info}",  # Сумма оплаты в криптовалюте
            "currency": "RUB",  # Валюта
            "order_id": str(uuid.uuid4())  # Номер заказа
        },
    )


def keyboard_check_payment(callback_data_check_payment):
    """Кнопка для проверки оплаты"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Проверить оплату",
                    callback_data=callback_data_check_payment
                )
            ]
        ]
    )


@router.callback_query(F.data == "payment_crypta_pas_training_handler")
async def payment_crypta_pas_training_handler(callback_query: types.CallbackQuery):
    """Оплата установки и обучения криптой"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь приобрести <b>Помощь в настройке ПО (консультация)</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{format_payment_info(payment_info)['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard_check_payment(f"check_paymentT_{format_payment_info(payment_info)['result']['uuid']}"),
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentT_"))
async def check_invoice_paid_training(callback_query: types.CallbackQuery):
    """Проверка счета на оплаченность"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            save_payment_info(  # Запись в базу данных пользователя, который оплатил счет в крипте
                callback_query.from_user.id,
                callback_query.from_user.first_name,
                callback_query.from_user.last_name,
                callback_query.from_user.username,
                json.dumps(invoice_data),  # Преобразуем словарь в строку JSON
                "Помощь в настройке ПО (консультация)",
                datetime.datetime.now().strftime("%Y-%m-%d"),
                "succeeded"
            )
            await bot.send_message(callback_query.from_user.id,
                                   "Оплата прошла успешно‼️ \nДля согласования даты и времени , свяжитесь с администратором"
                                   " через личные сообщения, используя указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                                   "Для возврата в начальное меню, нажмите: /start")
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"Пользователь:\n"
                     f"ID {callback_query.from_user.id},\n"
                     f"Username: @{callback_query.from_user.username},\n"
                     f"Имя: {callback_query.from_user.first_name},\n"
                     f"Фамилия: {callback_query.from_user.last_name},\n\n"
                     f"Приобрел 'Помощь в настройке ПО (консультация)' (криптой)")
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


product_telegram_search = "TelegramMaster-Search-GPT"


@router.callback_query(F.data == "payment_crypta_Search_GPT")
async def payment_crypta_pas_program_handler_com(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster-Search-GPT"""
    try:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
                 f"🌐 Вы собираетесь приобрести <b>TelegramMaster-Search-GPT</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
                 f"🔗 <a href='{format_payment_info(payment_info)['result']['url']}'>Перейти к оплате</a>\n\n"
                 f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
                 f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
                 f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
            reply_markup=keyboard_check_payment(
                f"CheckPayTMSearchGPTCrypta_{format_payment_info(payment_info)['result']['uuid']}"),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.exception(f"Ошибка в обработке оплаты TelegramMaster_Commentator: {e}")


# Обработчик для кнопки "Проверить оплату TelegramMaster-Search-GPT"
@router.callback_query(F.data.startswith("CheckPayTMSearchGPTCrypta"))
async def check_invoice_paid_program_com_tm_search_gpt_crypta(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты TelegramMaster-Search-GPT"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            # Запись в базу данных пользователя, который оплатил счет в рублях
            save_payment_info_user(
                table_name="users_pay_search",
                user_id=callback_query.from_user.id,
                first_name=callback_query.from_user.first_name,
                last_name=callback_query.from_user.last_name,
                username=callback_query.from_user.username,
                invoice_json=json.dumps(invoice_data),  # Преобразуем словарь в строку JSON
                product=product_telegram_search,
                date=datetime.datetime.now().strftime("%Y-%m-%d"),
                status="succeeded",
                price=TelegramMaster_Search_GPT
            )
            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster_Search_GPT")

            caption = (f"✅ <b>Платеж на сумму {TelegramMaster_Search_GPT} руб прошел успешно‼️</b>\n\n"
                       f"📦 Продукт: <b>{product_telegram_search}</b>\n\n"
                       f"🔑 <b>Ваш пароль:</b>\n"
                       f"<code>{password}</code>\n\n"
                       f"{message_check_payment(product_price=TelegramMaster_Search_GPT, product=product_telegram_search)}")
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=caption,
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
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


"""Оплата TelegramMaster-PRO криптой"""

product_telegram_master_pros = "TelegramMaster-PRO"


@router.callback_query(F.data == "payment_crypta_pas_program")
async def payment_crypta_pas_program_handler(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster-PRO криптой"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь приобрести <b>TelegramMaster-PRO</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{format_payment_info(payment_info)['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard_check_payment(f"check_paymentP_{format_payment_info(payment_info)['result']['uuid']}"),
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату TelegramMaster-PRO"
@router.callback_query(F.data.startswith("check_paymentP_"))
async def check_invoice_paid_program(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(
                callback_query.from_user.id,
                callback_query.from_user.first_name,
                callback_query.from_user.last_name,
                callback_query.from_user.username,
                json.dumps(invoice_data),  # Преобразуем словарь в строку JSON
                "TelegramMaster-PRO",
                datetime.datetime.now().strftime("%Y-%m-%d"),
                "succeeded")

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster-PRO")

            caption = (f"✅ <b>Платеж на сумму {TelegramMaster} руб прошел успешно‼️</b>\n\n"
                       f"📦 Продукт: <b>{product_telegram_master_pros}</b>\n\n"
                       f"🔑 <b>Ваш пароль:</b>\n"
                       f"<code>{password}</code>\n\n"
                       f"{message_check_payment(product_price=TelegramMaster, product=product_telegram_master_pros)}")

            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=caption,
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )

            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback_query.from_user.id},\n"
                                                                   f"Username: @{callback_query.from_user.username},\n"
                                                                   f"Имя: {callback_query.from_user.first_name},\n"
                                                                   f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                                   f"Приобрел {product_telegram_master_pros} (криптой)")
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


"""Оплата пароля TelegramMaster-PRO криптой"""

product_telegram_master_pro = "Пароль TelegramMaster-PRO"


# Обработчик для создания счета и отправки кнопки "Проверить оплату"
@router.callback_query(F.data == "payment_crypta_pas")
async def buy_handler(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster-PRO криптой"""
    # Отправляем сообщение с кнопкой
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь получить пароль от <b>TelegramMaster-PRO</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{format_payment_info(payment_info)['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа нажмите кнопку 'Проверить оплату'.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard_check_payment(f"check_paymentPAS_{format_payment_info(payment_info)['result']['uuid']}"),
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentPAS_"))
async def check_payment_handler(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(
                callback_query.from_user.id,
                callback_query.from_user.first_name,
                callback_query.from_user.last_name,
                callback_query.from_user.username,
                json.dumps(invoice_data),  # Преобразуем словарь в строку JSON
                "Пароль TelegramMaster-PRO",
                datetime.datetime.now().strftime("%Y-%m-%d"),
                "succeeded"
            )

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster-PRO")

            caption = (f"✅ <b>Платеж на сумму {password_TelegramMaster} руб прошел успешно‼️</b>\n\n"
                       f"📦 Продукт: <b>{product_telegram_master_pro}</b>\n\n"
                       f"🔑 <b>Ваш пароль:</b>\n"
                       f"<code>{password}</code>\n\n"
                       f"{message_check_payment(product_price=password_TelegramMaster, product=product_telegram_master_pro)}")

            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=caption,
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )

            # Проверяем наличие пользователя в базе данных
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback_query.from_user.id},\n"
                                                                   f"Username: @{callback_query.from_user.username},\n"
                                                                   f"Имя: {callback_query.from_user.first_name},\n"
                                                                   f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                                   f"Приобрел пароль от TelegramMaster-PRO (криптой)")
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


"""Оплата пароля TelegramMaster_Commentator криптой"""


# Обработчик для создания счета и отправки кнопки "Проверить оплату"
@router.callback_query(F.data == "payment_crypta_commentator_pass")
async def buy_handler_commentator(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster_Commentator криптой"""
    # Отправляем сообщение с кнопкой
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь получить пароль от <b>TelegramMaster_Commentator</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{format_payment_info(payment_info)['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа нажмите кнопку 'Проверить оплату'.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard_check_payment(f"check_paymentPass_{format_payment_info(payment_info)['result']['uuid']}"),
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentPass_"))
async def check_payment_handler_commentator(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)

        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно

            save_payment_info(  # Запись в базу данных пользователя, который оплатил счет в крипте
                callback_query.from_user.id,
                callback_query.from_user.first_name,
                callback_query.from_user.last_name,
                callback_query.from_user.username,
                json.dumps(invoice_data),  # Преобразуем словарь в строку JSON
                "Пароль TelegramMaster_Commentator",
                datetime.datetime.now().strftime("%Y-%m-%d"),
                "succeeded"
            )
            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster_Commentator")
            caption = (
                f"✅ <b>Платеж на сумму {password_TelegramMaster_Commentator} руб прошел успешно‼️</b>\n\n"
                f"📦 Продукт: <b>Пароль TelegramMaster_Commentator</b>\n\n"
                f"🔑 <b>Ваш пароль:</b>\n"
                f"<code>{password}</code>\n\n"
                f"Для возврата в начальное меню нажмите /start"
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=caption,
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )

            # Проверяем наличие пользователя в базе данных
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"Пользователь:\n"
                         f"ID {callback_query.from_user.id},\n"
                         f"Username: @{callback_query.from_user.username},\n"
                         f"Имя: {callback_query.from_user.first_name},\n"
                         f"Фамилия: {callback_query.from_user.last_name},\n\n"
                         f"Приобрел пароль от TelegramMaster_Commentator (криптой)"
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


"""Оплата TelegramMaster_Commentator криптой"""

# Оплата TelegramMaster_Commentator
TelegramMaster_Commentator = "TelegramMaster_Commentator"


async def make_request(url: str, invoice_data: dict):
    encoded_data = base64.b64encode(json.dumps(invoice_data).encode("utf-8")).decode("utf-8")
    signature = hashlib.md5(f"{encoded_data}{CRYPTOMUS_API_KEY}".encode("utf-8")).hexdigest()

    async with aiohttp.ClientSession(headers={
        "merchant": CRYPTOMUS_MERCHANT_ID,
        "sign": signature,
    }) as session:
        async with session.post(url=url, json=invoice_data) as response:
            if not response.ok:
                raise ValueError(response.reason)

            return await response.json()


@router.callback_query(F.data == "payment_crypta_commentator")
async def payment_crypta_pas_program_handler_com(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster_Commentator криптой"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь приобрести <b>TelegramMaster_Commentator</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{format_payment_info(payment_info)['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard_check_payment(f"check_paymen_{format_payment_info(payment_info)['result']['uuid']}"),
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату TelegramMaster_Commentator"
@router.callback_query(F.data.startswith("check_paymen"))
async def check_invoice_paid_program_com(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(
                callback_query.from_user.id,
                callback_query.from_user.first_name,
                callback_query.from_user.last_name,
                callback_query.from_user.username,
                json.dumps(invoice_data),  # Преобразуем словарь в строку JSON
                "TelegramMaster_Commentator",
                datetime.datetime.now().strftime("%Y-%m-%d"),
                "succeeded"
            )

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster_Commentator")

            caption = (f"✅ <b>Платеж на сумму {TelegramMaster_Commentator} руб прошел успешно‼️</b>\n\n"
                       f"📦 Продукт: <b>{TelegramMaster_Commentator}</b>\n\n"
                       f"🔑 <b>Ваш пароль:</b>\n"
                       f"<code>{password}</code>\n\n"
                       f"{message_check_payment(product_price=TelegramMaster_Commentator, product=TelegramMaster_Commentator)}")

            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=caption,
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )

            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"Пользователь:\n"
                         f"ID {callback_query.from_user.id},\n"
                         f"Username: @{callback_query.from_user.username},\n"
                         f"Имя: {callback_query.from_user.first_name},\n"
                         f"Фамилия: {callback_query.from_user.last_name},\n\n"
                         f"Приобрел {TelegramMaster_Commentator} (криптой)"
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

# 564
