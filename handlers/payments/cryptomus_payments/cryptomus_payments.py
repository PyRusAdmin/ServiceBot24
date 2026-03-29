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
    TelegramMaster_Commentator, TelegramMaster, TelegramMaster_Search_GPT, payment_installation
)
from handlers.payments.products_goods_services import password_TelegramMaster_Commentator, password_TelegramMaster
from keyboards.user_keyboards import start_menu
from messages.messages import message_check_payment
from system.dispatcher import CRYPTOMUS_API_KEY, CRYPTOMUS_MERCHANT_ID
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)


@router.callback_query(F.data == "payment_crypta_pas_training_handler")
async def payment_crypta_pas_training_handler(callback_query: types.CallbackQuery):
    """Оплата установки и обучения криптой"""

    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{payment_installation}",
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )

    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")
    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_paymentT_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
                                f"🌐 Вы собираетесь приобрести <b>Помощь в настройке ПО (консультация)</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
                                f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
                                f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
                                f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
                                f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
                           reply_markup=keyboard,
                           parse_mode="HTML")


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentT_"))
async def check_invoice_paid_training(callback_query: types.CallbackQuery):
    """Проверка счета на оплаченность"""
    # invoice_uuid = callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
    # logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты
    try:
        # invoice_data = await make_request(
        #     url="https://api.cryptomus.com/v1/payment/info",
        #     invoice_data={"uuid": id},
        # )
        invoice_data = await get_invoice_data(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                              callback_query.from_user.last_name, callback_query.from_user.username, invoice_json,
                              "Помощь в настройке ПО (консультация)", date, "succeeded")
            await bot.send_message(callback_query.from_user.id,
                                   "Оплата прошла успешно‼️ \nДля согласования даты и времени , свяжитесь с администратором"
                                   " через личные сообщения, используя указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                                   "Для возврата в начальное меню, нажмите: /start")
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
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
@router.callback_query(F.data.startswith("CheckPayTMSearchGPTCrypta"))
async def check_invoice_paid_program_com_tm_search_gpt_crypta(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты TelegramMaster-Search-GPT"""
    # invoice_uuid = callback_query.data.split("_")[1]  # Извлекаем UUID счета из callback_data
    # logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты
    try:
        # invoice_data = await make_request(
        #     url="https://api.cryptomus.com/v1/payment/info",
        #     invoice_data={"uuid": invoice_uuid},
        # )
        invoice_data = await get_invoice_data(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON
            # Запись в базу данных пользователя, который оплатил счет в рублях
            save_payment_info_user(
                table_name="users_pay_search", user_id=callback_query.from_user.id,
                first_name=callback_query.from_user.first_name, last_name=callback_query.from_user.last_name,
                username=callback_query.from_user.username, invoice_json=invoice_json, product=product_telegram_search,
                date=datetime.datetime.now().strftime("%Y-%m-%d"), status="succeeded", price=TelegramMaster_Search_GPT
            )

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster_Search_GPT")

            if password:
                caption = (f"✅ <b>Платеж на сумму {TelegramMaster_Search_GPT} руб прошел успешно‼️</b>\n\n"
                           f"📦 Продукт: <b>{product_telegram_search}</b>\n\n"
                           f"🔑 <b>Ваш пароль:</b>\n"
                           f"<code>{password}</code>\n\n"
                           f"{message_check_payment(product_price=TelegramMaster_Search_GPT, product=product_telegram_search)}")
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

    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{TelegramMaster}",  # Сумма оплаты в криптовалюте за TelegramMaster
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )
    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")

    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_paymentP_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
                                f"🌐 Вы собираетесь приобрести <b>TelegramMaster-PRO</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
                                f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
                                f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
                                f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
                                f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
                           reply_markup=keyboard,
                           parse_mode="HTML")


# Обработчик для кнопки "Проверить оплату TelegramMaster-PRO"
@router.callback_query(F.data.startswith("check_paymentP_"))
async def check_invoice_paid_program(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # invoice_uuid = callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
    # logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты
    try:
        # invoice_data = await make_request(
        #     url="https://api.cryptomus.com/v1/payment/info",
        #     invoice_data={"uuid": invoice_uuid},
        # )
        invoice_data = await get_invoice_data(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                              callback_query.from_user.last_name, callback_query.from_user.username, invoice_json,
                              "TelegramMaster-PRO", date, "succeeded")

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster-PRO")

            if password:
                caption = (f"✅ <b>Платеж на сумму {TelegramMaster} руб прошел успешно‼️</b>\n\n"
                           f"📦 Продукт: <b>{product_telegram_master_pros}</b>\n\n"
                           f"🔑 <b>Ваш пароль:</b>\n"
                           f"<code>{password}</code>\n\n"
                           f"{message_check_payment(product_price=TelegramMaster, product=product_telegram_master_pros)}")
            else:
                caption = (f"✅ <b>Платеж на сумму {TelegramMaster} руб прошел успешно‼️</b>\n\n"
                           f"⚠️ <b>Внимание!</b> Пароль еще не установлен администратором.\n\n"
                           f"Пожалуйста, обратитесь к @PyAdminRU")

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

    # Создаем счет для оплаты
    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{password_TelegramMaster}",
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )
    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")
    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_paymentPAS_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    # Отправляем сообщение с кнопкой
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь получить пароль от <b>TelegramMaster-PRO</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа нажмите кнопку 'Проверить оплату'.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentPAS_"))
async def check_payment_handler(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # invoice_uuid = callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
    # logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты
    try:
        # invoice_data = await make_request(
        #     url="https://api.cryptomus.com/v1/payment/info",
        #     invoice_data={"uuid": invoice_uuid},
        # )
        invoice_data = await get_invoice_data(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON

            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                              callback_query.from_user.last_name, callback_query.from_user.username, invoice_json,
                              "Пароль TelegramMaster-PRO", date, "succeeded")

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster-PRO")

            if password:
                caption = (f"✅ <b>Платеж на сумму {password_TelegramMaster} руб прошел успешно‼️</b>\n\n"
                           f"📦 Продукт: <b>{product_telegram_master_pro}</b>\n\n"
                           f"🔑 <b>Ваш пароль:</b>\n"
                           f"<code>{password}</code>\n\n"
                           f"{message_check_payment(product_price=password_TelegramMaster, product=product_telegram_master_pro)}")
            else:
                caption = (f"✅ <b>Платеж на сумму {password_TelegramMaster} руб прошел успешно‼️</b>\n\n"
                           f"⚠️ <b>Внимание!</b> Пароль еще не установлен администратором.\n\n"
                           f"Пожалуйста, обратитесь к @PyAdminRU")

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

    # Создаем счет для оплаты
    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{password_TelegramMaster}",
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )
    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")
    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_paymentPass_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    # Отправляем сообщение с кнопкой
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь получить пароль от <b>TelegramMaster_Commentator</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа нажмите кнопку 'Проверить оплату'.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def get_invoice_data(callback_query):
    """Получение информации о счете для оплаты криптовалютой"""
    return await make_request(
        url="https://api.cryptomus.com/v1/payment/info",
        invoice_data={
            "uuid": callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
        },
    )


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentPass_"))
async def check_payment_handler_commentator(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # invoice_uuid = callback_query.data.split("_")[2]
    # logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты
    try:
        # invoice_data = await make_request(
        #     url="https://api.cryptomus.com/v1/payment/info",
        #     invoice_data={
        #         "uuid": callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
        #     },
        # )
        invoice_data = await get_invoice_data(callback_query)

        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            # date = datetime.datetime.now().strftime("%Y-%m-%d")
            # invoice_json = json.dumps(invoice_data)
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(
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

            # if password:
            caption = (
                f"✅ <b>Платеж на сумму {password_TelegramMaster_Commentator} руб прошел успешно‼️</b>\n\n"
                f"📦 Продукт: <b>Пароль TelegramMaster_Commentator</b>\n\n"
                f"🔑 <b>Ваш пароль:</b>\n"
                f"<code>{password}</code>\n\n"
                f"Для возврата в начальное меню нажмите /start"
            )
            # else:
            #     caption = (f"✅ <b>Платеж на сумму {password_TelegramMaster_Commentator} руб прошел успешно‼️</b>\n\n"
            #                f"⚠️ <b>Внимание!</b> Пароль еще не установлен администратором.\n\n"
            #                f"Пожалуйста, обратитесь к @PyAdminRU")
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

    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{TelegramMaster_Commentator}",  # Сумма оплаты в криптовалюте за TelegramMaster_Commentator
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )
    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")

    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_paymen_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
                                f"🌐 Вы собираетесь приобрести <b>TelegramMaster_Commentator</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
                                f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
                                f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
                                f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
                                f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
                           reply_markup=keyboard,
                           parse_mode="HTML")


# Обработчик для кнопки "Проверить оплату TelegramMaster_Commentator"
@router.callback_query(F.data.startswith("check_paymen"))
async def check_invoice_paid_program_com(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    # invoice_uuid = callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
    # logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты

    try:
        # invoice_data = await make_request(
        #     url="https://api.cryptomus.com/v1/payment/info",
        #     invoice_data={"uuid": invoice_uuid},
        # )
        invoice_data = await get_invoice_data(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                              callback_query.from_user.last_name, callback_query.from_user.username, invoice_json,
                              "TelegramMaster_Commentator", datetime.datetime.now().strftime("%Y-%m-%d"), "succeeded")

            # Получаем пароль из базы данных
            password = get_product_password("TelegramMaster_Commentator")

            if password:
                caption = (f"✅ <b>Платеж на сумму {TelegramMaster_Commentator} руб прошел успешно‼️</b>\n\n"
                           f"📦 Продукт: <b>{TelegramMaster_Commentator}</b>\n\n"
                           f"🔑 <b>Ваш пароль:</b>\n"
                           f"<code>{password}</code>\n\n"
                           f"{message_check_payment(product_price=TelegramMaster_Commentator, product=TelegramMaster_Commentator)}")
            else:
                caption = (f"✅ <b>Платеж на сумму {TelegramMaster_Commentator} руб прошел успешно‼️</b>\n\n"
                           f"⚠️ <b>Внимание!</b> Пароль еще не установлен администратором.\n\n"
                           f"Пожалуйста, обратитесь к @PyAdminRU")

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

# 656
