# -*- coding: utf-8 -*-
from aiogram import F, Router, types

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram import F, Router, types
from loguru import logger  # Логирование с помощью loguru
from yookassa import Payment

from db.settings_db import save_payment_info_user, get_product_password
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import TelegramMaster_Search_GPT
from keyboards.payments_keyboards import payment_keyboard_telegram_master_search_gpt
from keyboards.user_keyboards import start_menu
from messages.messages import message_payment
from services.i18n import t
from system.dispatcher import bot
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from handlers.payments.products_goods_services import TelegramMaster_Commentator
from handlers.payments.products_goods_services import payment_installation
from keyboards.payments_keyboards import payment_yookassa_check_keyboard
from aiogram import F, Router, types
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from db.settings_db import save_payment_info, add_user_if_not_exists, is_user_in_db
from handlers.payments.generates_payment_data import generates_payment_data
from handlers.payments.products_goods_services import TelegramMaster_PRO
from keyboards.payments_keyboards import payment_yookassa_check_keyboard_custom
from system.dispatcher import ADMIN_CHAT_ID

router = Router(name=__name__)


@router.callback_query(F.data == "payment_yookassa_commentator")
async def payment_yookassa_program_com(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster_Commentator"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"Оплата: TelegramMaster_Commentator",  # Текст описания товара
        product_price=TelegramMaster_Commentator  # Цена товара в рублях
    )
    # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=message_payment(
            "TelegramMaster_Commentator",
            payment_url
        ),
        reply_markup=payment_yookassa_check_keyboard(payment_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("cccheck_pay"))
async def check_payment_com(callback_query: types.CallbackQuery):
    """Проверка платежа TelegramMaster_Commentator"""
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    payment_info = Payment.find_one(split_data[2])  # Проверьте статус платежа с помощью API yookassa
    logger.info(payment_info)

    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(
            generates_payment_data(
                callback_query=callback_query,
                payment_info=payment_info.id,
                product="TelegramMaster_Commentator",
                date=payment_info.captured_at
            )
        )
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=t(
                "tgmaster-commentator-payment-success",
                price=TelegramMaster_Commentator,
                password=get_product_password("TelegramMaster_Commentator"),  # Получаем пароль из базы данных
                footer_text=t("tgmaster-payment-footer")
            ),
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
                     f"Приобрел TelegramMaster_Commentator"
            )
    else:
        await bot.send_message(
            callback_query.message.chat.id,
            text=t("payment-not-completed")
        )


@router.callback_query(F.data.startswith("payment_yookassa_password_commentator_password"))
async def payment_url_handler_commentator_password(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты пароля от TelegramMaster-PRO"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"Пароль TelegramMaster_Commentator",  # Текст описания товара
        product_price=TelegramMaster_Commentator.get("price"),  # Цена товара в рублях
    )
    # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Проверить оплату (Юкасса)', callback_data=f"paymenst_passs_{payment_id}")],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ])
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=message_payment("Пароль TelegramMaster_Commentator", payment_url),
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("paymenst_passs"))
async def check_payments_commentator_password(callback_query: types.CallbackQuery, state: FSMContext):
    """Проверка платежа 'Пароль TelegramMaster_Commentator'"""
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    payment_info = Payment.find_one(split_data[2])  # Проверьте статус платежа с помощью API YooKassa
    logger.info(payment_info)

    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(
            generates_payment_data(
                callback_query=callback_query,
                payment_info=payment_info.id,
                product="Пароль TelegramMaster_Commentator",
                date=payment_info.captured_at
            )
        )
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=t(
                "tgmaster-commentator-password-payment-success",
                price=TelegramMaster_Commentator.get("price"),
                password=get_product_password("TelegramMaster_Commentator")  # Получаем пароль из базы данных
            ),
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
                     f"Приобрел пароль от TelegramMaster_Commentator"
            )
    else:
        await bot.send_message(
            callback_query.message.chat.id,
            text=t("payment-not-completed")
        )


@router.callback_query(F.data == "payment_yookassa_password")
async def payment_url_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты пароля от TelegramMaster-PRO"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"Пароль TelegramMaster-PRO",
        product_price=TelegramMaster_PRO.get("price")
    )
    # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
    keyboard = payment_yookassa_check_keyboard_custom(payment_id, "payment_pass")
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=message_payment("Пароль TelegramMaster-PRO", payment_url),
                           reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("payment_pass"))
async def check_payments(callback_query: types.CallbackQuery, state: FSMContext):
    """Проверка платежа 'Пароль обновления: TelegramMaster-PRO'"""
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    payment_info = Payment.find_one(split_data[2])  # Проверьте статус платежа с помощью API YooKassa
    logger.info(payment_info)

    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(
            generates_payment_data(
                callback_query=callback_query,
                payment_info=payment_info.id,
                product="Пароль TelegramMaster-PRO",
                date=payment_info.captured_at
            )
        )

        # Получаем пароль из базы данных
        password = get_product_password("TelegramMaster-PRO")
        caption = t(
            "tgmaster-pro-password-payment-success",
            price=TelegramMaster_PRO.get("price"),
            password=password
        )
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
                     f"Приобрел пароль от TelegramMaster-PRO"
            )
    else:
        await bot.send_message(
            callback_query.message.chat.id,
            text=t("payment-not-completed")
        )


@router.callback_query(F.data.startswith("payment_yookassa_program"))
async def payment_url_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster-PRO"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"Оплата: TelegramMaster-PRO",  # Текст описания товара
        product_price=TelegramMaster_PRO  # Цена товара в рублях
    )
    # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=message_payment(
            "TelegramMaster-PRO",
            payment_url
        ),
        reply_markup=payment_yookassa_check_keyboard_custom(
            payment_id,
            "checsk_payment"
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("checsk_payment"))
async def check_payment(callback_query: types.CallbackQuery, state: FSMContext):
    """"Проверка платежа TelegramMaster-PRO"""
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    payment_info = Payment.find_one(split_data[2])  # Проверьте статус платежа с помощью API yookassa
    logger.info(payment_info)

    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(
            generates_payment_data(
                callback_query=callback_query,
                payment_info=payment_info.id,
                product="TelegramMaster-PRO",
                date=payment_info.captured_at
            )
        )

        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=t(
                "tgmaster-pro-payment-success",
                price=TelegramMaster_PRO,
                password=get_product_password("TelegramMaster-PRO"),  # Получаем пароль из базы данных
                footer_text=t("tgmaster-payment-footer")
            ),
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
                     f"Приобрел TelegramMaster-PRO"
            )
    else:
        await bot.send_message(
            callback_query.message.chat.id,
            text=t("payment-not-completed")
        )


@router.callback_query(F.data == "payment_yookassa_Search_GPT")
async def payment_yookassa_telegram_master_search_gpt(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster-Search-GPT"""
    try:
        payment_url, payment_id = payment_yookassa_com(
            description_text=f"Оплата: TelegramMaster-Search-GPT",  # Текст описания товара
            product_price=TelegramMaster_Search_GPT  # Цена товара в рублях
        )
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=message_payment(
                product="TelegramMaster-Search-GPT",
                payment_url=payment_url
            ),
            reply_markup=payment_keyboard_telegram_master_search_gpt(payment_id),
            parse_mode="HTML"
        )
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
                first_name=callback_query.from_user.first_name,
                last_name=callback_query.from_user.last_name,
                username=callback_query.from_user.username,
                invoice_json=payment_info.id,
                product="TelegramMaster-Search-GPT",
                date=payment_info.captured_at,
                status="succeeded",
                price=TelegramMaster_Search_GPT
            )

            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=t(
                    "tgmaster-search-gpt-payment-success",
                    price=TelegramMaster_Search_GPT,
                    password=get_product_password("TelegramMaster_Search_GPT"),  # Получаем пароль из базы данных
                    footer_text=t("tgmaster-payment-footer")
                ),
                reply_markup=start_menu(),  # Отправляемся в главное меню
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                callback_query.message.chat.id,
                text=t("payment-not-completed")
            )
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data.startswith("payment_yookassa_training"))
async def payment_url_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster-PRO"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"Помощь в настройке ПО (консультация)",  # Текст описания товара
        product_price=payment_installation  # Цена товара в рублях
    )
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=message_payment(
            "Помощь в настройке ПО (консультация)",
            payment_url
        ),
        reply_markup=payment_yookassa_check_keyboard_custom(
            # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
            payment_id,
            "csheck_service"
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("csheck_service"))
async def check_payment_program_setup_service(callback_query: types.CallbackQuery, state: FSMContext):
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    # Проверьте статус платежа с помощью API yookassa
    payment_info = Payment.find_one(split_data[2])
    logger.info(payment_info)
    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(
            generates_payment_data(
                callback_query=callback_query,
                payment_info=payment_info.id,
                product="Помощь в настройке ПО (консультация)",
                date=payment_info.captured_at
            )
        )
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"Пользователь:\n"
                 f"ID {callback_query.from_user.id},\n"
                 f"Username: @{callback_query.from_user.username},\n"
                 f"Имя: {callback_query.from_user.first_name},\n"
                 f"Фамилия: {callback_query.from_user.last_name},\n\n"
                 f"Приобрел 'Помощь в настройке ПО (консультация)'"
        )
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=t("training-payment-success")
        )
    else:
        await bot.send_message(
            callback_query.message.chat.id,
            text=t("payment-not-completed")
        )
