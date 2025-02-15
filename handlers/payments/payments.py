# -*- coding: utf-8 -*-
import datetime  # Дата

from aiogram import types, F
from loguru import logger  # Логирование с помощью loguru

from db.database import connect_db
from db.settings_db import checking_for_presence_in_the_user_database
from handlers.payments.products_goods_services import TelegramMaster, payment_installation, TelegramMaster_Commentator, \
    password_TelegramMaster_Commentator
from handlers.payments.products_goods_services import password_TelegramMaster
from keyboards.payments_keyboards import payment_keyboard, payment_keyboard_password, payment_keyboard_com, \
    payment_yookassa_password_commentator_password_keyboard
from keyboards.payments_keyboards import purchasing_a_program_setup_service
from messages.messages import generate_payment_message, generate_payment_message_commentator
from system.dispatcher import ADMIN_CHAT_ID
from system.dispatcher import bot, dp


@dp.callback_query(F.data == "delivery")
async def buy(callback_query: types.CallbackQuery):
    """Покупка TelegramMaster 2.0"""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    payment_keyboard_key = payment_keyboard()
    payment_mes = ("Купить TelegramMaster 2.0.\n\n"
                   f"Цена на {current_date} — {TelegramMaster} рублей.\n\n"
                   "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                   "@PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)


@dp.callback_query(F.data == "delivery_com")
async def buy_com(callback_query: types.CallbackQuery):
    """Покупка TelegramMaster_Commentator"""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    payment_mes = ("Купить TelegramMaster_Commentator.\n\n"
                   f"Цена на {current_date} — {TelegramMaster_Commentator} рублей.\n\n"
                   "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                   "@PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_com())


@dp.callback_query(F.data == "purchasing_a_program_setup_service")
async def buy_program_setup_service(callback_query: types.CallbackQuery):
    """Оплата услуг по установке ПО"""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    payment_keyboard_key = purchasing_a_program_setup_service()
    payment_mes = ("Оплатите услуги по настройке и консультации.\n\n"
                   f"Цена на {current_date} — {payment_installation} рублей.\n\n"
                   "После завершения процесса оплаты, свяжитесь с администратором через личные сообщения, используя "
                   "указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=payment_mes,
                                reply_markup=payment_keyboard_key,
                                disable_web_page_preview=True)


@dp.callback_query(F.data == "commentator_password")
async def get_password_tg_com(callback: types.CallbackQuery):
    """Проверка подписки на канал, бот обязательно должен быть админом, ссылка в виде: @master_tg_d"""
    try:
        logger.info(f'Пользователь {callback.from_user.id} {callback.from_user.username} запросил / запросила пароль '
                    f'от TelegramMaster_Commentator')
        logger.info(callback.from_user.id)  # Проверка ID пользователя
        user = await bot.get_chat_member(chat_id="@master_tg_d", user_id=callback.from_user.id)  # Проверка подписки
        logger.info(f"User Status: {user.status}")

        text = (
            "Для того чтобы воспользоваться всеми возможностями бота 🤖, вам необходимо подписаться на канал "
            "🔗 https://t.me/+uE6L_wey4c43YWEy и купить TelegramMaster_Commentator.\n\n"

            "Это позволит вам получить самую свежую версию TelegramMaster_Commentator и воспользоваться всеми новыми "
            "функциями.\n\n"

            "Если вы ранее уже приобретали TelegramMaster_Commentator, но бот 🤖 не выдаёт пароль, обратитесь к "
            "🔗 @PyAdminRU.")
        if user.status in ['member', 'administrator', 'creator']:
            # Подключение к базе данных
            conn = connect_db()
            cursor = conn.cursor()

            # Проверка наличия записи о покупке в базе данных
            product_name = "TelegramMaster_Commentator"
            cursor.execute(
                'SELECT 1 FROM users_pay WHERE user_id = ? AND product = ?',
                (callback.from_user.id, product_name)
            )
            result = cursor.fetchone()

            if result:

                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                payment_keyboard_key = payment_yookassa_password_commentator_password_keyboard()
                # Сообщение пользователю
                payment_mes = generate_payment_message_commentator(current_date, password_TelegramMaster_Commentator)
                await bot.send_message(callback.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)

                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster_Commentator")
            else:

                await bot.send_message(chat_id=callback.message.chat.id, text=text)  # ID пользователя нет в базе данных
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster_Commentator")
        else:
            await bot.send_message(chat_id=callback.message.chat.id, text=text)  # ID пользователя нет в базе данных
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                               f"ID {callback.from_user.id},\n"
                                                               f"Username: @{callback.from_user.username},\n"
                                                               f"Имя: {callback.from_user.first_name},\n"
                                                               f"Фамилия: {callback.from_user.last_name},\n"
                                                               f"Запросил пароль от TelegramMaster_Commentator")
    except Exception as e:
        logger.exception(e)


@dp.callback_query(F.data == "get_password")
async def get_password(callback: types.CallbackQuery):
    """Обработчик команды /get_password для получения пароля для пользователя"""
    try:
        logger.info(f'Пользователь {callback.from_user.id} {callback.from_user.username} запросил / запросила пароль '
                    f'от TelegramMaster 2.0')
        logger.info(callback.from_user.id)  # Проверка ID пользователя
        user = await bot.get_chat_member(chat_id="@master_tg_d", user_id=callback.from_user.id)  # Проверка подписки
        logger.info(f"User Status: {user.status}")
        if user.status in ['member', 'administrator', 'creator']:
            result = checking_for_presence_in_the_user_database(callback.from_user.id)
            if result:

                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                payment_keyboard_key = payment_keyboard_password()
                # Сообщение пользователю
                payment_mes = generate_payment_message(current_date, password_TelegramMaster)
                await bot.send_message(callback.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)

                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster 2.0")
            else:
                text = (
                    "Для того чтобы воспользоваться всеми возможностями бота 🤖, вам необходимо подписаться на канал "
                    "🔗 https://t.me/+uE6L_wey4c43YWEy и купить TelegramMaster 2.0.\n\n"

                    "Это позволит вам получить самую свежую версию TelegramMaster 2.0 и воспользоваться всеми новыми "
                    "функциями.\n\n"

                    "Если вы ранее уже приобретали TelegramMaster 2.0, но бот 🤖 не выдаёт пароль, обратитесь к "
                    "🔗 @PyAdminRU.")
                await bot.send_message(chat_id=callback.message.chat.id, text=text)  # ID пользователя нет в базе данных
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster 2.0")
        else:
            text = ("Для того чтобы воспользоваться всеми возможностями бота 🤖, вам необходимо подписаться на канал "
                    "🔗 https://t.me/+uE6L_wey4c43YWEy и купить TelegramMaster 2.0.\n\n"

                    "Это позволит вам получить самую свежую версию TelegramMaster 2.0 и воспользоваться всеми новыми "
                    "функциями.\n\n"

                    "Если вы ранее уже приобретали TelegramMaster 2.0, но бот 🤖 не выдаёт пароль, обратитесь к "
                    "🔗 @PyAdminRU.")
            await bot.send_message(chat_id=callback.message.chat.id, text=text)  # ID пользователя нет в базе данных
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                               f"ID {callback.from_user.id},\n"
                                                               f"Username: @{callback.from_user.username},\n"
                                                               f"Имя: {callback.from_user.first_name},\n"
                                                               f"Фамилия: {callback.from_user.last_name},\n"
                                                               f"Запросил пароль от TelegramMaster 2.0")
    except Exception as e:
        logger.exception(e)


def register_program_payments():
    """Регистрируем handlers для бота"""
    dp.message.register(buy)  # Покупка TelegramMaster 2.0
    dp.message.register(buy_com)  # Покупка TelegramMaster_Commentator
    dp.message.register(buy_program_setup_service)  # Оплата настройки и установки ПО
    dp.message.register(get_password)  # Получение пароля
    dp.message.register(get_password_tg_com)  # Получение пароля TelegramMaster_Commentator
