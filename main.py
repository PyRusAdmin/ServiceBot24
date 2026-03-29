# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.group_handlers import router as group_handlers
from handlers.payments.cryptomus_payments.cryptomus_commentator import router as cryptomus_commentator
from handlers.payments.cryptomus_payments.cryptomus_commentator_password import router as cryptomus_commentator_password
from handlers.payments.cryptomus_payments.cryptomus_password import router as cryptomus_password
from handlers.payments.cryptomus_payments.cryptomus_program import router as cryptomus_program
from handlers.payments.cryptomus_payments.cryptomus_search import router as cryptomus_search
from handlers.payments.cryptomus_payments.cryptomus_training import router as cryptomus_training
from handlers.payments.payments import router as payments
from handlers.payments.yookassa_payments.yookassa_commentator import router as yookassa_commentator
from handlers.payments.yookassa_payments.yookassa_commentator_password import router as yookassa_commentator_password
from handlers.payments.yookassa_payments.yookassa_password import router as yookassa_password
from handlers.payments.yookassa_payments.yookassa_program import router as yookassa_program
from handlers.payments.yookassa_payments.yookassa_search import router as yookassa_search
from handlers.payments.yookassa_payments.yookassa_training import router as yookassa_training
from handlers.user.ai_handlers import router as ai_handlers
from handlers.user.fag_handlers import router as fag_handlers
from handlers.user.reference_handlers import router as faq_handler
from handlers.user.sending_log_file import router as sending_log_file
from handlers.user.user_account import router as user_account
from handlers.user.user_handlers import router as user_handlers
from system.dispatcher import dp, bot

logger.add("logs/log.log", rotation="1 MB", compression="zip", level="INFO")  # Логирование программы
logger.add("logs/log_ERROR.log", rotation="1 MB", compression="zip", level="ERROR")  # Логирование программы


async def main() -> None:
    """Запуск бота https://t.me/h24service_bot"""

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

    # Оплата yookassa
    dp.include_router(yookassa_password)  # Покупка пароля TelegramMaster-PRO
    dp.include_router(yookassa_commentator_password)  # Покупка пароля TelegramMaster_Commentator
    dp.include_router(yookassa_commentator)  # Купить TelegramMaster_Commentator
    dp.include_router(yookassa_program)  # Купить TelegramMaster-PRO
    dp.include_router(yookassa_training)  # Оплата настройки ПО

    # Оплата Криптой
    dp.include_router(cryptomus_password)  # Покупка пароля TelegramMaster-PRO
    dp.include_router(cryptomus_commentator_password)  # Покупка пароля TelegramMaster_Commentator
    dp.include_router(cryptomus_program)  # Покупка TelegramMaster-PRO
    dp.include_router(cryptomus_commentator)  # Купить TelegramMaster_Commentator
    dp.include_router(cryptomus_training)  # Покупка 'Помощь в настройке ПО (консультация)'

    # Покупка TelegramMaster_Search_GPT
    dp.include_router(yookassa_search)
    dp.include_router(cryptomus_search)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
