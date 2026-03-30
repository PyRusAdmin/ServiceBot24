# -*- coding: utf-8 -*-
import datetime  # Дата

from aiogram import F, Router, types
from loguru import logger  # Логирование с помощью loguru

from db.settings_db import check_user_payment, is_user_in_db
from handlers.payments.products_goods_services import (
    TelegramMaster_PRO, payment_installation, TelegramMaster_Commentator,
    TelegramMaster_Search_GPT, MaxMaster, SERVER_RENT_PRICE
)
from keyboards.payments_keyboards import (
    payment_keyboard, payment_keyboard_password, payment_keyboard_com,
    payment_yookassa_password_commentator_password_keyboard, payment_keyboard_telegram_master_search_gpt_1,
    payment_keyboard_maxmaster, payment_keyboard_server_rent, purchasing_a_program_setup_service
)
from services.i18n import t
from system.dispatcher import ADMIN_CHAT_ID
from system.dispatcher import bot

router = Router(name=__name__)


@router.callback_query(F.data == "delivery")
async def buy(callback_query: types.CallbackQuery):
    """Покупка TelegramMaster-PRO"""
    payment_keyboard_key = payment_keyboard()
    payment_mes = ("Купить TelegramMaster-PRO.\n\n"
                   f"Цена на — {TelegramMaster_PRO} рублей.\n\n"
                   "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                   "@PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)


@router.callback_query(F.data == "delivery_telegrammaster_search_gpt")
async def buy_com(callback_query: types.CallbackQuery):
    """Покупка TelegramMaster_Search_GPT"""
    payment_mes = ("Купить TelegramMaster_Search_GPT.\n\n"
                   f"Цена на — {TelegramMaster_Search_GPT} рублей.\n\n"
                   "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                   "@PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes,
                           reply_markup=payment_keyboard_telegram_master_search_gpt_1())


@router.callback_query(F.data == "delivery_com")
async def buy_com(callback_query: types.CallbackQuery):
    """Покупка TelegramMaster_Commentator"""
    payment_mes = ("Купить TelegramMaster_Commentator.\n\n"
                   f"Цена на — {TelegramMaster_Commentator} рублей.\n\n"
                   "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                   "@PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_com())


@router.callback_query(F.data == "purchasing_a_program_setup_service")
async def buy_program_setup_service(callback_query: types.CallbackQuery):
    """Оплата услуг по установке ПО"""
    payment_keyboard_key = purchasing_a_program_setup_service()
    payment_mes = ("Оплатите услуги по настройке и консультации.\n\n"
                   f"Цена на — {payment_installation} рублей.\n\n"
                   "После завершения процесса оплаты, свяжитесь с администратором через личные сообщения, используя "
                   "указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=payment_mes,
                                reply_markup=payment_keyboard_key,
                                disable_web_page_preview=True)


@router.callback_query(F.data == "delivery_maxmaster")
async def buy_maxmaster(callback_query: types.CallbackQuery):
    """Покупка MaxMaster"""
    payment_keyboard_key = payment_keyboard_maxmaster()
    await bot.send_message(
        callback_query.message.chat.id,
        text=t("maxmaster-buy-info", price=MaxMaster),
        reply_markup=payment_keyboard_key
    )


@router.callback_query(F.data == "delivery_server_rent")
async def buy_server_rent(callback_query: types.CallbackQuery):
    """Аренда сервера"""
    payment_keyboard_key = payment_keyboard_server_rent()
    await bot.send_message(
        callback_query.message.chat.id,
        text=t("server-rent-info", price=SERVER_RENT_PRICE),
        reply_markup=payment_keyboard_key,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "commentator_password")
async def get_password_tg_com(callback: types.CallbackQuery):
    """Проверка подписки на канал, бот обязательно должен быть админом, ссылка в виде: @master_tg_d"""
    try:
        logger.info(f'Пользователь {callback.from_user.id} {callback.from_user.username} запросил / запросила пароль '
                    f'от TelegramMaster_Commentator')
        logger.info(callback.from_user.id)  # Проверка ID пользователя
        user = await bot.get_chat_member(chat_id="@master_tg_d", user_id=callback.from_user.id)  # Проверка подписки
        logger.info(f"User Status: {user.status}")

        if user.status in ['member', 'administrator', 'creator']:
            # Проверка наличия записи о покупке в базе данных
            product_name = "TelegramMaster_Commentator"
            result = check_user_payment(callback.from_user.id, product_name)
            if result:
                # Сообщение пользователю
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                await bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=t("payment-commentator", current_date=current_date,
                           password_TelegramMaster_Commentator=TelegramMaster_Commentator.get("price_password")),
                    reply_markup=payment_yookassa_password_commentator_password_keyboard()
                )
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"Пользователь:\n"
                         f"ID {callback.from_user.id},\n"
                         f"Username: @{callback.from_user.username},\n"
                         f"Имя: {callback.from_user.first_name},\n"
                         f"Фамилия: {callback.from_user.last_name},\n"
                         f"Запросил пароль от TelegramMaster_Commentator"
                )
            else:
                await bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=t("subscription-required-commentator")
                )
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"Пользователь:\n"
                         f"ID {callback.from_user.id},\n"
                         f"Username: @{callback.from_user.username},\n"
                         f"Имя: {callback.from_user.first_name},\n"
                         f"Фамилия: {callback.from_user.last_name},\n"
                         f"Запросил пароль от TelegramMaster_Commentator"
                )
        else:
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=t("subscription-required-commentator")
            )
            await bot.send_message(chat_id=ADMIN_CHAT_ID,
                                   text=f"Пользователь:\n"
                                        f"ID {callback.from_user.id},\n"
                                        f"Username: @{callback.from_user.username},\n"
                                        f"Имя: {callback.from_user.first_name},\n"
                                        f"Фамилия: {callback.from_user.last_name},\n"
                                        f"Запросил пароль от TelegramMaster_Commentator"
                                   )
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "get_password")
async def get_password(callback: types.CallbackQuery):
    """Обработчик команды /get_password для получения пароля для пользователя"""
    try:
        logger.info(f'Пользователь {callback.from_user.id} {callback.from_user.username} запросил / запросила пароль '
                    f'от TelegramMaster-PRO')
        logger.info(callback.from_user.id)  # Проверка ID пользователя
        user = await bot.get_chat_member(chat_id="@master_tg_d", user_id=callback.from_user.id)  # Проверка подписки
        logger.info(f"User Status: {user.status}")
        if user.status in ['member', 'administrator', 'creator']:
            result = is_user_in_db(callback.from_user.id)
            if result:
                # Сообщение пользователю
                await bot.send_message(
                    callback.message.chat.id,
                    text=t("payment-pro", current_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                           password_TelegramMaster=TelegramMaster_PRO.get("price_password")),
                    reply_markup=payment_keyboard_password()
                )
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"Пользователь:\n"
                         f"ID {callback.from_user.id},\n"
                         f"Username: @{callback.from_user.username},\n"
                         f"Имя: {callback.from_user.first_name},\n"
                         f"Фамилия: {callback.from_user.last_name},\n"
                         f"Запросил пароль от TelegramMaster-PRO"
                )
            else:
                await bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=t("subscription-required-pro")
                )
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster-PRO")
        else:
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=t("subscription-required-pro")
            )
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                               f"ID {callback.from_user.id},\n"
                                                               f"Username: @{callback.from_user.username},\n"
                                                               f"Имя: {callback.from_user.first_name},\n"
                                                               f"Фамилия: {callback.from_user.last_name},\n"
                                                               f"Запросил пароль от TelegramMaster-PRO")
    except Exception as e:
        logger.exception(e)
