# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from db.settings_db import init_password_tables, init_new_products_tables
from handlers.admin.admin_handlers import router as admin_handlers
from handlers.group_handlers import router as group_handlers
from handlers.payments.cryptomus_payments import router as cryptomus_payments
from handlers.payments.maxmaster_payments import router as maxmaster_payments
from handlers.payments.maxmaster_stars import router as maxmaster_stars
from handlers.payments.payments import router as payments
from handlers.payments.server_rent_payments import router as server_rent_payments
from handlers.payments.server_rent_stars import router as server_rent_stars
from handlers.payments.telegram_stars_payments import router as telegram_stars_payments
from handlers.payments.yookassa_payments import router as yookassa_payments
from handlers.user.ai_handlers import router as ai_handlers
from handlers.user.fag_handlers import router as fag_handlers
from handlers.user.reference_handlers import router as faq_handler
from handlers.user.sending_log_file import router as sending_log_file
from handlers.user.user_account import router as user_account
from handlers.user.user_handlers import router as user_handlers
from system.dispatcher import dp, bot
from system.server_rent_checker import run_periodic_check

logger.add("logs/log.log", rotation="1 MB", compression="zip", level="INFO")  # Логирование программы
logger.add("logs/log_ERROR.log", rotation="1 MB", compression="zip", level="ERROR")  # Логирование программы


async def main() -> None:
    """Запуск бота https://t.me/h24service_bot"""

    # Инициализация таблиц базы данных для паролей
    init_password_tables()
    logger.info("Таблицы базы данных для паролей инициализированы")

    # Инициализация таблиц для MaxMaster и аренды сервера
    init_new_products_tables()
    logger.info("Таблицы базы данных для MaxMaster и аренды сервера инициализированы")

    # Админские команды (рассылка, статистика, справка)
    dp.include_router(admin_handlers)

    # MaxMaster
    dp.include_router(maxmaster_payments)  # Оплата MaxMaster YooKassa
    dp.include_router(maxmaster_stars)  # Оплата MaxMaster Stars

    # Аренда сервера
    dp.include_router(server_rent_payments)  # Аренда сервера YooKassa
    dp.include_router(server_rent_stars)  # Аренда сервера Stars

    # Кабинет пользователя
    dp.include_router(user_account)

    #  ИИ
    dp.include_router(ai_handlers)

    # Работа с группой
    dp.include_router(group_handlers)  # Удаление сообщений о входе/выходе из группы

    # Рабата с пользователем бота
    dp.include_router(user_handlers)  # Пост приветствие пользователей бота
    dp.include_router(fag_handlers)  # Помощь по боту

    dp.include_router(sending_log_file)  # Отправка логов боту

    dp.include_router(faq_handler)  # Регистрация FAQ

    # Меню оплата
    dp.include_router(payments)  # Купить TelegramMaster-PRO, Помощь в настройке ПО, Пароль от TelegramMaster-PRO

    dp.include_router(yookassa_payments)  # Оплата yookassa
    dp.include_router(cryptomus_payments)  # Оплата Криптой

    # Оплата Telegram Stars
    dp.include_router(telegram_stars_payments)  # Оплата звездами всех услуг

    # Запуск периодической проверки аренды сервера (в фоне)
    asyncio.create_task(run_periodic_check(interval_hours=24))
    logger.info("Запущена периодическая проверка аренды сервера (24 часа)")

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
