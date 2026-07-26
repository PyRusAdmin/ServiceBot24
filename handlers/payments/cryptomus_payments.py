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
    save_payment_info, add_user_if_not_exists, is_user_in_db, get_product_password
)
from handlers.payments.generates_payment_data import generates_payment_data
from handlers.payments.products_goods_services import (
    TelegramMaster_Commentator, TelegramMaster_PRO, TelegramMaster_Search_GPT, payment_installation
)
from keyboards.user_keyboards import start_menu
from messages.messages import message_check_payment
from services.i18n import t
from system.dispatcher import CRYPTOMUS_API_KEY, CRYPTOMUS_MERCHANT_ID, bot, ADMIN_CHAT_ID

router = Router(name=__name__)


async def make_request(url: str, invoice_data: dict):
    """Отправка запроса к API Cryptomus"""
    async with aiohttp.ClientSession(headers={
        "merchant": CRYPTOMUS_MERCHANT_ID,
        "sign": hashlib.md5(
            f"{base64.b64encode(json.dumps(invoice_data).encode("utf-8")).decode("utf-8")}{CRYPTOMUS_API_KEY}".encode(
                "utf-8")).hexdigest(),
    }) as session:
        async with session.post(url=url, json=invoice_data) as response:
            if not response.ok:
                raise ValueError(response.reason)

            return await response.json()


async def get_payment_info(callback_query):
    """Получение информации о счете для оплаты криптовалютой"""
    return await make_request(
        url="https://api.cryptomus.com/v1/payment/info",
        invoice_data={
            "uuid": callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
        },
    )


async def format_payment_info(amount):
    """Форматирование информации о счете для оплаты криптовалютой"""
    return await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{amount}",  # Сумма оплаты в криптовалюте
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


def message_payment_fo_admin(callback_query, name_goods):
    """
    Сообщение админу о том, что пользователь оплатил счет

    :param callback_query: CallbackQuery - объект callback_query
    :param name_goods: str - название товара
    """
    return (
        f"Пользователь:\n"
        f"ID {callback_query.from_user.id},\n"
        f"Username: @{callback_query.from_user.username},\n"
        f"Имя: {callback_query.from_user.first_name},\n"
        f"Фамилия: {callback_query.from_user.last_name},\n\n"
        f"Приобрел {name_goods}"
    )


def message_payment_for_user(payment_info, name_goods):
    """
    Сообщение пользователю о том, что он оплатил счет

    :param payment_info: dict - информация о счете
    :param callback_query: CallbackQuery - объект callback_query
    :param name_goods: str - название товара
    """
    return (
        f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
        f"🌐 Вы собираетесь приобрести <b>{name_goods}</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
        f"🔗 <a href='{format_payment_info(payment_info)['result']['url']}'>Перейти к оплате</a>\n\n"
        f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
        f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
        f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
    )


@router.callback_query(F.data == "payment_crypta_pas_training_handler")
async def payment_crypta_pas_training_handler(callback_query: types.CallbackQuery):
    """Оплата установки и обучения криптой"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=message_payment_for_user(
            payment_info=payment_installation,
            name_goods="Помощь в настройке ПО (консультация)",
        ),
        reply_markup=keyboard_check_payment(
            f"check_paymentT_{format_payment_info(payment_installation)['result']['uuid']}"),
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
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(
                generates_payment_data(
                    callback_query=callback_query,
                    payment_info=json.dumps(invoice_data),
                    product="Помощь в настройке ПО (консультация)",
                    date=datetime.datetime.now().strftime("%Y-%m-%d")
                )
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Оплата прошла успешно‼️ \nДля согласования даты и времени , свяжитесь с администратором"
                     " через личные сообщения, используя указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                     "Для возврата в начальное меню, нажмите: /start"
            )
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=message_payment_fo_admin(
                    callback_query=callback_query,
                    name_goods="Помощь в настройке ПО (консультация)' (криптой)"
                )
            )
        else:
            # Если оплата еще не прошла
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=t("payment-not-completed")
            )
    except Exception as e:
        # Обработка ошибок
        logger.exception(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == "payment_crypta_Search_GPT")
async def payment_crypta_pas_program_handler_com(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster-Search-GPT"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=message_payment_for_user(
            payment_info=TelegramMaster_Search_GPT,
            name_goods="TelegramMaster-Search-GPT",
        ),
        reply_markup=keyboard_check_payment(
            f"CheckPayTMSearchGPTCrypta_{format_payment_info(TelegramMaster_Search_GPT)['result']['uuid']}"),
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату TelegramMaster-Search-GPT"
@router.callback_query(F.data.startswith("CheckPayTMSearchGPTCrypta"))
async def check_invoice_paid_program_com_tm_search_gpt_crypta(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты TelegramMaster-Search-GPT"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(
                generates_payment_data(
                    callback_query=callback_query,
                    payment_info=json.dumps(invoice_data),
                    product="TelegramMaster-Search-GPT",
                    date=datetime.datetime.now().strftime("%Y-%m-%d")
                )
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=(
                    f"✅ <b>Платеж на сумму {TelegramMaster_Search_GPT} руб прошел успешно‼️</b>\n\n"
                    f"📦 Продукт: <b>TelegramMaster-Search-GPT</b>\n\n"
                    f"🔑 <b>Ваш пароль:</b>\n"
                    f"<code>{get_product_password("TelegramMaster_Search_GPT")}</code>\n\n"
                    f"{message_check_payment(product_price=TelegramMaster_Search_GPT, product="TelegramMaster-Search-GPT")}"
                ),
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )
        else:
            # Если оплата еще не прошла
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=t("payment-not-completed")
            )
    except Exception as e:
        # Обработка ошибок
        logger.exception(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == "payment_crypta_pas_program")
async def payment_crypta_pas_program_handler(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster-PRO криптой"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=message_payment_for_user(
            payment_info=TelegramMaster_PRO.get("price"),
            name_goods=TelegramMaster_PRO.get("name"),
        ),
        reply_markup=keyboard_check_payment(
            f"check_paymentP_{format_payment_info(TelegramMaster_PRO)['result']['uuid']}"
        ),
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
                generates_payment_data(
                    callback_query=callback_query,
                    payment_info=json.dumps(invoice_data),
                    product="TelegramMaster-PRO",
                    date=datetime.datetime.now().strftime("%Y-%m-%d")
                )
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=(
                    f"✅ <b>Платеж на сумму {TelegramMaster_PRO} руб прошел успешно‼️</b>\n\n"
                    f"📦 Продукт: <b>TelegramMaster-PRO</b>\n\n"
                    f"🔑 <b>Ваш пароль:</b>\n"
                    f"<code>{get_product_password("TelegramMaster-PRO")}</code>\n\n"
                    f"{message_check_payment(product_price=TelegramMaster_PRO, product="TelegramMaster-PRO")}"
                ),
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=message_payment_fo_admin(
                        callback_query=callback_query,
                        name_goods="TelegramMaster-PRO (криптой)"
                    )
                )
        else:
            # Если оплата еще не прошла
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=t("payment-not-completed")
            )
    except Exception as e:
        # Обработка ошибок
        logger.exception(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )


# Обработчик для создания счета и отправки кнопки "Проверить оплату"
@router.callback_query(F.data == "payment_crypta_pas")
async def buy_handler(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster-PRO криптой"""
    # Отправляем сообщение с кнопкой
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=message_payment_for_user(
            payment_info=TelegramMaster_PRO.get("price_password"),
            name_goods=TelegramMaster_PRO.get("name_password"),
        ),
        reply_markup=keyboard_check_payment(
            f"check_paymentPAS_{format_payment_info(TelegramMaster_PRO.get("price_password"))['result']['uuid']}"),
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentPAS_"))
async def check_payment_handler(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты пароля TelegramMaster-PRO"""
    # Проверяем статус оплаты
    try:
        invoice_data = await get_payment_info(callback_query)
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(
                generates_payment_data(
                    callback_query=callback_query,
                    payment_info=json.dumps(invoice_data),
                    product=TelegramMaster_PRO.get("name_password"),
                    date=datetime.datetime.now().strftime("%Y-%m-%d")
                )
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=(
                    f"✅ <b>Платеж на сумму {TelegramMaster_PRO.get("price_password")} руб прошел успешно‼️</b>\n\n"
                    f"📦 Продукт: <b>Пароль TelegramMaster-PRO</b>\n\n"
                    f"🔑 <b>Ваш пароль:</b>\n"
                    f"<code>{get_product_password("TelegramMaster-PRO")}</code>\n\n"
                    f"{message_check_payment(product_price=TelegramMaster_PRO.get("price_password"), product=TelegramMaster_PRO.get("name_password"))}"
                ),
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )
            # Проверяем наличие пользователя в базе данных
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=message_payment_fo_admin(
                        callback_query=callback_query,
                        name_goods="TelegramMaster-PRO (криптой)"
                    )
                )
            else:
                # Если оплата еще не прошла
                await bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=t("payment-not-completed")
                )
    except Exception as e:
        # Обработка ошибок
        logger.exception(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )


# Обработчик для создания счета и отправки кнопки "Проверить оплату"
@router.callback_query(F.data == "payment_crypta_commentator_pass")
async def buy_handler_commentator(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster-Commentator криптой"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=message_payment_for_user(
            payment_info=TelegramMaster_Commentator.get("price_password"),
            name_goods="TelegramMaster-Commentator",
        ),
        reply_markup=keyboard_check_payment(
            f"check_paymentPass_{format_payment_info(TelegramMaster_Commentator.get("price_password"))['result']['uuid']}"),
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
            save_payment_info(
                generates_payment_data(
                    callback_query=callback_query,
                    payment_info=json.dumps(invoice_data),
                    product="Пароль TelegramMaster_Commentator",
                    date=datetime.datetime.now().strftime("%Y-%m-%d")
                )
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=(
                    f"✅ <b>Платеж на сумму {TelegramMaster_Commentator.get("price_password")} руб прошел успешно‼️</b>\n\n"
                    f"📦 Продукт: <b>Пароль TelegramMaster_Commentator</b>\n\n"
                    f"🔑 <b>Ваш пароль:</b>\n"
                    f"<code>{get_product_password("TelegramMaster_Commentator")}</code>\n\n"
                    f"Для возврата в начальное меню нажмите /start"
                ),
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )
            # Проверяем наличие пользователя в базе данных
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=message_payment_fo_admin(
                        callback_query=callback_query,
                        name_goods="пароль от TelegramMaster_Commentator (криптой)"
                    )
                )
            else:
                # Если оплата еще не прошла
                await bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=t("payment-not-completed")
                )
    except Exception as e:
        # Обработка ошибок
        logger.exception(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == "payment_crypta_commentator")
async def payment_crypta_pas_program_handler_com(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster_Commentator криптой"""
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=message_payment_for_user(
            payment_info=TelegramMaster_Commentator,
            name_goods="TelegramMaster_Commentator",
        ),
        reply_markup=keyboard_check_payment(
            f"check_paymen_{format_payment_info(TelegramMaster_Commentator)['result']['uuid']}"),
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
                generates_payment_data(
                    callback_query=callback_query,
                    payment_info=json.dumps(invoice_data),
                    product="TelegramMaster_Commentator",
                    date=datetime.datetime.now().strftime("%Y-%m-%d")
                )
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=(
                    f"✅ <b>Платеж на сумму {TelegramMaster_Commentator} руб прошел успешно‼️</b>\n\n"
                    f"📦 Продукт: <b>{TelegramMaster_Commentator}</b>\n\n"
                    f"🔑 <b>Ваш пароль:</b>\n"
                    f"<code>{get_product_password("TelegramMaster_Commentator")}</code>\n\n"
                    f"{message_check_payment(product_price=TelegramMaster_Commentator, product=TelegramMaster_Commentator)}"
                ),
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=message_payment_fo_admin(
                        callback_query=callback_query,
                        name_goods="TelegramMaster_Commentator (криптой)"
                    )
                )
        else:
            # Если оплата еще не прошла
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=t("payment-not-completed")
            )
    except Exception as e:
        # Обработка ошибок
        logger.exception(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )

# 543
